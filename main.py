from text_alignment import correct_generated_text_with_script
from subtitle_generation import (
    store_wordlevel_info,
    read_wordlevel_info,
    delete_json_file,
    split_text_into_lines,
    create_final_video
)
from video_processing import (
    get_local_video_file_path,
    extract_audio,
    delete_temp_audio_file,
    transcribe_audio
)
from gui import run_gui
import argparse

def main():
    parser = argparse.ArgumentParser(description="Automatic Video Subtitles Creator")
    parser.add_argument('--gui', action='store_true', help="Launch the graphical interface")
    parser.add_argument('--video', type=str, help="Path to the video file")
    parser.add_argument('--script', type=str, help="Video script (optional)")
    parser.add_argument('--platform', type=str, choices=["Tiktok", "Youtube", "Facebook", "Instagram"], default="Youtube", help="Platform")
    parser.add_argument('--text_position', type=str, choices=["top", "middle", "bottow"], default="low", help="Text position")
    parser.add_argument('--output_dir', type=str, help="Output directory (optional)")

    args = parser.parse_args()

    if args.gui:
        run_gui()
    else:
        if not args.video:
            parser.error("the following arguments are required: --video")

        mp4videopath = args.video
        video_script = args.script if args.script else ""
        platform = args.platform
        text_position = args.text_position
        output_dir = args.output_dir if args.output_dir else "output"

        videofilename = get_local_video_file_path(mp4videopath)
        audiofilename = extract_audio(videofilename)
        wordlevel_info = transcribe_audio(audiofilename)
        wordlevel_info = correct_generated_text_with_script(video_script, wordlevel_info)

        store_wordlevel_info(wordlevel_info)
        wordlevel_info_modified = read_wordlevel_info()
        linelevel_subtitles = split_text_into_lines(wordlevel_info_modified)
        create_final_video(videofilename, linelevel_subtitles, platform, text_position, output_dir)

        # Delete the temporary audio file
        delete_temp_audio_file(audiofilename)

        # Delete the JSON file
        delete_json_file()

if __name__ == "__main__":
    main()