# UI界面版的主程序，集成了代码模块的所有功能
# 包括 下载，切分，复原，生成数据集，测试数据集等功能
# 将三大模块 LoadFigure, plitFigure, RecoverFigure 功能集于一体，并贴加了一个UI交互界面

import sys
import os
import re
from PyQt5.QtWidgets import (QWidget, QLabel, QApplication, QDesktopWidget, QPushButton, QRadioButton,
                QMessageBox, QFileDialog, QInputDialog, QProgressDialog, QButtonGroup, QComboBox)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont, QPalette, QColor
from PyQt5.QtCore import Qt
if __package__ is None:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from Package.LoadFigure import loadFigure
    from Package.SplitFigure import splitFigure
    from Package.RecoverFigure import recoverFigure
    from Package.Config import (ROOTDIR, SPLITDIR, RECOVERDIR, FILEDIR, FILEPATH, 
                                    FIGNAME, FILENAME, SPLITSNM, IMAGE_SIZE, RECOVERFILE)
else:
    from ..Package.LoadFigure import loadFigure
    from ..Package.SplitFigure import splitFigure
    from ..Package.RecoverFigure import recoverFigure
    from ..Package.Config import (ROOTDIR, SPLITDIR, RECOVERDIR, FILEDIR, FILEPATH, 
                                    FIGNAME, FILENAME, SPLITSNM, IMAGE_SIZE, RECOVERFILE)

REMATCH = r"^Sample(\d+)$" # 正则匹配
PREDIR = os.path.dirname(__file__) # 当前路径

class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("碎片图像还原")
        self.setFixedSize(1600, 900)
        self.center()
        self.figFile = None
        self.created = False
        self.isCurve = True
        self.isBalance = False
        self.size = SPLITSNM.copy()
        # 生成碎片的按钮
        self.pushButton1 = QPushButton('生成碎片',self)
        self.pushButton1.setGeometry(250, 50, 200, 75)
        self.pushButton1.setStyleSheet('QWidget{background-color:rgb(255,200,200)}')
        self.pushButton1.setFont(QFont('SimHei',16))
        self.pushButton1.clicked.connect(self.createFigs)
        # 还原碎片的按钮
        self.pushButton2 = QPushButton('还原碎片',self)
        self.pushButton2.setFont(QFont('SimHei',16))
        self.pushButton2.setGeometry(1150, 50, 200, 75)
        self.pushButton2.setStyleSheet('QWidget{background-color:rgb(200,255,200)}')
        self.pushButton2.clicked.connect(self.recoverFig)
        # 图像标签列表
        self.splitedFigs = self.initSplitFigs((52, 152))
        self.recoveredFig = self.initRecoverFig((953, 153))
        self.recoveredFig.setAlignment(Qt.AlignCenter)
        # 描述标签，显示“图像来源”
        self.label1 = QLabel(self)
        self.label1.move(100, 800)
        self.label1.setFont(QFont('SimHei',16))
        self.label1.setText("图像来源:")
        # 描述标签，显示选择文件的目录位置 
        self.label2 = QLabel(self)
        self.label2.setGeometry(100, 860, 1200, 30)
        self.label2.setFont(QFont('Roman times',10))
        # 显示“需要联网”
        self.label3 = QLabel(self)
        self.label3.move(400, 785)
        self.label3.setFont(QFont('Roman times',10))
        self.label3.setText("需要联网...")
        # 显示作者信息
        self.label4 = QLabel(self)
        self.label4.move(1150, 790)
        self.label4.setFont(QFont('Roman times',14))
        self.label4.setText("作者：PyJun\n邮箱：py.jun@qq.com")
        # 单选框，选择“网页爬虫”选项
        self.radioButton1 = QRadioButton('网页爬虫', self)
        self.radioButton1.move(250, 780)
        self.radioButton1.setChecked(True)
        self.radioButton1.setFont(QFont('SimHei',12))
        # 单选框，选择“指定文件”选项
        self.radioButton2 = QRadioButton('指定文件', self)
        self.radioButton2.move(250, 820)
        self.radioButton2.setFont(QFont('SimHei',12))
        # 单选框按钮分组1
        self.group1 =  QButtonGroup(self)
        self.group1.addButton(self.radioButton1, 11)
        self.group1.addButton(self.radioButton2, 12)
        self.group1.buttonClicked.connect(self.setFigFile)
        # 按钮， 打开文件对话框选择文件
        self.pushButton3 = QPushButton('选择文件...', self)
        self.pushButton3.move(400, 820)
        self.pushButton3.setFont(QFont('Roman times',10))
        self.pushButton3.clicked.connect(self.changeFigFile)
        # 按钮， 爬虫批量下载数据集
        self.pushButton4 = QPushButton('下载数据', self)
        self.pushButton4.setGeometry(700, 50, 200, 45)
        self.pushButton4.setFont(QFont('SimHei',14))
        self.pushButton4.setStyleSheet('QWidget{background-color:rgb(200,200,200)}')
        self.pushButton4.clicked.connect(self.downloadFigures)
        # 按钮， 运行数据集计算程序还原图片的准确性
        self.pushButton4 = QPushButton('测试数据', self)
        self.pushButton4.setGeometry(700, 150, 200, 45)
        self.pushButton4.setFont(QFont('SimHei',14))
        self.pushButton4.setStyleSheet('QWidget{background-color:rgb(200,200,255)}')
        self.pushButton4.clicked.connect(self.computeAccuracy)
        # 显示“碎片数目”
        self.label7 = QLabel(self)
        self.label7.move(725, 275)
        self.label7.setFont(QFont('SimHei',18))
        self.label7.setText("切分数目：")
        # 下拉列表，用来选择行数 3, 4, 5
        self.box1 = QComboBox(self)
        self.box1.addItems(("行数:"+str(i) for i in range(2, 4)))
        self.box1.move(735, 350)
        self.box1.setFont(QFont('SimHei',14))
        self.box1.setCurrentIndex(1)
        self.box1.activated[str].connect(self.changeNM)
        # 下拉列表，用来选择列数 3, 4, 5
        self.box2 = QComboBox(self)
        self.box2.addItems(("列数:"+str(i) for i in range(2, 4)))
        self.box2.move(735, 475)
        self.box2.setFont(QFont('SimHei',14))
        self.box2.setCurrentIndex(1)
        self.box2.activated[str].connect(self.changeNM)
        # 显示
        self.show()

    def center(self):
        qr=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def paintEvent(self,event):
        qp=QPainter()
        qp.begin(self)
        self.drawSplitWindow(qp, (50, 150))
        self.drawRecoverWindow(qp, (950, 150))
        qp.end()

    def drawSplitWindow(self, qp, post):
        pen=QPen(Qt.black, 3, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(2):
            qp.drawLine(post[0]+609*i, post[1], post[0]+609*i, post[1]+609)
        for j in range(2):
            qp.drawLine(post[0], post[1]+609*j, post[0]+609, post[1]+609*j)
        width = IMAGE_SIZE[0]//SPLITSNM[0]
        height = IMAGE_SIZE[1]//SPLITSNM[1]
        for i in range(1, SPLITSNM[0]):
            qp.drawLine(post[0]+(width+2)*i, post[1], post[0]+(width+2)*i, post[1]+609)
        for j in range(1, SPLITSNM[1]):
            qp.drawLine(post[0], post[1]+(height+2)*j, post[0]+609, post[1]+(height+2)*j)
    
    def drawRecoverWindow(self, qp, post):
        pen=QPen(Qt.black, 3, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(post[0], post[1], post[0]+605, post[1])
        qp.drawLine(post[0], post[1], post[0], post[1]+605)
        qp.drawLine(post[0]+605, post[1], post[0]+605, post[1]+605)
        qp.drawLine(post[0], post[1]+605, post[0]+605, post[1]+605)

    def initSplitFigs(self, post):
        labelImgs = [[None for j in range(SPLITSNM[0])] for i in range(SPLITSNM[1])]
        for i in range(SPLITSNM[1]):
            for j in range(SPLITSNM[0]):
                fig = QLabel(self)
                fig.setText('?')
                fig.setFont(QFont('Decorative', 28))
                fig.setAlignment(Qt.AlignCenter)
                width = IMAGE_SIZE[0]//SPLITSNM[0]
                height = IMAGE_SIZE[1]//SPLITSNM[1]
                box = (post[0]+j*(width+2), post[1]+i*(height+2), width, height)
                fig.setGeometry(*box)
                fig.show()
                labelImgs[i][j] = fig
        return labelImgs

    def initRecoverFig(self, post):
        fig = QLabel(self)
        fig.setText("?")
        fig.setFont(QFont('Decorative', 68))
        fig.setAlignment(Qt.AlignCenter)
        box = (post[0], post[1], 600, 600)
        fig.setGeometry(*box)
        return fig

    def setFigFile(self):
        if self.group1.checkedId() == 11:
            self.figFile = None
            self.label2.clear()
        else:
            self.figFile = os.path.abspath(os.path.join(PREDIR, FILEPATH).replace('\\', '/'))
            self.label2.setText("文件位置: "+self.figFile)

    def changeNM(self, text):
        if text[0] == '行':
            SPLITSNM[1] = int(text[-1])
        else:
            SPLITSNM[0] = int(text[-1])
        if self.size != SPLITSNM:
            self.size = SPLITSNM.copy()
            self.update()
            for figLst in self.splitedFigs:
                for fig in figLst:
                    fig.deleteLater()
            self.splitedFigs = self.initSplitFigs((52, 152))

    def changeFigFile(self):
        fname, _ = QFileDialog.getOpenFileName(self,'Open file','.')
        if os.path.exists(fname):
            self.radioButton2.setChecked(True)
            self.figFile = fname
            self.label2.setText("文件位置: "+fname)

    def showSplitedFigs(self):
        filenames = [str(i)+".png" for i in range(1,SPLITSNM[0]*SPLITSNM[1]+1)]
        filepaths = [os.path.join(FILEDIR, f) for f in filenames]
        flag = all(os.path.exists(fp) for fp in filepaths)
        for i in range(SPLITSNM[1]):
            for j in range(SPLITSNM[0]):
                self.splitedFigs[i][j].clear()
                if flag:
                    self.splitedFigs[i][j].setPixmap(QPixmap(filepaths[SPLITSNM[0]*i+j]))
                    self.splitedFigs[i][j].setScaledContents(True)
                else:
                    self.splitedFigs[i][j].setText("?")
                    self.splitedFigs[i][j].setFont(QFont('Decorative', 28))
                    self.splitedFigs[i][j].setAlignment(Qt.AlignCenter)

    def showRecoveredFig(self, filepath=None, failure=False):
        self.recoveredFig.clear()
        if failure:
            self.recoveredFig.setText("无法还原")
            self.recoveredFig.setFont(QFont('Decorative', 50))
        elif filepath is None:
            self.recoveredFig.setText("?")
            self.recoveredFig.setFont(QFont('Decorative', 68))
        else:
            self.recoveredFig.setPixmap(QPixmap(filepath))
            self.recoveredFig.setScaledContents(True)

    def createFigs(self):
        if self.figFile and os.path.exists(self.figFile):
            splitFigure(filepath=self.figFile)
        else:
            loadFigure()
            splitFigure()
        self.showSplitedFigs()
        self.showRecoveredFig()
        self.created = True

    def recoverFig(self):
        if self.created:
            is_recoverd = recoverFigure()
            if is_recoverd:
                self.showRecoveredFig(filepath=RECOVERFILE)
            else:
                self.showRecoveredFig(failure=True)
            self.created = False

    def downloadFigures(self):
        num, ok = QInputDialog.getInt(self,'下载数据集','输入要下载的样本数:', 100, 1, 1000)
        if not ok: return
        self.checkDir()
        progress = QProgressDialog(self)
        progress.setFixedSize(500, 150)
        progress.setFont(QFont('SimHei',12))
        progress.setWindowTitle("下载数据集")  
        progress.setLabelText("正在下载......")
        progress.setCancelButtonText("取消")
        progress.setMinimumDuration(3)
        progress.setWindowModality(Qt.WindowModal)
        progress.setRange(0, num)
        for i in range(1, num+1):
            progress.setValue(i-1)
            if progress.wasCanceled():
                QMessageBox.warning(self,"提示","下载中断")
                break
            dirname = os.path.join(SPLITDIR, "Sample"+str(i))
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            loadFigure(dirname, FIGNAME)
        else:
            progress.setValue(num)
            QMessageBox.information(self,"提示","下载完毕")

    def computeAccuracy(self):
        reMatch = re.compile(REMATCH)
        total, succ = 0, 0
        dirList = []
        self.checkDir()
        for fd in os.listdir(SPLITDIR):
            dirname = os.path.join(SPLITDIR, fd)
            if os.path.isdir(dirname) and re.match(reMatch, fd):
                dirList.append(dirname)
        if len(dirList) == 0:
            QMessageBox.warning(self, "提示", "请先下载数据集...")
            return
        progress = QProgressDialog(self)
        progress.setFixedSize(500, 150)
        progress.setFont(QFont('SimHei',12))
        progress.setWindowTitle("测试数据集")  
        progress.setLabelText("正在测试......")
        progress.setCancelButtonText("取消")
        progress.setMinimumDuration(3)
        progress.setWindowModality(Qt.WindowModal)
        progress.setRange(0, len(dirList))
        for i, dirname in enumerate(dirList):
            progress.setValue(i)
            if progress.wasCanceled():
                QMessageBox.warning(self,"提示","计算中断")
                return
            orgfile = os.path.join(dirname, FIGNAME)
            splitFigure(dirname, orgfile)
            filename = "sample"+str(i+1)+".jpg"
            newfile = os.path.join(RECOVERDIR, filename)
            recoverFigure(dirname, newfile)
        progress.setValue(len(dirList))
        QMessageBox.information(self, "测试结果", "已完成碎片拼接测试！")
        os.startfile(RECOVERDIR)

    @staticmethod
    def checkDir():
        if not os.path.exists(ROOTDIR):
            os.mkdir(ROOTDIR)
        if not os.path.exists(SPLITDIR):
            os.mkdir(SPLITDIR)

# main() 函数
def main():
    app = QApplication(sys.argv)
    mainUI = MainUI()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()

