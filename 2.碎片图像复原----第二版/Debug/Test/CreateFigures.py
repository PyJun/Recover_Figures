# 批量下载测试数据

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Package.LoadFigure import loadFigure
from Package.SplitFigure import splitFigure
from Package.Config import SPLITDIR

DIRNAME = "Sample"
FILENAME = "cat.jpg"
NUM = 30

# 将测试数据集下载到 SPLITDIR 目录下， 数据集文件夹命名为 Sample1, Sample2, ..., SampleN
# 每个数据集下包含一张 cat.jpg 和 若干张随机切分后的碎片图像
def createFigures(num = NUM, skip = True, download=True):
    for i in range(1, num+1):
        dirname = os.path.join(SPLITDIR, DIRNAME+str(i))
        print("正在生成数据集 {} ......".format(dirname))
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        elif skip:
            continue
        if download:
            loadFigure(dirname, FILENAME)
        figfile = os.path.join(dirname, FILENAME)
        splitFigure(dirname, figfile, isCurve=False)
    print("成功生成 {} 个数据集！".format(num))

def main():
    createFigures(NUM, skip=False, download=False)

if __name__ == '__main__':
    main()
