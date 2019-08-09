# 对包模块中关键函数功能的测试

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Package.LoadFigure import loadFigure
from Package.SplitFigure import splitFigure
from Package.RecoverFigure import ImgRecover, compareFigure
from Package.Config import FILEPATH, RECOVERDIR, FILENAME

ORIGINFILE = FILEPATH
CREATEDFILE = os.path.join(RECOVERDIR, FILENAME)
ISCURVE = True

def test():
    cnt, tol = 0, 10
    for i in range(tol):
        # loadFigure()
        splitFigure(isCurve=ISCURVE, isBalance=True, shuffle=True)
        imgRecover = ImgRecover()
        print(imgRecover.getAccuOrder(splited=False, isCurve=ISCURVE), end=' ')
        if compareFigure(ORIGINFILE, CREATEDFILE):
            print(True)
            cnt += 1
        else:
            print(False)
            # break
    print("准确率: {:.2%}".format(cnt/tol))

if __name__ == "__main__":
    test()
    # print(compareFigure(ORIGINFILE, CREATEDFILE))
