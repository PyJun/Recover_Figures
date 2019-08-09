# 调用 RecoverFigs.exe 来实现图像的复原，
# 这个一个有 c++ 和 opencv 写的高性能的碎片复原可执行文件

import os
import subprocess
import numpy as np
if __package__ == None:
    from Config import (FILEDIR, FILEPATH, RECOVERFILE, EXEPATH, RECOVERDIR)
else:
    from .Config import (FILEDIR , FILEPATH, RECOVERFILE, EXEPATH, RECOVERDIR)

def recoverFigure(file_dir=FILEDIR, recover_file=RECOVERFILE):
    if not os.path.exists(RECOVERDIR):
        os.makedirs(RECOVERDIR)
    cmdstr = "{} {} {}".format(EXEPATH, file_dir, recover_file).replace('\\', '/')
    status, _ = subprocess.getstatusoutput(cmdstr)
    return status == 0

def main():
    print(recoverFigure())

if __name__ == '__main__':
    main()
