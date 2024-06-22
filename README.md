# ♻️ Garbage Recycling Service with YOLOv8
**임베디드시스템 및 IoT로의 활용 1분반 - 7조**    
- 32222443 신지영  
- 32221604 Vasilya  
- 32202970 윤예진
<br><br>

##### Demonstration Video  
[https://youtu.be/FZF8nJuzElo](https://youtu.be/FZF8nJuzElo?si=YLXfh1sURS7wopdC)
<br><br><br>

### 1. Project Overview
Nowadays, separate collection is emphasized in order to properly dispose of and reuse waste generated in everyday life.  
However, there are cases in which separate collection is not carried out properly because it is not properly followed or it is not possible to distinguish which trash can to throw in.  
Therefore, in order to improve this situation, we want to implement a system that uses the **YOLOv8 model** to distinguish the types of garbage and **to inform them to throw the garbage in the right place**.  
<br><br>
### 2. Role Distribution
- **Data Collection and Labeling, PPT Creation:** : 32222443 신지영

- **Model Training and Evaluation, Presentation** : 32221604 Vasilya

- **Program Implementation, Demonstration Video** : 32202970 윤예진  
<br><br>

### 3. Implementation Process
#### 1) Selection of Data Categories
Classification : Total of 6 types (battery, vinyl, can, plastic, glass, paper)  
<br>
#### 2) Data Collection
Collection of approximately 300 images per category followed by labeling   **(Garbage 1, Runs-Garbage Directory)**  
- Open Data References
- https://universe.roboflow.com/king-mongkuts-university-of-technology-north-bangkok-fgqbi/yolo-recycle-trash-detection/dataset/3/images
- https://www.kaggle.com/
<br><br>
#### 3) Model Training
Training the data using the YOLOv8 model   **(1차: output Directory / 2차: Garbage 1, Runs-Garbage Directory)**
<br>
- After the first training, the evaluation of classification performance showed relatively lower performance for specific categories (battery, vinyl).
- Upon discussing the cause of the performance degradation with team members, it was found that for categories like plastic, which have diverse shapes, there was a need to add more datasets for training.
- To improve performance, additional datasets for battery and vinyl were collected and other category datasets were also added for model training.
- After the second training, the evaluation of classification performance showed improvement in the classification of battery and vinyl compared to the first training.  <br><br>
<img width="600" alt="confusion_matrix_normalized" src="https://github.com/RecylingGarbegeYOLO/RecyclingYolo/assets/68535398/715b2582-a8ff-4712-ad47-9a106628bc48">
<br><br>

### 4. Program Introduction
#### 0) Structure
##### Main.py
- Main source code and **UI**
- Consists of 4 screens: Main, Cam 1, Cam 2, Patrol Gallery  
- Possible to move to screen via buttons in the menu  <br><br>

##### TrackerCam.py
- Processing with YOLOv8 model and running the webcam
- Loads the best-performing model (best.pt) from trained YOLOv8 models for object detection
- Classifies detected objects into one of 6 types of trash
- Draws trash bin areas on the webcam screen and configures them according to the webcam view
- Displays bounding boxes to indicate which type of trash an object belongs to
- Calculates the degree of overlap between the trash bin and the detected object to indicate if it was disposed incorrectly
<br><br>

#### 1) Main Screen
Screen that explains each menu of the program with a logo image.  <br><br>
<img width="600" alt="main" src="https://github.com/RecylingGarbegeYOLO/RecyclingYolo/assets/68535398/d7616fe2-f655-40f1-9dad-3ac1a792b02c"><br><br>

#### 2) Cam 1, Cam 2 Screen
Cam 1 (battery, vinyl, can, plastic, glass), Cam 2 (paper) shoots different types of trash bins through a webcam on each cam screen.  
Each trash bin on each screen is defined using Opencv, and recognized trash through the webcam is displayed on the screen using a bounding box.  <br><br>

- Minimum object recognition threshold
  - CONFIDENCE_THRESHOLD = 0.4
- Minimum area overlap for objects
  - CONFIDENCE_OVERLAP = 0.4  

##### Minimum object recognition threshold
Trash objects are displayed on the screen with a bounding box if they meet or exceed the minimum object recognition threshold.  <br><br>

##### Minimum area overlap for objects
After determining the intersection area between the trash object and the trash bin, the overlap ratio is calculated by dividing the area of the trash object by the intersection area.  
If this overlap ratio meets or exceeds the minimum overlap threshold, it is determined that the user has put the trash into the correct bin.  

If the trash is put into the wrong bin (i.e., the type of trash does not match the type of bin), a red bounding box notifies the user that the trash has been improperly sorted.  <br>

<img width="600" alt="cam1" src="https://github.com/RecylingGarbegeYOLO/RecyclingYolo/assets/68535398/0742354c-5b80-4eb6-9038-70d08fdcfd6f"><br><br>
<img width="600" alt="cam2" src="https://github.com/RecylingGarbegeYOLO/RecyclingYolo/assets/68535398/0ca0fca2-2806-40ce-927b-0dc2061103cb"><br><br>


#### 3) Patrol Gallery Screen
If the user improperly sorts the trash into the wrong bin on each camera screen, the webcam captures the screen and saves it to the Patrol Gallery.  
The Patrol Gallery screen allows users to view the saved photos, and clicking on a photo enlarges it for detailed inspection.  <br>
<img width="600" alt="patrol" src="https://github.com/RecylingGarbegeYOLO/RecyclingYolo/assets/68535398/56023bc0-a78c-4277-91d0-d006bef9ebfb"><br><br>


### 5. Results and Demonstration Video
[https://youtu.be/FZF8nJuzElo](https://youtu.be/FZF8nJuzElo?si=YLXfh1sURS7wopdC) <br><br>

### 6. Conclusion and Reflections
After the second round of training, I confirmed an improvement in the model's performance. However, there are noticeable differences in object recognition between Video 1 and Video 2 during the demonstration. Video 1 has a simpler background compared to Video 2, which was recorded in an actual recycling center where the background complexity led to lower object recognition rates. Originally, I attempted to position the webcam as close to the trash bins as possible to minimize the distance between the trash objects and the webcam. Due to the structural constraints of the recycling center, I had to maintain a certain distance between the trash bins and the webcam during the demonstration. This increased distance made the trash objects appear relatively small, making it difficult to distinguish them from the background and thus lowering the object recognition rate.  <br>

Taking these factors into account, I adjusted the CONFIDENCE_THRESHOLD in TrackerCam.py to conduct the recordings. Upon reviewing the Patrol Gallery (patrol directory) where the captured photos are stored after recording, it was evident that some objects were incorrectly detected.  <br>

Throughout the project, I realized that there can be discrepancies between the performance during training and the performance in real-world environments. To address this, it is necessary to further improve the model by adding more datasets and validating it to ensure that objects are recognized regardless of the complexity of the surrounding background.  <br>

With these performance improvements, I anticipate that the system can be deployed in places such as apartment complex recycling centers or school buildings' recycling bins, helping people to correctly separate their waste.  <br>
<br><br>
