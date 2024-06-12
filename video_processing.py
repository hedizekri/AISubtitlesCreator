import os
import ffmpeg
import whisper

# Function to download video
def get_local_video_file_path(filepath):
    """
    Validates the presence of a local video file and returns its file path if it exists.
    """
    if os.path.isfile(filepath):
        print(f"File found: {filepath}")
        return os.path.abspath(filepath)
    else:
        raise FileNotFoundError(f"No file exists at: {filepath}")

# Function to extract audio from video and create temporary audio file
def extract_audio(videofilename):
    audiofilename = videofilename.replace(".mp4", ".mp3")
    ffmpeg.input(videofilename).output(audiofilename).overwrite_output().run()
    print(f"Extracted audio to {audiofilename}")
    return audiofilename

# Function to delete the temporary audio file
def delete_temp_audio_file(audiofilename):
    if os.path.exists(audiofilename):
        os.remove(audiofilename)
        print(f"Deleted temporary file: {audiofilename}")
    else:
        print(f"File not found: {audiofilename}")

# Function to transcribe audio file and create a list of dicts with temporal characteristics for each word
def transcribe_audio(audiofilename):
    model = whisper.load_model("medium")
    result = model.transcribe(audiofilename, word_timestamps=True)

    wordlevel_info = []
    for each in result['segments']:
        words = each['words']
        for word in words:
            wordlevel_info.append({'word': word['word'].strip(), 'probability': word['probability'], 'start': word['start'], 'end': word['end']})

    # Merge French words with (')
    new_wordlevel_info = []
    i = 0
    while i < (len(wordlevel_info)):
        if i != (len(wordlevel_info)-1) and wordlevel_info[i+1]['word'][0] == "'":
            new_word = wordlevel_info[i]['word'] + wordlevel_info[i+1]['word']
            new_probability = (wordlevel_info[i]['probability'] + wordlevel_info[i+1]['probability']) / 2
            new_start = wordlevel_info[i]['start']
            new_end = wordlevel_info[i+1]['end']
            new_wordlevel_info.append({'word': new_word.strip(), 'probability': new_probability, 'start': new_start, 'end': new_end})
            i += 2
        else:
            new_wordlevel_info.append(wordlevel_info[i])
            i += 1

    return new_wordlevel_info