import torch
import numpy as np
from ultralytics import YOLO
import cv2

"""
1. THRESHOLD 조정
2. TrashCan 테스트 이미지 가져오기, 테스트 이미지에 맞춰서 쓰레기통 도형 쓰레기 종류마다 생성
3. 해당 객체 bb에 경고 메세지? 띄우기
3-1. 제대로 버릴 경우 bb에 엄지척 메세지 띄우기?
4. 마우스 클릭으로 쓰레기통 설정하는 기능..
5. 쓰레기 잘못 버렸을 경우 해당 화면 캡처 후 Gallery에 보관(이후 제대로 버렸을 시 해당 객체 삭제)
6. WebCam 화면에 현재 시간 표시
7. 
"""




class YoloCam:
    def __init__(self):
        self.winWidth = 1280
        self.winHeight = 720
        self.model = YOLO("./Runs-Garbage/runs/detect/train/weights/best.pt")
        self.names = self.model.names             # model classes(labels)
        self.cap = None

        self.CONFIDENCE_THRESHOLD = 0.0
        self.CONFIDENCE_OVERLAP = 0.6

        self.custumBbox = None
        self.drawing = False
        self.start_point = None

        # overlab
        self.overlabX1 = 0
        self.overlabY1 = 0
        self.overlabX2 = 0
        self.overlabY2 = 0
        self.overlabArea = 0
        self.overlabPercent = 0.0

        # set trashcan area (bb)
        self.trashcanX1 = int(self.winWidth*0.1) # left
        self.trashcanY1 = int(self.winHeight*0.1) # top
        self.trashcanX2 = int(self.winWidth*0.5) # right
        self.trashcanY2 = int(self.winHeight*0.5) # bottom
        self.trashcanXY = (self.trashcanX1, self.trashcanY1)
        self.trashcanXY2 = (self.trashcanX2, self.trashcanY2)
        self.trashcanArea = (self.trashcanX2-self.trashcanX1)*(self.trashcanY2-self.trashcanY1)

        self.title = "garbage recycle"
        
        # 쓰레기 종류별 라벨 색깔 지정
        RED = (255, 66, 66)
        ORANGE = (255, 159, 41)
        GREEN = (10, 140, 27)
        BLUE = (0, 0, 255)
        PURPLE = (108, 31, 163)
        PINK = (240, 93, 196)
        self.colors = [RED, ORANGE, GREEN, BLUE, PURPLE, PINK]

        # custom window
        # cv2.namedWindow(self.title)
        # cv2.resizeWindow(self.title, self.winWidth, self.winHeight)
                    
        
    def use_result(self, results):
        
        # if results exist and results[0] is not null
        if (results and results[0]) :
            bboxes = np.array(results[0].boxes.xyxy.cpu(), dtype="int")         # bb xy
            classes = np.array(results[0].boxes.cls.cpu(), dtype="int")         # class index numpy array
            confidence = np.array(results[0].boxes.conf.cpu(), dtype="float")
            pred_box = zip(classes, bboxes, confidence)
            
            for cls, bbox, confidence in pred_box:
                if confidence < self.CONFIDENCE_THRESHOLD: continue
                (x, y, x2, y2) = bbox
                label = f"{self.names[cls]}: {confidence:.2f}"
                
                # calculate overlab area
                overlabX1 = max(self.trashcanX1, x)
                overlabX2 = min(self.trashcanX2, x2)
                overlabY1 = max(self.trashcanY1, y)
                overlabY2 = min(self.trashcanY2, y2)
                
                # if not overlab
                if overlabX2 <= overlabX1 or overlabY2 <= overlabY1:
                    overlabPercent = 0.0
                else:
                    overlabArea = (overlabX2-overlabX1)*(overlabY2-overlabY1)
                    overlabPercent = overlabArea/self.trashcanArea
                    
                    if(overlabPercent < self.CONFIDENCE_OVERLAP):
                        print(f"low overlap: {overlabPercent*100}%")
                        overlabPercent = 0.0
                    
                if(overlabPercent != 0.0):
                    print("bounding box (",x,y,x2,y2,") has class ", cls,
                    " which is ", self.names[cls], " with confidence ", confidence)     # printing detect result
                    print(f"{self.names[cls]} is in Trashcan with Overlap: {overlabPercent*100}% !!!")
                else:
                    print("bounding box (",x,y,x2,y2,") has class ", cls,
                    " which is ", self.names[cls], " with confidence ", confidence)     # printing detect result
                cv2.rectangle(self.frame, (x,y), (x2,y2), (0,0,255), 2)      # bounding box drawing
                cv2.putText(self.frame, label, (x, y-5), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)  # class name  
                    
        return
    
    def run(self):
        # run web cam
        ret, self.frame = self.cap.read()
        results = self.model(self.frame)
        GRAY = (176, 176, 176)
        cv2.rectangle(self.frame, self.trashcanXY, self.trashcanXY2, GRAY, 3)      # trashcan bounding box drawing
        self.use_result(results)
        key = cv2.waitKey(1)
        return ret, self.frame
    
    def setCamSize(self, width, height):
        self.winWidth = width
        self.winWidth = height