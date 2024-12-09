import os
import sys
import subprocess
from pydub import AudioSegment
import eyed3

def convert_video_to_audio(video_path, output_folder):
    try:
        # Extract audio from video file using ffmpeg
        audio_output = os.path.join(output_folder, os.path.basename(video_path).replace('.mp4', '.mp3'))
        subprocess.run(['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_output], check=True)
        return audio_output
    except subprocess.CalledProcessError as e:
        print(f"Error processing video '{video_path}': {e}")
        sys.exit(1)

def create_combined_audio(folder_path, output_folder):
    try:
        # Create a new audio segment from each video
        combined = AudioSegment.empty()
        markers = []
        current_time = 0  # Start time for the combined audio

        for file_name in os.listdir(folder_path):
            if file_name.endswith('.mp4'):
                video_path = os.path.join(folder_path, file_name)
                audio_path = convert_video_to_audio(video_path, output_folder)
                audio = AudioSegment.from_mp3(audio_path)
                combined += audio  # Append the audio
                markers.append(f"Audio from {file_name} starts at {current_time / 1000.0} seconds.")
                current_time += len(audio)  # Update current time with the length of this clip

        # Save the combined audio
        combined_output = os.path.join(output_folder, 'combined_audio.mp3')
        combined.export(combined_output, format='mp3')

        # Add markers to the combined audio metadata (ID3 tags)
        audio_file = eyed3.load(combined_output)
        for idx, marker in enumerate(markers):
            # Add custom tags as comments in the ID3 metadata
            audio_file.tag.comments.set(f"Marker {idx + 1}: {marker}")

        audio_file.tag.save()

        print(f"Combined audio saved to {combined_output}")
        print(f"Markers embedded in the audio metadata.")
        return combined_output, markers

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ask user for the input and output folder paths
    folder_path = input("Enter the path to the folder containing video files: ").strip()
    output_folder = input("Enter the path to the folder to save the audio files: ").strip()

    if not os.path.exists(folder_path):
        print(f"Error: The input folder '{folder_path}' does not exist.")
        sys.exit(1)

    if not os.path.exists(output_folder):
        print(f"Output folder '{output_folder}' does not exist. Creating it...")
        os.makedirs(output_folder)

    create_combined_audio(folder_path, output_folder)
