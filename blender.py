import cv2
import mediapipe as mp
import csv

video_path = '/path/to/input_video.mp4'
csv_path = '/path/to/output_keypoints.csv'

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

cap = cv2.VideoCapture(video_path)

with open(csv_path, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    keypoint_names = [
        "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner", "right_eye",
        "right_eye_outer", "left_ear", "right_ear", "mouth_left", "mouth_right", "left_shoulder",
        "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist", "left_pinky",
        "right_pinky", "left_index", "right_index", "left_thumb", "right_thumb", "left_hip", 
        "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle", "left_heel", 
        "right_heel", "left_foot_index", "right_foot_index"
    ]

    header = ['frame'] + [f'{name}_{coord}' for name in keypoint_names for coord in ('x', 'y', 'z')]
    csv_writer.writerow(header)
    
    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:
            row = [frame_number]
            for lm in results.pose_landmarks.landmark:
                row.extend([lm.x, lm.y, lm.z])
            csv_writer.writerow(row)
        else:
            # If no landmarks detected, write a row with 'None'
            row = [frame_number] + ['None'] * 99
            csv_writer.writerow(row)

        frame_number += 1

cap.release()
pose.close()

print(f"Keypoints have been saved to {csv_path}")

#CODE ON BLENDER

import bpy
import csv

csv_path = '/path/to/output_keypoints.csv'

with open(csv_path, mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    header = next(csv_reader)  # Read the header row

    collection = bpy.data.collections.new('Keypoints')
    bpy.context.scene.collection.children.link(collection)

    empties = {}

    for row in csv_reader:
        frame_number = int(row[0])
        keypoint_data = row[1:]

        for i in range(0, len(keypoint_data), 3):
            keypoint_name = header[i + 1].rsplit('_', 1)[0]  
            x = float(keypoint_data[i]) if keypoint_data[i] != 'None' else None
            y = float(keypoint_data[i + 1]) if keypoint_data[i + 1] != 'None' else None
            z = float(keypoint_data[i + 2]) if keypoint_data[i + 2] != 'None' else None

            if x is not None and y is not None and z is not None:
                if frame_number == 0:
                    bpy.ops.object.empty_add(type='SPHERE', location=(x, y, z))
                    empty = bpy.context.object
                    empty.name = keypoint_name
                    collection.objects.link(empty)
                    empties[keypoint_name] = empty
                else:
                    if keypoint_name in empties:
                        empty = empties[keypoint_name]
                        empty.location = (x, y, z)
                        empty.keyframe_insert(data_path='location', frame=frame_number)

print("Keypoints import complete")

