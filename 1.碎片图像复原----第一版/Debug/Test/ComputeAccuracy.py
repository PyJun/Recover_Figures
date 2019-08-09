# 从测试数据集中还原整张图片，并计算算法准确率

import sys
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Package.RecoverFigure import ImgRecover, compareFigure
from Package.Config import SPLITDIR, RECOVERDIR

FILENAME = "sample"
FIGNAME = "cat.jpg"
REMATCH = r"^Sample(\d+)$"
ISCURVE = False

# 对于每个SplitFigures文件夹中碎片数据集 SampleN, 
# 都会在RecoverFigures文件夹下生成一个复原图像sampleN.jpg
# 将所有的复原图像和原图像 cat.jpg 作比较，然后统计正确率
def computeAccuracy(splitDir = SPLITDIR, recoverDir = RECOVERDIR):
    reMatch = re.compile(REMATCH)
    total, succ = 0, 0
    for fd in os.listdir(splitDir):
        dirname = os.path.join(splitDir, fd)
        if os.path.isdir(dirname) and re.match(reMatch, fd):
            print("正在还原数据集 {} ...".format(fd))
            imgRecover = ImgRecover(dirname, recoverDir)
            num = re.search(reMatch, fd).group(1)
            filename = FILENAME+num+".jpg"
            accuOrder = imgRecover.getAccuOrder(filename, splited=False, isCurve=ISCURVE)
            if accuOrder:
                file1 = os.path.join(dirname, FIGNAME)
                file2 = os.path.join(RECOVERDIR, filename)
                succ += compareFigure(file1, file2)
            total += 1
    if total:
        print("准确率: {:.2%}".format(succ/total))
        return succ/total
    return 0

if __name__ == "__main__":
    computeAccuracy()
