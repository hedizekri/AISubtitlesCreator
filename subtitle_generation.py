import json
import os
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip, ColorClip
from datetime import datetime

# Function to store word-level timestamps into a JSON file
def store_wordlevel_info(wordlevel_info, json_filename='data.json'):
    with open(json_filename, 'w') as f:
        json.dump(wordlevel_info, f, indent=4)
    print(f"Stored word-level info to {json_filename}")


# Function to read the modified word-level info from a JSON file
def read_wordlevel_info(json_filename='data.json'):
    with open(json_filename, 'r') as f:
        wordlevel_info_modified = json.load(f)
    print(f"Read word-level info from {json_filename}")
    return wordlevel_info_modified


# Function to delete the JSON file
def delete_json_file(json_filename='data.json'):
    if os.path.exists(json_filename):
        os.remove(json_filename)
        print(f"Deleted JSON file: {json_filename}")
    else:
        print(f"File not found: {json_filename}")


# Function to split text into lines
def split_text_into_lines(data):
    MaxChars = 20
    #maxduration in seconds
    MaxDuration = 1.3
    #Split if nothing is spoken (gap) for these many seconds
    MaxGap = 1.5

    subtitles = []
    line = []
    line_duration = 0
    line_chars = 0


    for idx,word_data in enumerate(data):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        line.append(word_data)
        line_duration += end - start
        
        temp = " ".join(item["word"] for item in line)
        

        # Check if adding a new word exceeds the maximum character count or duration
        new_line_chars = len(temp)

        duration_exceeded = line_duration > MaxDuration 
        chars_exceeded = new_line_chars > MaxChars 
        if idx>0:
          gap = word_data['start'] - data[idx-1]['end'] 
          # print (word,start,end,gap)
          maxgap_exceeded = gap > MaxGap
        else:
          maxgap_exceeded = False
        

        if duration_exceeded or chars_exceeded or maxgap_exceeded:
            if line:
                subtitle_line = {
                    "word": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "textcontents": line
                }
                subtitles.append(subtitle_line)
                line = []
                line_duration = 0
                line_chars = 0


    if line:
        subtitle_line = {   
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line
        }
        subtitles.append(subtitle_line)

    return subtitles
     

# Function to create captions for one line of text
def create_caption(textJSON, framesize, platform, text_position, font="Montserrat-ExtraBold", color='white', bgcolor='blue', bg_opacity=0.5):
    """
    Create captions for one line of text.

    Args:
    textJSON (dict): JSON containing the text and timing information.
    framesize (tuple): Size of the video frame as (width, height).
    font (str): Font to be used for the text.
    color (str): Color of the text.
    bgcolor (str): Background color of the text.
    bg_opacity (float): Opacity of the background.
    text_position (str): Position of the text on the frame ('high', 'middle', 'low').

    Returns:
    list: List of TextClip and ColorClip objects representing the caption.
    """

    platform_margins = {
        'tiktok': 0.20,
        'youtube': 0.35,
        'facebook': 0.22,
        'instagram': 0.22
    }

    if platform.lower() not in platform_margins:
        raise ValueError("Invalid platform name. Must be 'Tiktok', 'Youtube', 'Facebook', or 'Instagram'")

    wordcount = len(textJSON['textcontents'])
    full_duration = textJSON['end'] - textJSON['start']

    word_clips = []
    xy_textclips_positions = []

    frame_width, frame_height = framesize
    fontsize = frame_height * 0.05

    x_margin = frame_width * 1 / 10
    y_margin = frame_height * platform_margins[platform.lower()]

    # Calculate total width of the line
    total_width = sum(TextClip(word['word'], font=font, fontsize=fontsize, color=color).size[0] for word in textJSON['textcontents']) + \
                  (len(textJSON['textcontents']) - 1) * TextClip(" ", font=font, fontsize=fontsize, color=color).size[0]

    lines = [[]]
    line_widths = [0]

    if total_width > frame_width - 2 * x_margin:
        # Split text into multiple lines if the total width exceeds frame width
        current_line = 0
        current_line_width = 0

        for wordJSON in textJSON['textcontents']:
            word_clip = TextClip(wordJSON['word'], font=font, fontsize=fontsize, color=color)
            word_width, word_height = word_clip.size

            if current_line_width + word_width + (TextClip(" ", font=font, fontsize=fontsize, color=color).size[0] if len(lines[current_line]) > 0 else 0) > frame_width - 2 * x_margin:
                current_line += 1
                lines.append([])
                line_widths.append(0)
                current_line_width = 0

            lines[current_line].append(wordJSON)
            current_line_width += word_width + (TextClip(" ", font=font, fontsize=fontsize, color=color).size[0] if len(lines[current_line]) > 0 else 0)
            line_widths[current_line] = current_line_width

    else:
        lines[0] = textJSON['textcontents']
        line_widths[0] = total_width

    # Calculate y_position based on text_position
    total_text_height = len(lines) * fontsize
    if text_position == 'top':
        y_pos = frame_height * 1 / 10
    elif text_position == 'middle':
        y_pos = (frame_height - total_text_height) / 2
    elif text_position == 'bottom':
        y_pos = frame_height - y_margin - total_text_height
    else:
        raise ValueError("text_position must be 'high', 'middle', or 'low'")

    for line_idx, line in enumerate(lines):
        line_width = line_widths[line_idx]
        x_start_pos = (frame_width - line_width) / 2
        x_pos = x_start_pos

        for index, wordJSON in enumerate(line):
            duration = wordJSON['end'] - wordJSON['start']
            word_clip = TextClip(wordJSON['word'], font=font, fontsize=fontsize, color=color).set_start(textJSON['start']).set_duration(full_duration)
            word_clip_space = TextClip(" ", font=font, fontsize=fontsize, color=color).set_start(textJSON['start']).set_duration(full_duration)

            word_width, word_height = word_clip.size
            space_width, space_height = word_clip_space.size
            current_word_width = word_width + (space_width if index < len(line) - 1 else 0)

            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos": x_pos,
                "y_pos": y_pos,
                "width": word_width,
                "height": word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            # Create transparent background
            bg_clip_merged = ColorClip(size=(current_word_width, word_height), color=(0, 0, 0), ismask=False).set_opacity(bg_opacity).set_position((x_pos, y_pos)).set_duration(full_duration).set_start(textJSON['start'])
            word_clip = word_clip.set_position((x_pos, y_pos))
            word_clip_space = word_clip_space.set_position((x_pos + word_width, y_pos))

            x_pos += current_word_width

            word_clips.append(bg_clip_merged)
            word_clips.append(word_clip)
            word_clips.append(word_clip_space)

        y_pos += word_height + 5  # Move to the next line

    for highlight_word in xy_textclips_positions:
        word_clip_highlight = TextClip(highlight_word['word'], font=font, fontsize=fontsize, color=color, bg_color=bgcolor).set_start(highlight_word['start']).set_duration(highlight_word['duration'])
        word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
        word_clips.append(word_clip_highlight)

    return word_clips


# Function to create the final video
def create_final_video(videopath, linelevel_subtitles, platform, text_position, output_dir="output"):
    # Load the input video
    input_video = VideoFileClip(videopath)
    videofilename = os.path.basename(videopath)
    
    frame_size = input_video.size

    all_linelevel_splits = []

    for line in linelevel_subtitles:
        out = create_caption(line, frame_size, platform, text_position)
        all_linelevel_splits.extend(out)
    
    # Overlay the subtitles to the original video.
    final_video = CompositeVideoClip([input_video] + all_linelevel_splits)

    # Set the audio of the final video to be the same as the input video
    final_video = final_video.set_audio(input_video.audio)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create a unique output filename using the current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output_filename = f"subtitled_{os.path.splitext(videofilename)[0]}_{timestamp}.mp4"
    output_filepath = os.path.join(output_dir, base_output_filename)

    # Save the final clip as a video file with the audio included
    final_video.write_videofile(output_filepath, fps=24, codec="libx264", audio_codec="aac")
    print(f"Video saved as {output_filepath}")