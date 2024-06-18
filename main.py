import torch
import tkinter
import numpy as np
from ultralytics import YOLO
import cv2

# object 인지(분류) --> 추적
# url = 'https://www.youtube.com/watch?v=sD9gTAFDq40'
# video = pafy.new(url)
# best = video.getbest(preftype="mp4")

winWidth = 1280
winHeight = 720
model = YOLO("./Runs-Garbage/runs/detect/train/weights/best.pt")
labels = ['Battery', 'Can', 'Glass', 'Paper', 'Plastic', 'Vinyl']
cap = cv2.VideoCapture(0)       # webcam
names = model.names             # model classes(labels)

CONFIDENCE_THRESHOLD = 0.6
CONFIDENCE_OVERLAP = 0.6
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

custumBbox = None
drawing = False
start_point = None

# overlab
overlabX1 = 0
overlabY1 = 0
overlabX2 = 0
overlabY2 = 0
overlabArea = 0
overlabPercent = 0.0

# set trashcan area (bb)
trashcanX1 = int(winWidth*0.1) # left
trashcanY1 = int(winHeight*0.1) # top
trashcanX2 = int(winWidth*0.5) # right
trashcanY2 = int(winHeight*0.5) # bottom
trashcanXY = (trashcanX1, trashcanY1)
trashcanXY2 = (trashcanX2, trashcanY2)
trashcanArea = (trashcanX2-trashcanX1)*(trashcanY2-trashcanY1)

GRAY = (176, 176, 176)
title = "garbage recycle"

# 쓰레기 종류별 라벨 색깔 지정
RED = (255, 66, 66)
ORANGE = (255, 159, 41)
GREEN = (10, 140, 27)
BLUE = (0, 0, 255)
PURPLE = (108, 31, 163)
PINK = (240, 93, 196)
colors = [RED, ORANGE, GREEN, BLUE, PURPLE, PINK]

# custom window
cv2.namedWindow(title)
cv2.resizeWindow(title, winWidth, winHeight)

def use_result(results):
    
    # if results exist and results[0] is not null
    if (results and results[0]) :
        bboxes = np.array(results[0].boxes.xyxy.cpu(), dtype="int")         # bb xy
        classes = np.array(results[0].boxes.cls.cpu(), dtype="int")         # class index numpy array
        confidence = np.array(results[0].boxes.conf.cpu(), dtype="float")
        pred_box = zip(classes, bboxes, confidence)
        
        for cls, bbox, confidence in pred_box:
            if confidence < CONFIDENCE_THRESHOLD: continue
            (x, y, x2, y2) = bbox
            label = f"{names[cls]}: {confidence:.2f}"
            
            # calculate overlab area
            overlabX1 = max(trashcanX1, x)
            overlabX2 = min(trashcanX2, x2)
            overlabY1 = max(trashcanY1, y)
            overlabY2 = min(trashcanY2, y2)
            
            # if not overlab
            if overlabX2 <= overlabX1 or overlabY2 <= overlabY1:
                overlabPercent = 0.0
            else:
                overlabArea = (overlabX2-overlabX1)*(overlabY2-overlabY1)
                overlabPercent = overlabArea/trashcanArea
                
                if(overlabPercent < CONFIDENCE_OVERLAP):
                    print(f"low overlap: {overlabPercent*100}%")
                    overlabPercent = 0.0
                
            if(overlabPercent != 0.0):
                print("bounding box (",x,y,x2,y2,") has class ", cls,
                  " which is ", names[cls], " with confidence ", confidence)     # printing detect result
                print(f"{names[cls]} is in Trashcan with Overlap: {overlabPercent*100}% !!!")
            else:
                print("bounding box (",x,y,x2,y2,") has class ", cls,
                  " which is ", names[cls], " with confidence ", confidence)     # printing detect result
            cv2.rectangle(frame, (x,y), (x2,y2), (0,0,255), 2)      # bounding box drawing
            cv2.putText(frame, label, (x, y-5), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)  # class name  
                 
    return

# run web cam
while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = model(frame)
    
    cv2.rectangle(frame, trashcanXY, trashcanXY2, GRAY, 3)      # trashcan bounding box drawing
    use_result(results)
    cv2.imshow(title, frame)
    key = cv2.waitKey(1)
    if key == 27:           # ESC
        break
    
cap.release()
cv2.destroyAllWindows()


"""
모델 실행
쓰레기 분류 값 받아오기
쓰레기 트래킹

"""
