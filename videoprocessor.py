import cv2
import mediapipe as mp
import numpy as np

def extract_landmarks(landmarks):
    return np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])

def process_video(video_path, save_output=False):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video.")
        return None, None

    output_path = "demo_out/video_output.mp4"
    out = None
    if save_output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    keypoints = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect pose
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            keypoints.append(extract_landmarks(results.pose_landmarks))

            # Draw landmarks on the frame
            mp.solutions.drawing_utils.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )

        if save_output:
            out.write(frame)

        cv2.imshow("Exercise Analysis", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()
    return keypoints, output_path if save_output else None
