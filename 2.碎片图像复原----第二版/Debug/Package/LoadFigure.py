# 爬取 http://placekitten.com/ 网站的小猫图片
# 作为本程序的数据图像的来源

import os
import random
import urllib.request as request
from urllib.error import HTTPError, URLError
from socket import timeout
if __package__ is None:
    from Config import ROOTDIR, SPLITDIR, FILEDIR, FIGNAME
else:
    from .Config import ROOTDIR, SPLITDIR, FILEDIR, FIGNAME


# 从网上下载一张图像以 filename 命名保存在 filedir 目录下
def loadFigure(filedir = FILEDIR, filename = FIGNAME):
    for dirname in (ROOTDIR, SPLITDIR, FILEDIR):
        if not os.path.exists(dirname):
            os.mkdir(dirname)
    width = random.randint(600, 900)
    height = random.randint(600, 900)
    errCnt = 5
    while errCnt > 0:
        try:
            response = request.urlopen('http://placekitten.com/{}/{}'.format(width, height),timeout=5)
            if response.getcode() != 200:
                errCnt -= 1
                continue
                return False
            figure = response.read()
            if figure == b'':
                errCnt -= 1
                continue
            with open(os.path.join(filedir, filename), 'wb') as f:
                f.write(figure);
            return True
        except (HTTPError, timeout, URLError):
            errCnt -= 1
    return False

def main():
    loadFigure()
    
if __name__=='__main__':
    main()
