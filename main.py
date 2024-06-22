import os
import sys
import cv2
import TrackerCam
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import threading  # threading 모듈 임포트

class MyApp(QWidget):
    prjTitle = "Garbage Recycling Project"
    nowFrame1 = None
    nowFrame2 = None
    
    pushBtnStyle = "color: #fff; font-weight: bold; font-size:15pt; border:5px solid #fff; border-radius: 8px; border: 5px solid #fff; margin: 1px 5px; background-color: #0000ff;"

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
        self.stack.addWidget(self.initTrackerWindow1())
        self.stack.addWidget(self.initTrackerWindow2())
        self.stack.addWidget(self.initPatrolWindow())
        self.stack.addWidget(self.initSettingsWindow())
        self.stack.setCurrentWidget(self.stack.widget(0))

        # 웹캠 화면 설정
        self.trackerCam1 = TrackerCam.YoloCam()
        self.trackerCam2 = TrackerCam.YoloCam()
        self.timer1 = QTimer()
        self.timer1.timeout.connect(lambda: self.updateFrame(1))
        self.timer2 = QTimer()
        self.timer2.timeout.connect(lambda: self.updateFrame(2))
        self.trackerThread = None

        self.setLayout(self.mainLayout)

        self.setWindowTitle(self.prjTitle)
        self.setGeometry(100, 100, 1920, 1080)
        self.show()

    def initSplitter(self):
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.menuFrame)
        self.splitter.addWidget(self.stack)
        self.splitter.setSizes([int(0.1 * self.splitter.size().width()), int(0.9 * self.splitter.size().width())])
        self.splitter.setHandleWidth(0)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #6E6E6E; border: 2px solid #6E6E6E; }")

    def initMenuUI(self):
        menuLayout = QVBoxLayout()
        menuLayout.setSpacing(10)

        mainBtn = QPushButton("Main", self)
        mainBtn.clicked.connect(lambda: self.showNewWindow(0))
        mainBtn.setStyleSheet(self.pushBtnStyle)

        cam1Btn = QPushButton("Run Cam1", self)
        cam1Btn.clicked.connect(lambda: self.showNewWindow(1))
        cam1Btn.setStyleSheet(self.pushBtnStyle)
        
        cam2Btn = QPushButton("Run Cam2", self)
        cam2Btn.clicked.connect(lambda: self.showNewWindow(2))
        cam2Btn.setStyleSheet(self.pushBtnStyle)

        patrolBtn = QPushButton(" Patrol Gallery ", self)
        patrolBtn.clicked.connect(lambda: self.showNewWindow(3))
        patrolBtn.setStyleSheet(self.pushBtnStyle)

        menuLayout.addWidget(mainBtn)
        menuLayout.addWidget(cam1Btn)
        menuLayout.addWidget(cam2Btn)
        menuLayout.addWidget(patrolBtn)

        return menuLayout

    def initMainWindow(self):
        mainFrame = QFrame()
        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(10)
        
        titleText = QLabel(self)
        titleText.setText("Garbage Recycling Project with YOLOv8")
        titleText.setAlignment(Qt.AlignHCenter)
        titleText.setStyleSheet('color:black; font-size:40pt; font-weight: bold;')
        
        teamText = QLabel(self)
        teamText.setText("Team 7")
        teamText.setAlignment(Qt.AlignRight)
        teamText.setStyleSheet('color:black; font-size:15pt;')
        
        logoImg = QPixmap("./src/logo.png")
        logoLabel = QLabel(self)
        logoLabel.setAlignment(Qt.AlignHCenter)
        logoLabel.setPixmap(logoImg)
        logoLabel.setPixmap(logoImg.scaled(300, 300, Qt.KeepAspectRatio))
    
        menuText = QLabel(self)
        menuText.setText("[ Menu ]")
        menuText.setAlignment(Qt.AlignLeft)
        menuText.setStyleSheet('color:black; font-size:25pt; font-weight: bold;')
        
        guideText = QLabel(self)
        guideText.setText("Cam 1 : Check Battery, Can, Glass, Plastic, Vinyl\n\nCam 2 : Check Paper\n\nPatrol Gallery : You can check who did the wrong recycling!")
        guideText.setAlignment(Qt.AlignLeft)
        guideText.setStyleSheet('color:black; font-size:15pt;')

        mainLayout.addWidget(titleText)
        mainLayout.addWidget(teamText)
        mainLayout.addWidget(logoLabel)
        mainLayout.addWidget(menuText)
        mainLayout.addWidget(guideText)
        mainFrame.setLayout(mainLayout)

        return mainFrame

    def initTrackerWindow1(self):
        trackerFrame = QFrame()
        trackerLayout = QVBoxLayout()
        self.wcLabel1 = QLabel()
        self.wcLabel1.setAlignment(Qt.AlignCenter)
        self.wcLabel1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        trackerLayout.addWidget(self.wcLabel1)
        trackerFrame.setLayout(trackerLayout)

        return trackerFrame
    
    def initTrackerWindow2(self):
        trackerFrame = QFrame()
        trackerLayout = QVBoxLayout()
        self.wcLabel2 = QLabel()
        self.wcLabel2.setAlignment(Qt.AlignCenter)
        self.wcLabel2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        trackerLayout.addWidget(self.wcLabel2)
        trackerFrame.setLayout(trackerLayout)

        return trackerFrame


    # 웹캠 실행
    def runTracker(self, camNum):
        if(camNum == 1):
            while self.trackerCam1.cap.isOpened():
                ret, frame = self.trackerCam1.run(camNum)

                if ret:
                    self.nowFrame1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    self.nowFrame1 = None
                    QMessageBox.about(self, "Error", "Cannot read frame.")
                    break
                cv2.waitKey(1)
        elif(camNum == 2):
            while self.trackerCam2.cap.isOpened():
                ret, frame = self.trackerCam2.run(camNum)

                if ret:
                    self.nowFrame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    self.nowFrame2 = None
                    QMessageBox.about(self, "Error", "Cannot read frame.")
                    break
                cv2.waitKey(1)


    # 웹캠에서 프레임을 읽어와 화면에 표시
    def updateFrame(self, camNum):
        if(camNum==1):
            if self.nowFrame1 is not None:
                h, w, c = self.nowFrame1.shape
                qImg = QImage(self.nowFrame1.data, w, h, w * c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg).scaled(self.wcLabel1.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.wcLabel1.setPixmap(pixmap)
                
        elif(camNum==2):
            if self.nowFrame2 is not None:
                h, w, c = self.nowFrame2.shape
                qImg = QImage(self.nowFrame2.data, w, h, w * c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg).scaled(self.wcLabel2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.wcLabel2.setPixmap(pixmap)

    def initPatrolWindow(self):
        patrolFrame = QFrame()
        patrolLayout = QVBoxLayout() 
        
        # 스크롤 영역
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        patrolLayout.addWidget(scrollArea)
         
        # 그리드 레이아웃 생성 (사진 갤러리)
        gridLayout = QGridLayout()
        gridLayout.setHorizontalSpacing(10)
        gridLayout.setVerticalSpacing(10)

        patrolFrame.setLayout(patrolLayout)
        
        # patrol 폴더 내의 모든 이미지 파일 경로 찾기
        self.folder_path = "./patrol"  # patrol 폴더 경로
        imagePaths = [os.path.join(self.folder_path, file) for file in os.listdir(self.folder_path)
                       if file.lower().endswith('.jpeg')]
        
        for idx, imgPath in enumerate(imagePaths):
            pixmap = QPixmap(imgPath)
            if not pixmap.isNull():
                label = QLabel()
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                label.setPixmap(pixmap)
                label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
                label.mousePressEvent = lambda event, index=idx: self.showImage(index)
                gridLayout.addWidget(label, idx // 5, idx % 5)

        scrollWidget = QWidget()
        scrollWidget.setLayout(gridLayout)
        scrollArea.setWidget(scrollWidget)

        return patrolFrame
    
    # 클릭 시 이미지 확대 표시
    def showImage(self, index):
        imagePath= os.path.join(self.folder_path, os.listdir(self.folder_path)[index])
        pixmap = QPixmap(imagePath)
        if not pixmap.isNull():
            viewerWidget = QWidget()
            viewerLayout = QVBoxLayout()
            
            # 이미지 라벨
            imgLabel = QLabel()
            imgLabel.setAlignment(Qt.AlignCenter)
            imgLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            imgLabel.setPixmap(pixmap)
            
            # 뒤로가기 버튼
            backBtn = QPushButton("Back")
            backBtn.clicked.connect(lambda: self.stack.setCurrentWidget(self.stack.widget(3)))  # 갤러리 화면으로 돌아가기
            backBtn.setStyleSheet(self.pushBtnStyle)
            
            viewerLayout.addWidget(imgLabel)
            viewerLayout.addWidget(backBtn)
            viewerWidget.setLayout(viewerLayout)
            
            self.stack.addWidget(viewerWidget)
            self.stack.setCurrentWidget(viewerWidget)


    # 화면 이동
    def showNewWindow(self, index):
        # 동일 화면인 경우
        if self.stack.currentIndex() == index:
            return
        
        # 현재 웹캠 화면을 사용 중인 경우 정지
        if self.stack.currentIndex() == 1:
            self.timer1.stop()
            self.trackerCam1.cap.release()
            cv2.destroyAllWindows()
            if self.trackerThread is not None:
                self.trackerThread.join()
        elif self.stack.currentIndex() == 2:
            self.timer2.stop()
            self.trackerCam2.cap.release()
            cv2.destroyAllWindows()
            if self.trackerThread is not None:
                self.trackerThread.join()
                
        # 새로운 화면으로 전환
        self.stack.setCurrentIndex(index)

        # Run Cam1 선택 시
        if index == 1:
            if self.trackerThread is None or not self.trackerThread.is_alive():
                self.trackerCam1.cap = cv2.VideoCapture(0)
                self.trackerThread = threading.Thread(target=self.runTracker, args=(1,))
                self.trackerThread.start()
                self.timer1.start(100)
        
        # Run Cam2 선택 시
        elif index == 2:
            if self.trackerThread is None or not self.trackerThread.is_alive():
                self.trackerCam2.cap = cv2.VideoCapture(0)
                self.trackerThread = threading.Thread(target=self.runTracker, args=(2,))
                self.trackerThread.start()
                self.timer2.start(100)

    def initSettingsWindow(self):
        settingsFrame = QFrame()
        settingsLayout = QVBoxLayout()
        settingsText = QLabel("Settings Window", self)

        settingsLayout.addWidget(settingsText)
        settingsFrame.setLayout(settingsLayout)

        return settingsFrame

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
