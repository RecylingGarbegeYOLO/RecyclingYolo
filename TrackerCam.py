import os
import torch
import datetime
import numpy as np
from ultralytics import YOLO
import cv2


class TrashCan:
    def __init__(self, x1, y1, x2, y2, label, color):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.label = label
        self.area = ((self.x2 - self.x1) * (self.y2 - self.y1))
        self.color = color
        
    def draw(self, frame):
        cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), self.color, 3)
        cv2.putText(frame, self.label, (self.x1, self.y1 - 5), cv2.FONT_HERSHEY_PLAIN, 1, self.color, 2)
        

class YoloCam:
    colors = [(0, 149, 255), (0, 199, 86), (219, 235, 0), (255, 0, 0), (255, 0, 149), (187, 0, 255)]
    
    def __init__(self, win_width=1280, win_height=720):
        self.win_width = win_width
        self.win_height = win_height
        self.model = YOLO("./Runs-Garbage/runs/detect/train/weights/best.pt")
        self.names = self.model.names       # ['Battery', 'Can', 'Glass', 'Paper', 'Plastic', 'Vinyl']
        self.cap = None

        self.CONFIDENCE_THRESHOLD = 0.4
        self.CONFIDENCE_OVERLAP = 0.4

        # Trash can area
        batteryBin = TrashCan(
            int(self.win_width * 0.06),
            int(self.win_height * 0.4),
            int(self.win_width * 0.13),
            int(self.win_height * 0.7),
            self.names[0],
            self.colors[0]
        )
        
        canBin = TrashCan(
            int(self.win_width * 0.13),
            int(self.win_height * 0.4),
            int(self.win_width * 0.2),
            int(self.win_height * 0.7),
            self.names[1],
            self.colors[1]
        )
        
        glassBin = TrashCan(
            int(self.win_width * 0.2),
            int(self.win_height * 0.4),
            int(self.win_width * 0.3),
            int(self.win_height * 0.7),
            self.names[2],
            self.colors[2]
        )
        
        paperBin = TrashCan(
            int(self.win_width * 0.2),
            int(self.win_height * 0.3),
            int(self.win_width * 0.4),
            int(self.win_height * 0.7),
            self.names[3],
            self.colors[3]
        )
        
        plasticBin = TrashCan(
            int(self.win_width * 0.3),
            int(self.win_height * 0.4),
            int(self.win_width * 0.4),
            int(self.win_height * 0.7),
            self.names[4],
            self.colors[4]
        )
        
        vinylBin = TrashCan(
            int(self.win_width * 0.4),
            int(self.win_height * 0.4),
            int(self.win_width * 0.5),
            int(self.win_height * 0.7),
            self.names[5],
            self.colors[5]
        )
        
        self.binCam1 = [batteryBin, canBin, glassBin, plasticBin, vinylBin]
        self.binCam2 = [paperBin]
        

    def use_result(self, results, camNum):
        nowTime = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        cv2.putText(self.frame, nowTime,
                        (50, 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)
        if results and results[0]:
            bboxes = np.array(results[0].boxes.xyxy.cpu(), dtype="int")
            classes = np.array(results[0].boxes.cls.cpu(), dtype="int")
            confidences = np.array(results[0].boxes.conf.cpu(), dtype="float")
                     
            for cls, bbox, confidence in zip(classes, bboxes, confidences):
                # draw now time
                if confidence < self.CONFIDENCE_THRESHOLD:
                    continue
                
                (x1, y1, x2, y2) = bbox
                label = f"{self.names[cls]}: {confidence:.2f}"
                
                overlaps = []
                if (camNum == 1):
                    for bin in self.binCam1:
                        overlaps.append(self.calOverlap(bbox, bin))
                elif(camNum == 2):
                    for bin in self.binCam2:
                        overlaps.append(self.calOverlap(bbox, bin))
                
                maxOverlap = max(overlaps)
                    
                 # 일정 겹침 정도 이상이라면
                if maxOverlap >= self.CONFIDENCE_OVERLAP:
                    if(overlaps.index(maxOverlap) == cls):
                        cv2.rectangle(self.frame, (x1, y1), (x2, y2), self.colors[cls], 2)
                        cv2.putText(self.frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_PLAIN, 2, self.colors[cls], 2)
                    # wrong classification
                    else:
                        cv2.rectangle(self.frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(self.frame, label+" is not "+self.names[overlaps.index(maxOverlap)], (x1, y1 - 5), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                        # 디렉토리 존재 여부 확인 및 생성
                        patrol_dir = "./patrol"
                        if not os.path.exists(patrol_dir):
                            os.makedirs(patrol_dir)
                        
                        image_path = f"{patrol_dir}/{nowTime}_{self.names[cls]}.jpeg"
                        cv2.imwrite(image_path, self.frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                        print(f"Image saved at: {image_path}")
                else:
                    cv2.rectangle(self.frame, (x1, y1), (x2, y2), self.colors[cls], 2)
                    cv2.putText(self.frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_PLAIN, 2, self.colors[cls], 2)
            
    
    def calOverlap(self, bbox, trashCan):
        (x1, y1, x2, y2) = bbox
        overlab_x1 = max(trashCan.x1, x1)
        overlab_x2 = min(trashCan.x2, x2)
        overlab_y1 = max(trashCan.y1, y1)
        overlab_y2 = min(trashCan.y2, y2)
        
        if overlab_x2 > overlab_x1 and overlab_y2 > overlab_y1:
            overlab_area = (overlab_x2 - overlab_x1) * (overlab_y2 - overlab_y1)
            object_area = (x2 - x1) * (y2 - y1)
            overlab_percent = overlab_area / object_area
            return overlab_percent
        else:
            return 0
                    


    def run(self, camNum):
        ret, frame = self.cap.read()        
        self.frame = frame
        results = self.model(self.frame)
        
        if(camNum==1):
            for bin in self.binCam1:
                bin.draw(self.frame)
                
        if(camNum==2):
            for bin in self.binCam2:
                bin.draw(self.frame)
        
        self.use_result(results, camNum)
        key = cv2.waitKey(1)
        return ret, self.frame


    def setCamSize(self, width, height):
        self.win_width = width
        self.win_height = height
