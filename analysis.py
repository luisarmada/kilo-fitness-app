from videoprocessor import process_video
from squat import analyze_squat

def main():
    video_path = input("Enter the path to the video: ")
    save_output = input("Do you want to save the output video? (yes/no): ").lower() == "yes"

    # Process the video
    keypoints, output_video_path = process_video(video_path, save_output)

    # Analyze the exercise
    if keypoints:
        analyze_squat(keypoints)
        print(f"Output saved at: {output_video_path}")

if __name__ == "__main__":
    main()
