import numpy as np

def analyze_squat(keypoints):
    print("Analyzing squat...")

    # Example: Check the depth of squats
    for frame_landmarks in keypoints:
        hip_y = frame_landmarks[24][1]  # Hip (left)
        knee_y = frame_landmarks[26][1]  # Knee (left)
        ankle_y = frame_landmarks[28][1]  # Ankle (left)

        if hip_y > knee_y:  # Hip is higher than knee (not deep enough)
            print("Squat depth insufficient in one or more frames.")
            return

    print("Squat depth looks good!")
