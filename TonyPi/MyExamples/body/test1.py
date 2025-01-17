# test1.py
# V1.0
# Human body detection and tracking
#
#
# Prerequisits: cd .\TonyPi\MyExamples\body\ 
#               Set LAPTOP = True for laptop camera in Camera.py (or Camera_thread.py)
#
# Tested on laptop : 2024-01-06
# Tested on TonyPi : 
#
import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import Camera_thread as Camera

LAPTOP = True       # LAPTOP = True to use laptop camera
#LAPTOP = False     # LAPTOP = False for TonyPi camera

if LAPTOP:
    CAMERA_SETTINGS_PATH = '..\\..\\..\\boot\\camera_setting.yaml'
    CAMERA_ID = 0
else:
    CAMERA_SETTINGS_PATH = '/boot/camera_setting.yaml'
    CAMERA_ID = -1

my_camera = Camera.Camera(CAMERA_ID, CAMERA_SETTINGS_PATH)
my_camera.camera_open()
print("L’image d’origine de l’appareil photo n’a pas été corrigée pour la distorsion")
while True:
    # Il y a un thread qui s'occupe de la capture d'image, donc on peut directement lire l'image
    img = my_camera.frame
    if img is not None:
        cv2.imshow('img', img)
        key = cv2.waitKey(1)
        if key == 27:
            break  

        img_width = img.shape[1]
        img_height = img.shape[0]

        plt.figure(figsize = (10,10))
        plt.axis('off')
        plt.imshow(img[:,:,::-1]);

        # Initialize MediaPipe object.
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils

        # Process Image and Draw Landmarks 
        with mp_pose.Pose(static_image_mode = True) as pose:
                
            # Make a copy of the original image.
            annotated_img = img.copy()
            
            # Process image.
            results = pose.process(img)
            
            # Draw landmarks.
            circle_radius = int(.007*img_height) # Scale landmark circles as percentage of image height.
            
            # Specify landmark drawing style.
            point_spec = mp_drawing.DrawingSpec(color=(220, 100, 0), thickness=-1, circle_radius=circle_radius)
            
            # Draw landmark points.
            mp_drawing.draw_landmarks(annotated_img, 
                                    landmark_list=results.pose_landmarks,   
                                    landmark_drawing_spec=point_spec)
        plt.figure(figsize = (10,10))
        plt.axis('off')
        plt.imshow(annotated_img[:,:,::-1]);

        # Draw Landmark Connections
        # Make a copy of the original image.
        annotated_img = img.copy()

        # Specify landmark connections drawing style.
        line_spec = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
            
        # Draw both landmark points and connections.
        mp_drawing.draw_landmarks(annotated_img, 
                                landmark_list=results.pose_landmarks, 
                                connections=mp_pose.POSE_CONNECTIONS, 
                                landmark_drawing_spec=point_spec,
                                connection_drawing_spec=line_spec)

        plt.figure(figsize = (10,10))
        plt.axis('off')
        plt.imshow(annotated_img[:,:,::-1]);

        # Acquire Landmark Coordinates
        # Acquiring the landmark cordinates is often required for follow-on processing in many applications so 
        # that additional quantities can be computed such as angles and distances.
        if results.pose_landmarks is not None:
            r_hip_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x * img_width)
            r_hip_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y * img_height)

            l_hip_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x * img_width)
            l_hip_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * img_height)

            print('Right hip coordinates : (', r_hip_x,',',r_hip_y,')' )
            print('Left hip coordinates  : (', l_hip_x,',',l_hip_y,')' )

my_camera.camera_close()
cv2.destroyAllWindows()