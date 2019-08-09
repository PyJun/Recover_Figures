# 配置文件， 用来配置程序的参数，比如数据文件位置，图像尺寸等

import os

ROOTDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Data"))  # 数据根目录
SPLITDIR = os.path.join(ROOTDIR, "SplitFigures")  # 切分图像存放的根目录
FILEDIR = os.path.join(ROOTDIR, "SplitFigures/Sample")   # 下载后图像保存的默认目录
FILEPATH = os.path.join(ROOTDIR, "SplitFigures/Sample/cat.jpg")  # 默认完整图像的路径
RECOVERDIR = os.path.join(ROOTDIR, "RecoverFigures")  # 还原后图像存放的根目录
FIGNAME = "cat.jpg"   # 下载后图像的默认名称
FILENAME = "sample.jpg"  # 原图像的名称，用于跟复原后的图像对比

SPLITSNM = [4, 4]  # 分别为竖直切分和水平切分的数目
IMAGE_SIZE = (600, 600)  # 图像的大小
INTERVAL = 10
STEPTIME = 0.3   # 设置图像的还原显示时间间隔
MATCHNUM = 64
ITERNUM = 64  # 算法的迭代次数
