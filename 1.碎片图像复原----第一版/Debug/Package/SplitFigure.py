# 将图像切成 N*M 张小图片，并随机打乱
# 并将打乱后的碎片存放在指定目录，以 1.png, 2.png, ..., n.png 命名

import os
import math
import random
import numpy as np
from PIL import Image
if __package__ is None:
    from Config import ROOTDIR, SPLITDIR, FILEDIR, FILEPATH, SPLITSNM, IMAGE_SIZE, INTERVAL
else:
    from .Config import ROOTDIR, SPLITDIR, FILEDIR, FILEPATH, SPLITSNM, IMAGE_SIZE, INTERVAL


class Curve:
    def __init__(self, average, isCurve=True, isBalace=False, sign=1, seed=None, num=5):
        if isCurve:
            if isBalace:
                random.seed(seed)
            self.A = [random.uniform(2,6) for _ in range(num)]
            self.B = [(2*np.pi*max(*SPLITSNM)*random.uniform(0.16,0.64))/min(IMAGE_SIZE)]
            for _ in range(1, num):
                self.B.append(self.B[-1]+self.B[0])
            self.C = [random.uniform(0, 2*np.pi) for _ in range(num)]
            self.func = lambda x: np.round(sum(sign*A*np.sin(B*x+C) for A,B,C in zip(self.A,self.B,self.C)))+average
            self.W = math.ceil(sum(self.A))
        else:
            self.W = 0
            self.func = lambda x: average

def checkDir(filedir):
    for dirname in (ROOTDIR, SPLITDIR, FILEDIR):
        if not os.path.exists(dirname):
            os.makedir(dirname)
    for file in os.listdir(filedir):
        if file.endswith(".png"):
            os.remove(os.path.join(filedir, file))

def splitFigure(filedir=FILEDIR, filepath=FILEPATH, isCurve=True, isBalance=False, shuffle=True):
    checkDir(filedir)
    image = Image.open(filepath)
    image = image.resize(IMAGE_SIZE)
    imgAry = np.asarray(image).clip(0, 254)
    image = Image.fromarray(imgAry)
    width, height = image.size
    unit_w, unit_h = math.ceil(width/SPLITSNM[0]), math.ceil(height/SPLITSNM[1])
    seed = random.random() if isBalance else None
    w_curves = [Curve(min(j*unit_w,width),isCurve,isBalance,1,seed) for j in range(SPLITSNM[0]+1)]
    h_curves = [Curve(min(i*unit_h,height),isCurve,isBalance,-1,seed) for i in range(SPLITSNM[1]+1)]
    subImages = []
    for i in range(SPLITSNM[1]):
        for j in range(SPLITSNM[0]):
            left = max(j*unit_w-w_curves[j].W, 0)
            up = max(i*unit_h-h_curves[i].W, 0)
            right = min((j+1)*unit_w+w_curves[j+1].W, width)
            down = min((i+1)*unit_h+h_curves[i+1].W, height)
            box = (left, up, right, down)
            img = image.crop(box)
            ary = np.array(img)
            X, Y = np.meshgrid(np.arange(ary.shape[1]), np.arange(ary.shape[0]))
            X = X.reshape((X.shape[0], X.shape[1], 1))
            Y = Y.reshape((Y.shape[0], Y.shape[1], 1))
            if left!=0: 
                ary = np.where(X>=w_curves[j].func(Y+up)-left, ary, 255)
            if up!=0:
                ary = np.where(Y>=h_curves[i].func(X+left)-up, ary, 255)
            if right!=width: 
                ary = np.where(X<w_curves[j+1].func(Y+up)-left, ary, 255)
            if down!=height:
                ary = np.where(Y<h_curves[i+1].func(X+left)-up, ary, 255)
            img = Image.fromarray(ary)
            newImg = Image.new("RGB", (right-left+2*INTERVAL, down-up+2*INTERVAL), (255,255,255))
            newImg.paste(img, (INTERVAL, INTERVAL, INTERVAL+right-left, INTERVAL+down-up))
            subImages.append(newImg)
    if shuffle:
        random.shuffle(subImages)
    for i,subImg in enumerate(subImages, 1):
        subImg.save(os.path.join(filedir, "{}.png".format(i)))
    image.save(filepath)

# main() 函数，用于该模块的测试
def main():
    splitFigure(isCurve=True, shuffle=False)

if __name__ == "__main__":
    main()
