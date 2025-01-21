import os
import sys
import threading
import pygame
import cv2
from objviewer import main as objviewer_main

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
VIEWER_WIDTH = 800
VIEWER_HEIGHT = 600


def play_video(video_path, surface):
    """Play a video in the right section of the screen."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file {video_path}")
        sys.exit(1)

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart the video
            continue

        # Resize and convert frame for Pygame
        frame = cv2.resize(frame, (SCREEN_WIDTH - VIEWER_WIDTH, VIEWER_HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")

        # Blit the video frame onto the surface
        surface.blit(frame_surface, (VIEWER_WIDTH, 0))
        pygame.display.flip()

    cap.release()


def main(obj_folder):
    """Run the OBJ viewer and video player."""
    # Check for the video file
    video_path = os.path.join(obj_folder, "trackedvideo.mp4")
    if not os.path.isfile(video_path):
        print(f"Error: Video file 'trackedvideo.mp4' not found in {obj_folder}.")
        sys.exit(1)

    # Initialize Pygame for the combined display
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("OBJ Viewer and Video Player")

    # Create a separate surface for the video playback
    video_surface = pygame.Surface((SCREEN_WIDTH - VIEWER_WIDTH, VIEWER_HEIGHT))

    # Run the OBJ viewer in a separate thread
    viewer_thread = threading.Thread(target=objviewer_main, args=(obj_folder,), daemon=True)
    viewer_thread.start()

    # Play the video in the main thread
    play_video(video_path, video_surface)

    pygame.quit()


# Entry point for the program
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <obj_folder>")
        sys.exit(1)

    obj_folder = sys.argv[1]

    if not os.path.isdir(obj_folder):
        print(f"Error: {obj_folder} is not a valid directory.")
        sys.exit(1)

    main(obj_folder)
