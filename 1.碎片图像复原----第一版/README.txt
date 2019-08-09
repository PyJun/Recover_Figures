程序介绍:
    程序功能分三部分，数据图像下载，随机切分碎片，碎片拼接还原
    程序代码的目录如下:
    --Debug
        --Main
            MainUI.py
        --Package
            Config.py
            LoadFigure.py
            SplitFigure.py
            RecoverFigure.py
        --Test
            CreateFigures.py
            ComputeAccuracy.py
            Test.py
        __main__.py
    --Release
        MainUi.exe

    Debug 目录下为开发版，需要配置 python3 开发环境，同时需要安装一些第三方模块，
        可以在终端使用 pip install -r Debug/requirements.txt 安装程序所需的第三方模块
        完成后，在终端使用 python -m Debug 即可运行 MainUI.py UI界面主程序

    Release 目录下为发行版，在 Win7或Win10 64位下无需配置任何环境，
            双击 MainUI.exe 打开就可以运行 UI 界面程序

    注意: 可能出现程序的UI界面过大，本机显示屏无法完全显示，若出现这种情况，
        可以调节本机电脑的分辨率 至 1680*1050 以上，在笔者电脑的分辨率为 1920*1080，
        能够正常显示程序界面，至于怎么调电脑的分辨率，可以自行百度。