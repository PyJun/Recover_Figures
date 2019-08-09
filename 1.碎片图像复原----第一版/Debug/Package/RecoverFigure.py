# 将多张碎片图进行边缘匹配， 拼接复原图像
# 核心算法: ImageRecover 类中的 _jointImg() 方法

import os
import queue
import random
import numpy as np
from PIL import Image
from sklearn.preprocessing import scale as scale
if __package__ == None:
    from Config import (ROOTDIR, RECOVERDIR, FILEDIR, FILENAME, IMAGE_SIZE, 
                            ITERNUM, STEPTIME, INTERVAL, MATCHNUM)
else:
    from .Config import (ROOTDIR, RECOVERDIR, FILEDIR, FILENAME, IMAGE_SIZE, ITERNUM,
                            STEPTIME, INTERVAL, MATCHNUM)


# 比较二个图像文件是否相同，若相同，则放回 True
def compareFigure(file1, file2):
    aryImg1 = np.array(Image.open(file1).convert('L'))
    aryImg2 = np.array(Image.open(file2).convert('L'))
    return np.all(aryImg1==aryImg2)


class Img:
    def __init__(self, image, imgId): # imgage 为 Image 的对象，表示碎片图像
        self.id = imgId  # 碎片图像的 id, 比如该碎片来自 1.png, 这 id 为 1
        self.size = image.size # 碎片图像的尺寸， (宽，高) 二元组
        self.post = [None, None] # 碎片图像拼接后的绝对位置，初始化为空
        self.x = self.y = None  # 碎屏图像拼接后的相对位置， 初始化为空
        self.aroundImg = {dire:None for dire in "LURD"} # 表示其四周上下左右紧邻的Img, 初始化为空
        self.initVec(image); # 初始化边缘形状和像素向量

    # 通过 imgage 来初始化四个边缘向量，并将边缘向量标准化
    def initVec(self, image):
        self.aroundVec = {dire:{'shapeVec':None, 'pixelVec':None} for dire in "LURD"}
        imgAry = np.array(image).astype(np.int)  # 提取图像矩阵 
        size = imgAry.shape
        boolAry = (imgAry==255)
        # left shapeVec and pixelVec
        self.aroundVec['L']['shapeVec'] = shapeVec = np.argmin(boolAry, axis=1)
        self.aroundVec['L']['pixelVec'] = pixVec = imgAry[np.arange(size[0]), shapeVec]
        self.aroundVec['L']['vec'] = scale(pixVec[INTERVAL:size[0]-INTERVAL].astype(np.float64))
        # up shapeVec and pixelVec
        self.aroundVec['U']['shapeVec'] = shapeVec = np.argmin(boolAry, axis=0)
        self.aroundVec['U']['pixelVec'] = pixVec = imgAry[shapeVec, np.arange(size[1])]
        self.aroundVec['U']['vec'] = scale(pixVec[INTERVAL:size[1]-INTERVAL].astype(np.float64))
        # right shapeVec and pixelVec
        self.aroundVec['R']['shapeVec'] = shapeVec = np.argmin(np.fliplr(boolAry), axis=1)
        self.aroundVec['R']['pixelVec'] = pixVec = np.fliplr(imgAry)[np.arange(size[0]), shapeVec]
        self.aroundVec['R']['vec'] = scale(pixVec[INTERVAL:size[0]-INTERVAL].astype(np.float64))
        # down shapeVec and pixelVec
        self.aroundVec['D']['shapeVec'] = shapeVec = np.argmin(np.flipud(boolAry), axis=0)
        self.aroundVec['D']['pixelVec'] = pixVec = np.flipud(imgAry)[shapeVec, np.arange(size[1])]
        self.aroundVec['D']['vec'] = scale(pixVec[INTERVAL:size[1]-INTERVAL].astype(np.float64))
        # 以上四行，分别得到 左，上，右，下，四个边缘形状向量和像素向量

# 定义一个 ImgRecover 类，将分散 Img 类拼接成正确顺序
class ImgRecover:
    def __init__(self, filedir=FILEDIR, newdir=RECOVERDIR): 
        self.newdir = newdir   # filedir 碎片图像目录
        self.filedir = filedir  # newdir 复原图像位置
        self.imgHead = None  # Img 图中的一个头结点，这里特指图中最左上方的Img
        self.imgArray = None # 碎片图像复原后的数组，比如 imgArray[i][j] 表示第i行j列的碎片 Img
        self.shape = None
        self.imgSet = None # 所有碎片 Img 的集合
        self._load_ImgSet() # 加载 imgSet 集合

    # 检查文件目录
    def _checkDir(self):
        if not os.path.exists(ROOTDIR):
            os.mkdir(ROOTDIR)
        if not os.path.exists(self.newdir):
            os.mkdir(self.newdir)

    # 初始化操作，将所有属性清空
    def _init(self):
        self.imgHead = None
        self.imgArray = None
        self.shape = None
        for img in self.imgSet:
            img.aroundImg = {dire:None for dire in "LURD"}
            img.x = img.y = None
            self.post = [None, None]

    # 从碎片图像目录中依次打开碎片图像，贴加到 imgSet 集合中
    def _load_ImgSet(self):
        filelist = os.listdir(self.filedir)
        self.imgSet = set()
        for file in filelist:
            if file.endswith('.png'):
                image = Image.open(os.path.join(self.filedir,file)).convert("L")
                self.imgSet.add(Img(image, int(file.rstrip('.png'))))

    # 核心算法，使用贪心法满足当前欧式距离最小的情况下随机化匹配链接碎片Img, 形成一个无向图
    # 可以通过多次迭代该算法，直到形成一个合理无向图，从而提取出正确的拼接数组 imgArray
    # 贪心法虽然有可能得不到全局最优解，但有因为该算法是随机的，所以每次得到的贪心结果都不同，
    # 只要多次迭代， 在很大的概率下会出现一个正确的最优解，因此只要淘汰那些局部最优解了
    def _jointImg(self, isCurve=True):
        imgNums = len(self.imgSet)
        imgList = list(self.imgSet)
        self.imgHead = imgList[0]
        random.shuffle(imgList)
        if imgNums <= 10:
            imgList.pop()
        else:
            imgList += random.sample(self.imgSet, imgNums//10)
        for img1 in imgList:
            min_diff, match_dires, match_imgs = float('inf'), None, None
            for dire1 in img1.aroundImg:
                if img1.aroundImg[dire1]: continue
                for img2 in self.imgSet:
                    if img1 == img2: continue
                    dire2 = {'L':'R', 'R':'L', 'U':'D', 'D':'U'}[dire1]
                    if img2.aroundImg[dire2]: continue
                    if isCurve:
                        shapeVec1 = img1.aroundVec[dire1]['shapeVec']
                        shapeVec2 = img2.aroundVec[dire2]['shapeVec']
                        if shapeVec1.size != shapeVec2.size:
                            continue
                        shapeVec = shapeVec1+shapeVec2
                        dist = np.argmax(np.bincount(shapeVec))
                        index = (shapeVec==dist)
                        num = np.sum(index)
                        if num < MATCHNUM:
                            continue
                        pixelVec1 = img1.aroundVec[dire1]['pixelVec'].astype(np.float64)
                        pixelVec2 = img2.aroundVec[dire2]['pixelVec'].astype(np.float64)
                        vec1 = scale(pixelVec1[index])
                        vec2 = scale(pixelVec2[index])
                    else:
                        vec1 = img1.aroundVec[dire1]['vec']
                        vec2 = img2.aroundVec[dire2]['vec']
                        if vec1.size != vec2.size:
                            continue
                        num = vec1.size
                    diff = np.sqrt(np.sum(np.square(vec1-vec2))/num)                    
                    if diff < min_diff:
                        min_diff = diff
                        match_dires = (dire1, dire2)
                        match_imgs = (img1, img2)
            if match_imgs:
                match_imgs[0].aroundImg[match_dires[0]] = match_imgs[1]
                match_imgs[1].aroundImg[match_dires[1]] = match_imgs[0]

    # 通过深度优先搜索遍历整张图，从而得到该图的形状，如果该形状非矩形，则为局部最优器，淘汰，返回 False
    def _judgeShape(self):
        self.imgHead.x = self.imgHead.y = 0
        que = queue.Queue()
        imgSet = self.imgSet.copy()
        que.put(self.imgHead)
        imgSet.remove(self.imgHead)
        min_x, min_y = 0, 0
        max_x, max_y = 0, 0
        while not que.empty():
            img = que.get()
            if img.x+img.y < min_x+min_y:
                min_x = img.x
                min_y = img.y
                self.imgHead = img
            if img.x+img.y > max_x+max_y:
                max_x = img.x
                max_y = img.y
            for dire,ardImg in img.aroundImg.items():
                if ardImg:
                    new_x = img.x + {'L':-1, 'R':1, 'U':0, 'D':0}[dire]
                    new_y = img.y + {'U':-1, 'D':1, 'L':0, 'R':0}[dire]
                    if ardImg in imgSet:
                        ardImg.x = new_x
                        ardImg.y = new_y
                        que.put(ardImg)
                        imgSet.remove(ardImg)
                    elif new_x != ardImg.x or new_y != ardImg.y:
                        return False
        self.shape = [max_x-min_x+1, max_y-min_y+1]
        return self.shape[0]*self.shape[1] == len(self.imgSet)

    # 通过深度优先搜索遍历整张图, 定位每个碎片的位置，并填入 imgArray 数组
    # 如果 imgArray 数组未填满，则局部最优，淘汰该解，返回 False
    # 如果 imgArray 全填满，那么还原记录每个img的绝对post，返回 True
    def _fillArray(self):
        self.imgArray = [[None for i in range(self.shape[0])] for j in range(self.shape[1])]
        self.imgHead.x = self.imgHead.y = 0
        que = queue.Queue()
        imgSet = self.imgSet.copy()
        que.put(self.imgHead)
        imgSet.remove(self.imgHead)
        while not que.empty():
            img = que.get()
            try:
                self.imgArray[img.y][img.x] = img
            except IndexError:
                return False
            for dire,ardImg in img.aroundImg.items():
                if ardImg and ardImg in imgSet:
                    ardImg.x = img.x + {'L':-1, 'R':1, 'U':0, 'D':0}[dire]
                    ardImg.y = img.y + {'U':-1, 'D':1, 'L':0, 'R':0}[dire]
                    que.put(ardImg)
                    imgSet.remove(ardImg)
        isFull = all(all(lst) for lst in self.imgArray)
        if isFull:
            post = [0, 0]
            for i,imgLst in enumerate(self.imgArray):
                for j,img in enumerate(imgLst):
                    img.post = post.copy()
                    if j < len(imgLst)-1: 
                        shapeVec1 = self.imgArray[i][j].aroundVec['R']['shapeVec']
                        shapeVec2 = self.imgArray[i][j+1].aroundVec['L']['shapeVec']
                        if shapeVec1.size != shapeVec2.size:
                            print('size...')
                            return False
                        wid = np.argmax(np.bincount(shapeVec1+shapeVec2))
                        post[0] += img.size[0]-wid
                if i < len(self.imgArray)-1:
                    shapeVec1 = self.imgArray[i][0].aroundVec['D']['shapeVec']
                    shapeVec2 = self.imgArray[i+1][0].aroundVec['U']['shapeVec']
                    if shapeVec1.size != shapeVec2.size:
                        print('size...')
                        return False
                    hei = np.argmax(np.bincount(shapeVec1+shapeVec2))
                    post = [0, post[1]+imgLst[0].size[1]-hei]
        return isFull

    # 通过 imgArray 数组和每个碎片 Img 的绝对位置 post, 复原生成一张新图像，
    # 并以 filename 命名 保存在 self.newdir 目录下
    def _recover(self, filename=FILENAME, splited=True, breath=2):
        imgAry = np.zeros((2*IMAGE_SIZE[1], 2*IMAGE_SIZE[0], 3)).astype(np.uint8)
        max_size = [0, 0]
        for i, imgLst in enumerate(self.imgArray, 1):
            for j, img in enumerate(imgLst, 1):
                image = Image.open(os.path.join(self.filedir, str(img.id)+".png"))
                left, up = img.post
                if splited:
                    left += j*breath
                    up += i*breath
                width = img.size[0]-2*INTERVAL
                height = img.size[1]-2*INTERVAL
                right = left + width
                down = up + height
                shapeVecX1 = img.aroundVec['L']['shapeVec'][INTERVAL:INTERVAL+height]
                shapeVecY1 = img.aroundVec['U']['shapeVec'][INTERVAL:INTERVAL+width]
                shapeVecX2 = img.aroundVec['R']['shapeVec'][INTERVAL:INTERVAL+height]
                shapeVecY2 = img.aroundVec['D']['shapeVec'][INTERVAL:INTERVAL+width]
                X, Y = np.meshgrid(np.arange(width), np.arange(height))
                X = X.reshape((X.shape[0], X.shape[1], 1))
                Y = Y.reshape((Y.shape[0], Y.shape[1], 1))
                postXY1 = np.logical_and(X>=shapeVecX1[Y]-INTERVAL, Y>=shapeVecY1[X]-INTERVAL)
                postXY2 = np.logical_and(X<img.size[0]-shapeVecX2[Y]-INTERVAL, 
                                            Y<img.size[1]-shapeVecY2[X]-INTERVAL)
                postXY = np.logical_and(postXY1, postXY2)
                ary = np.array(image)[INTERVAL:INTERVAL+height, INTERVAL:INTERVAL+width]
                tempAry = imgAry[up:down,left:right]
                imgAry[up:down,left:right] = np.where(np.logical_and(postXY,ary!=255), ary, tempAry)
                max_size[0] = max(max_size[0], right)
                max_size[1] = max(max_size[1], down)
        if splited:
            imgAry = imgAry[:max_size[1]+breath, :max_size[0]+breath]
        else:
            imgAry = imgAry[:max_size[1], :max_size[0]]
        newImage = Image.fromarray(imgAry)
        newImage.save(os.path.join(self.newdir, filename))

    # 不断迭代 self._jointImg() 方法，得到全局最优解
    # 返回碎片图像还原后正确的id序列
    # 如果 isRecover 为 True, 同时将调用 self._recover() 保存复原后的图像
    def getAccuOrder(self, filename=FILENAME, isRecover=True, splited=True, isCurve=True):
        if len(self.imgSet) == 0:
            return None
        for _ in range(ITERNUM):  # 循环迭代，最大次数为 ITERNUM
            self._init()  # 每次迭代前，清空属性
            self._jointImg(isCurve)  # 拼接碎片图像，形成一个图
            if self._judgeShape() and self._fillArray(): # 淘汰不合理的图(局部最优解)
                if isRecover:
                    self._checkDir()
                    self._recover(filename, splited)
                # 得到全局最优器，返回碎片图像还原后正确的id序列(先行后列)
                return [self.imgArray[i][j].id for i in range(self.shape[1]) for j in range(self.shape[0])]
        if isRecover:
            self._checkDir()
            newImage = Image.new('RGB', IMAGE_SIZE)            
            newImage.save(os.path.join(self.newdir, filename))
        return None

    # def test(self, filename=FILENAME, isRecover = True):
    #     self._init()  # 每次迭代前，清空属性
    #     self._jointImg()  # 拼接碎片图像，形成一个图
    #     if self._judgeShape() and self._fillArray(): # 淘汰不合理的图(局部最优解)
    #         return [self.imgArray[i][j].id for i in range(self.shape[1]) for j in range(self.shape[0])]
    #     return None

    # def testSome(self, filename=FILENAME, isRecover = True, splited=True, isCurve=True):
    #     cnt = 0
    #     for _ in range(ITERNUM):
    #         cnt += 1
    #         self._init()  # 每次迭代前，清空属性
    #         diff = self._jointImg(isCurve)  # 拼接碎片图像，形成一个图
    #         if self._judgeShape() and self._fillArray(): # 淘汰不合理的图(局部最优解)
    #             if isRecover:
    #                 self._recover(filename, splited)
    #             print("cnt:", cnt)
    #             # self.showPost()
    #             return [self.imgArray[i][j].id for i in range(self.shape[1]) for j in range(self.shape[0])]
    #     return None

# main() 函数，用于该模块的测试
def main():
    imgRecover = ImgRecover()
    print(imgRecover.getAccuOrder(splited=True, isCurve=True))

if __name__ == "__main__":
    main()
