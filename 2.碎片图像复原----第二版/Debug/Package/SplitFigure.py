# 将图像切成 N*M 张小图片，并随机打乱
# 并将打乱后的碎片存放在指定目录，以 1.png, 2.png, ..., n.png 命名

import os
import math
import random
import numpy as np
from PIL import Image
from PIL.Image import BILINEAR
if __package__ is None:
    from Config import ROOTDIR, SPLITDIR, FILEDIR, FILEPATH, SPLITSNM, IMAGE_SIZE
else:
    from .Config import ROOTDIR, SPLITDIR, FILEDIR, FILEPATH, SPLITSNM, IMAGE_SIZE

class Curve:
    def __init__(self, average, num=7):
        self.A = [random.uniform(4,12)/max(*SPLITSNM) for _ in range(num)]
        self.B = [(2*np.pi*max(*SPLITSNM)*random.uniform(0.32,0.64))/min(IMAGE_SIZE)]
        for _ in range(1, num):
            self.B.append(self.B[-1]+self.B[0])
        self.C = [random.uniform(0, 2*np.pi) for _ in range(num)]
        self.func = lambda x: np.round(sum(A*np.sin(B*x+C) for A,B,C in zip(self.A,self.B,self.C)))+average
        self.W = math.ceil(sum(self.A))

def checkDir(filedir):
    for dirname in (ROOTDIR, SPLITDIR, FILEDIR):
        if not os.path.exists(dirname):
            os.makedir(dirname)
    for file in os.listdir(filedir):
        if file.endswith(".png"):
            os.remove(os.path.join(filedir, file))

def splitAry(imgAry):
    height, width = imgAry.shape[:2]
    unit_w, unit_h = math.ceil(width/SPLITSNM[0]), math.ceil(height/SPLITSNM[1])
    w_curves = [Curve(min(j*unit_w,width)) for j in range(SPLITSNM[0]+1)]
    h_curves = [Curve(min(i*unit_h,height)) for i in range(SPLITSNM[1]+1)]
    subImages = []
    for i in range(SPLITSNM[1]):
        for j in range(SPLITSNM[0]):
            left = max(j*unit_w-w_curves[j].W, 0)
            up = max(i*unit_h-h_curves[i].W, 0)
            right = min((j+1)*unit_w+w_curves[j+1].W, width)
            down = min((i+1)*unit_h+h_curves[i+1].W, height)
            ary = imgAry[up:down,left:right]
            X, Y = np.meshgrid(np.arange(ary.shape[1]), np.arange(ary.shape[0]))
            X = X.reshape((X.shape[0], X.shape[1], 1))
            Y = Y.reshape((Y.shape[0], Y.shape[1], 1))
            if left!=0:
                ary = np.where(X>=w_curves[j].func(Y+up)-left, ary, 1)
            else:
                ary = np.where(X>=w_curves[j].func(Y+up)-left+w_curves[j].W, ary, 1)
            if up!=0:
                ary = np.where(Y>=h_curves[i].func(X+left)-up, ary, 1)
            else:
                ary = np.where(Y>=h_curves[i].func(X+left)-up+h_curves[i].W, ary, 1)
            if right!=width:
                ary = np.where(X<w_curves[j+1].func(Y+up)-left, ary, 1)
            else:
                ary = np.where(X<w_curves[j+1].func(Y+up)-left-w_curves[j+1].W, ary, 1)
            if down!=height:
                ary = np.where(Y<h_curves[i+1].func(X+left)-up, ary, 1)
            else:
                ary = np.where(Y<h_curves[i+1].func(X+left)-up-h_curves[i+1].W, ary, 1)
            interx = IMAGE_SIZE[0]/SPLITSNM[0]
            intery = IMAGE_SIZE[1]/SPLITSNM[1]
            interval = int(2*((interx**2+intery**2)**0.5-min(interx,intery))/2)
            newAry = np.full((down-up+2*interval, right-left+2*interval, 3), 1, dtype='float64')
            newAry[interval:down-up+interval,interval:right-left+interval] = ary
            subImages.append(newAry)
    random.shuffle(subImages)
    return subImages

def splitFigure(filedir=FILEDIR, filepath=FILEPATH):
    checkDir(filedir)
    image = Image.open(filepath)
    image = image.resize(IMAGE_SIZE, resample=BILINEAR)
    imgAry = np.array(image).astype('float')/255
    subImages = splitAry(imgAry)
    for i,subImg in enumerate(subImages, 1):
        theta = random.uniform(0,360)
        img = Image.fromarray((255*subImg).astype('uint8'))
        rotImg = img.rotate(theta, expand=0, resample=BILINEAR, fillcolor=(255,255,255))
        rotImg.save(os.path.join(filedir, "{}.png".format(i)))

# main() 函数，用于该模块的测试
def main():
    splitFigure()

if __name__ == "__main__":
    main()
