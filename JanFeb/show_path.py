from PyQt5 import QtCore, QtWidgets
import sys
import strTool
import threading
##########################################
global path
path = ""
startpath = "F:/summerImmunedroid2021/spring2022/lotsOfApp/strava"
##########################################
#ui界面设置
class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
    
        #主窗口参数设置
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(848, 721)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 设置分析按键参数
        self.analyze = QtWidgets.QPushButton(self.centralwidget)
        # Qrect(a,b,c,d):以(a,b)为左上角，给定宽度c和高度d的矩形
        self.analyze.setGeometry(QtCore.QRect(57, 260, 175, 28))
        self.analyze.setObjectName("file")
        self.analyze.setStyleSheet("background-color:rgb(111,180,219)")
        self.analyze.setStyleSheet(
            "QPushButton{background-color:rgb(111,180,219)}"  # 按键背景色
            "QPushButton:hover{color:green}"  # 光标移动到上面后的前景色
            "QPushButton{border-radius:6px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(180,180,180);border: None;}"  # 按下时的样式
        )

        # 设置路径按钮参数
        self.file = QtWidgets.QPushButton(self.centralwidget)
        self.file.setGeometry(QtCore.QRect(57, 200, 175, 28))
        self.file.setObjectName("analyze")
        self.file.setStyleSheet("background-color:rgb(111,180,219)")
        self.file.setStyleSheet(
            "QPushButton{background-color:rgb(111,180,219)}"  # 按键背景色
            "QPushButton:hover{color:green}"  # 光标移动到上面后的前景色
            "QPushButton{border-radius:6px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(180,180,180);border: None;}"  # 按下时的样式
        )

        # 设置显示窗口参数
        self.fileT = QtWidgets.QPushButton(self.centralwidget)
        self.fileT.setGeometry(QtCore.QRect(300, 200, 480, 28))
        self.fileT.setObjectName("file")
        self.fileT.setStyleSheet("background-color:rgb(111,180,219)")
        self.fileT.setStyleSheet(
            "QPushButton{background-color:rgb(111,180,219)}"  # 按键背景色
            "QPushButton:hover{color:green}"  # 光标移动到上面后的前景色
            "QPushButton{border-radius:6px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(180,180,180);border: None;}"  # 按下时的样式
        )


        #主窗口及菜单栏标题栏设置
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 848, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        ################button按钮点击事件回调函数################

        self.file.clicked.connect(self.msg)
        self.analyze.clicked.connect(self.androanalyze)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ImmuneDroid"))
        self.file.setText(_translate("MainWindow", "选择文件"))
        self.fileT.setText(_translate("MainWindow", ""))
        self.analyze.setText(_translate("MainWindow", "开始分析"))

    #########选择图片文件夹#########

    def msg(self,Filepath):
        global path
        path = QtWidgets.QFileDialog.getOpenFileName(None,"选取文件夹",startpath,"All Files (*);;Text Files (*.txt)")  # 起始路径
        # print(m)
        self.fileT.setText(path[0]) #m[0]是包含文件的路径

    #########分析函数入口#########
    def androanalyze(self):
        local_path = ""
        local_path = repr(path[0])
        case = local_path.split("/")
        apk_name = case[-1]
        dir_path = local_path.replace(apk_name,"")
        print("apk_name: " + apk_name)
        print("dir_path: " + dir_path)
        t = threading.Thread(target=strTool.main_analysis,args = (dir_path,apk_name))
        t.setDaemon(True) #不必等待子线程
        t.start()

#########主函数入口 #########

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())






