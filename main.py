import cv2
import sys
import TrackerCam
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ultralytics import YOLO
from datetime import datetime
import threading

class MyApp(QWidget):
    prjTitle = "Garbage Recycling Project"
    nowFrame = None
    
    def __init__(self):
        super().__init__()

        self.mainLayout = QHBoxLayout()
        self.menuFrame = QFrame()
        self.stack = QStackedWidget()
    
        self.setStyleSheet("background-color: #ffffff;")
        self.initSplitter()
        
        # 메뉴 생성
        self.menuFrame.setLayout(self.initMenuUI())
        
        # 메인 스택 생성        
        self.mainLayout.addWidget(self.splitter)
        self.stack.addWidget(self.initMainWindow())
        self.stack.addWidget(self.initTrackerWindow())
        self.stack.addWidget(self.initPatrolWindow())
        self.stack.addWidget(self.initSettingsWindow())
        self.stack.setCurrentWidget(self.stack.widget(0))

        # 웹캠 화면 설정
        self.trackerCam = TrackerCam.YoloCam()        
        self.timer = QTimer()
        self.trackerCam.setCamSize(1080, 480)  # 해상도를 640x480으로 설정
        self.trackerThread = None

        self.setLayout(self.mainLayout)
        
        self.setWindowTitle(self.prjTitle)
        self.setGeometry(500, 500, 1080, 720)
        self.show()
    
    
    def initSplitter(self):
        self.splitter = QSplitter(Qt.Horizontal)        
        self.splitter.addWidget(self.menuFrame)
        self.splitter.addWidget(self.stack)
        self.splitter.setSizes([0.1 * self.splitter.size().width(), 0.9 * self.splitter.size().width()])
        self.splitter.setHandleWidth(0)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #6E6E6E; border: 2px solid #6E6E6E; }")
                
        
    def initMenuUI(self):
        menuLayout = QVBoxLayout()
        
        mainBtn = QPushButton("Main", self)
        mainBtn.clicked.connect(lambda: self.showNewWindow(0))
        
        trackerBtn = QPushButton("Run Tracker", self)
        trackerBtn.clicked.connect(lambda: self.showNewWindow(1))
        
        patrolBtn = QPushButton("Patrol Gallery", self)
        patrolBtn.clicked.connect(lambda: self.showNewWindow(2))
        
        settingsBtn = QPushButton("Settings", self)
        settingsBtn.clicked.connect(lambda: self.showNewWindow(3))
        
        menuLayout.addWidget(mainBtn)
        menuLayout.addWidget(trackerBtn)
        menuLayout.addWidget(patrolBtn)
        menuLayout.addWidget(settingsBtn)
        
        return menuLayout
    
    
    def initMainWindow(self):
        mainFrame = QFrame()
        mainLayout = QVBoxLayout()
        mainText = QPushButton("Hello", self)
        
        mainLayout.addWidget(mainText)
        mainFrame.setLayout(mainLayout)
        
        return mainFrame
    
    
    def initTrackerWindow(self):
        trackerFrame = QFrame()
        trackerLayout = QVBoxLayout()
        self.wcLabel = QLabel()
        self.wcLabel.setAlignment(Qt.AlignCenter)
        
        trackerLayout.addWidget(self.wcLabel)
        trackerFrame.setLayout(trackerLayout)
        
        return trackerFrame
    
    
    def runTracker(self):
        while self.trackerCam.cap.isOpened():
            ret, frame = self.trackerCam.run()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h,w,c = frame.shape
                qImg = QImage(frame.data, w, h, w*c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                self.wcLabel.setPixmap(pixmap)
            else:
                QMessageBox.about(self, "Error", "Cannot read frame.")
            cv2.waitKey(1)  # This gives some time to process each frame, adjust as necessary
            
    
    def destroyTrackerWindow(self):
        self.trackerCam.cap.release()
        cv2.destroyAllWindows()
    
    
    def initPatrolWindow(self):
        patrolFrame = QFrame()
        patrolLayout = QVBoxLayout()
        
        mainText = QPushButton("Patrol", self)     
        patrolLayout.addWidget(mainText)
        patrolFrame.setLayout(patrolLayout)
        
        return patrolFrame
    
    
    def initSettingsWindow(self):
        settingsFrame = QFrame()
        settingsLayout = QVBoxLayout()
        
        mainText = QPushButton("Settings", self)
        settingsLayout.addWidget(mainText)
        settingsFrame.setLayout(settingsLayout)
        
        return settingsFrame
    

    def showNewWindow(self, index):
        if self.stack.currentIndex() == index:
            return
        # 웹캠 화면에서 다른 화면으로 전환할 경우 웹캠 종료
        elif self.stack.currentIndex() == 1:
            self.timer.stop()
            self.trackerCam.cap.release()
            cv2.destroyAllWindows()
            print("DESTROY WINDOWS!!!!!")
            if self.trackerThread is not None:
                self.trackerThread.join()  # Wait for the thread to finish
            
        self.stack.setCurrentIndex(index)
        
        if index == 1:
            self.trackerCam.cap = cv2.VideoCapture(0)
            self.timer.start(100)   # update webcam frame every 0.1 seconds
            if self.trackerThread is None or not self.trackerThread.is_alive():
                self.trackerThread = threading.Thread(target=self.runTracker)
                self.trackerThread.start()

    
    
    def closeEvent(self, event):
        result = QMessageBox.question(self, self.prjTitle, "Are you sure to Quit?")
        
        if result == QMessageBox.Yes:
            if self.trackerThread is not None:
                self.trackerThread.join()  # Wait for the thread to finish
            event.accept()
        else:
            event.ignore()

    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myApp = MyApp()
    sys.exit(app.exec_())
