from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import numpy as np
import scipy.io.wavfile as wav
import os
import pandas as pd
from mutagen.flac import FLAC, Picture

def find_audio_start(filename, check_after_ms=0, silence_thresh=-50, chunk_size=10):
    audio = AudioSegment.from_file(filename)
    
    # Trim the audio to start checking after the specified time
    if check_after_ms > 0:
        audio = audio[check_after_ms:]
    
    non_silent_ranges = detect_nonsilent(audio, min_silence_len=chunk_size, silence_thresh=silence_thresh)
    
    if non_silent_ranges:
        # Get the start time of the first non-silent range and add check_after_ms
        start_time = non_silent_ranges[0][0] + check_after_ms
        return start_time
    else:
        return None


def add_metadata(file_path, title, artist, album, cover_image_path):
    audio = FLAC(file_path)
    audio['title'] = title
    audio['artist'] = artist
    audio['album'] = album

    if cover_image_path:
        with open(cover_image_path, 'rb') as f:
            picture_data = f.read()

        picture = Picture()
        picture.data = picture_data
        picture.type = 3  # Cover (front)
        picture.mime = 'image/jpeg'  # or 'image/png' depending on the image type
        audio.add_picture(picture)

    audio.save()

def split_flac(input_file, df, song_durations_ms, output_folder):
    # Load the FLAC file
    audio = AudioSegment.from_file(input_file, format="flac")
    
    # Get the non-silent intervals
    # nonsilent_intervals = detect_nonsilent(audio, min_silence_len=1000, silence_thresh=-40)
    
    # Initialize the start of the first song
    current_start = 0
    current_start = find_audio_start(input_file, current_start)
    for i, duration in enumerate(song_durations_ms):
        current_end = current_start + duration
        
        # Extract the song from current_start to current_end
        song = audio[current_start:current_end]
        
        # Export the song as a new FLAC file
        name = df.iloc[i]['Track']+ " - " + df.iloc[i]['Artist'] +".flac"
        output_file = os.path.join(output_folder, name)
        song.export(output_file, format="flac")
        
        title = df.iloc[i]['Track']
        artist = df.iloc[i]['Artist']
        album = df.iloc[i]['Album']
        cover = "./track_photos/"+title+".jpg"

        add_metadata(output_file, title, artist, album, cover)
        # Update the start for the next song
        current_start = current_end
        print(name + " --- COMPLETED")
        current_start = find_audio_start(input_file, current_start)

        
    print("Splitting complete!")

# Example usage
df = pd.read_csv("./playlist.csv")

input_file = "./test.flac"
# song_durations = [359024, 315380, 412561, 423509, 212459]  # Example durations in seconds
song_durations= df['Duration'].to_list()
print(song_durations)
output_folder = "./songs"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

split_flac(input_file, df, song_durations, output_folder)