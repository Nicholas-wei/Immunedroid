from PyQt5 import QtCore, QtWidgets
import sys
import os
import strTool
import threading
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtCore import QThread, pyqtSignal
import time
##########################################
global path
path = ""
startpath = "F:/summerImmunedroid2021/spring2022/lotsOfApp/strava"
time_in_sec = 0
##########################################
#ui��������

class Thread(QThread):
    _signal = pyqtSignal(int) #�����ź�����Ϊ����
    def __init__(self):
        super(Thread, self).__init__()
    def __del__(self):
        self.wait()
    def run(self):
        for i in range(1,101):
            global time_in_sec
            time.sleep(time_in_sec/100)
            self._signal.emit(i)  #�����ź�


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
    
        #�����ڲ�������
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(848, 721)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # ���÷�����������
        self.analyze = QtWidgets.QPushButton(self.centralwidget)
        # Qrect(a,b,c,d):��(a,b)Ϊ���Ͻǣ��������c�͸߶�d�ľ���
        self.analyze.setGeometry(QtCore.QRect(57, 260, 175, 28))
        self.analyze.setObjectName("file")
        self.analyze.setStyleSheet("background-color:rgb(111,180,219)")
        self.analyze.setStyleSheet(
            "QPushButton{background-color:rgb(111,180,219)}"  # ��������ɫ
            "QPushButton:hover{color:green}"  # ����ƶ���������ǰ��ɫ
            "QPushButton{border-radius:6px}"  # Բ�ǰ뾶
            "QPushButton:pressed{background-color:rgb(180,180,180);border: None;}"  # ����ʱ����ʽ
        )

        # ���ý���������
        self.pbar = QtWidgets.QProgressBar(self.centralwidget)
        self.pbar.setGeometry(200,400,480,28)
        self.pbar.setValue(0)


        # ����·����ť����
        self.file = QtWidgets.QPushButton(self.centralwidget)
        self.file.setGeometry(QtCore.QRect(57, 200, 175, 28))
        self.file.setObjectName("analyze")
        self.file.setStyleSheet("background-color:rgb(111,180,219)")
        self.file.setStyleSheet(
            "QPushButton{background-color:rgb(111,180,219)}"  # ��������ɫ
            "QPushButton:hover{color:green}"  # ����ƶ���������ǰ��ɫ
            "QPushButton{border-radius:6px}"  # Բ�ǰ뾶
            "QPushButton:pressed{background-color:rgb(180,180,180);border: None;}"  # ����ʱ����ʽ
        )

        # ������ʾ���ڲ���
        self.fileT = QtWidgets.QPushButton(self.centralwidget)
        self.fileT.setGeometry(QtCore.QRect(300, 200, 480, 28))
        self.fileT.setObjectName("file")
        self.fileT.setStyleSheet("background-color:rgb(111,180,219)")
        self.fileT.setStyleSheet(
            "QPushButton{background-color:rgb(111,180,219)}"  # ��������ɫ
            "QPushButton:hover{color:green}"  # ����ƶ���������ǰ��ɫ
            "QPushButton{border-radius:6px}"  # Բ�ǰ뾶
            "QPushButton:pressed{background-color:rgb(180,180,180);border: None;}"  # ����ʱ����ʽ
        )


        #�����ڼ��˵�������������
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

        ################button��ť����¼��ص�����################

        self.file.clicked.connect(self.msg)
        self.analyze.clicked.connect(self.androanalyze)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ImmuneDroid"))
        self.file.setText(_translate("MainWindow", "choose"))
        self.fileT.setText(_translate("MainWindow", ""))
        self.analyze.setText(_translate("MainWindow", "start"))

    #########ѡ��ͼƬ�ļ���#########

    def msg(self,Filepath):
        global path
        path = QtWidgets.QFileDialog.getOpenFileName(None,"choose file",startpath,"All Files (*);;Text Files (*.txt)")  # ��ʼ·��
        # print(m)
        self.fileT.setText(path[0]) #m[0]�ǰ����ļ���·��

    #########�����������#########
    def androanalyze(self):
        local_path = ""
        local_path = repr(path[0])
        case = local_path.split("/")
        apk_name = case[-1]
        dir_path = local_path.replace(apk_name,"")
        file_size = os.path.getsize(local_path.replace("'",""))
        print("apk_name: " + apk_name)
        print("dir_path: " + dir_path)
        print("file_size: " + str(file_size))
        global time_in_sec
        time_in_sec = (int)(file_size/15100)
        print("time_in_sec: " + str(time_in_sec))
        t = threading.Thread(target=strTool.main_analysis,args = (dir_path,apk_name))
        t.setDaemon(True) #���صȴ����߳�
        t.start()
        self.fileT.setText("start! please wait!")
        self.thread = Thread()
        self.thread._signal.connect(self.signal_accept)
        self.thread.start() # �����Զ���Thread������run����
    def signal_accept(self,msg):
        self.pbar.setValue(int(msg))
        if self.pbar.value() == 100:
            self.fileT.setText("finish!")

#########��������� #########

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())

