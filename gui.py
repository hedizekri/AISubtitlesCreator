import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from video_processing import get_local_video_file_path, extract_audio, delete_temp_audio_file, transcribe_audio
from subtitle_generation import store_wordlevel_info, read_wordlevel_info, delete_json_file, split_text_into_lines, create_final_video
from text_alignment import correct_generated_text_with_script
import time

def select_file(entry):
    filepath = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    if filepath:
        entry.delete(0, ctk.END)
        entry.insert(0, filepath)

def select_output_directory(entry):
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, ctk.END)
        entry.insert(0, directory)

def smooth_progress(progress, start, end, duration, label, step, total_steps):
    increment = (end - start) / (duration * 10)  # Increment per 0.1 second
    for i in range(int(duration * 10)):
        current_value = start + increment * i
        progress['value'] = current_value
        label.configure(text=f"Step {step}/{total_steps}")
        progress.update_idletasks()
        time.sleep(0.1)

def process_video_gui(entry_filepath, entry_script, entry_output_dir, combo_platform, combo_position, progress, label_progress):
    mp4videopath = entry_filepath.get()
    video_script = entry_script.get("1.0", ctk.END).strip()
    output_dir = entry_output_dir.get() if entry_output_dir.get() else "output"
    platform = combo_platform.get()
    text_position = combo_position.get()

    if not mp4videopath:
        messagebox.showerror("Error", "Please select a video file.")
        return

    total_steps = 5
    durations = [3, 1, 1, 15, 15]
    current_step = 0

    try:
        # Step 1
        smooth_progress(progress, 0, 20, durations[current_step], label_progress, current_step + 1, total_steps)
        videofilename = get_local_video_file_path(mp4videopath)

        # Step 2
        current_step += 1
        smooth_progress(progress, 20, 40, durations[current_step], label_progress, current_step + 1, total_steps)
        audiofilename = extract_audio(videofilename)

        # Step 3
        current_step += 1
        smooth_progress(progress, 40, 60, durations[current_step], label_progress, current_step + 1, total_steps)
        wordlevel_info = transcribe_audio(audiofilename)
        wordlevel_info = correct_generated_text_with_script(video_script, wordlevel_info)

        # Step 4
        current_step += 1
        smooth_progress(progress, 60, 80, durations[current_step], label_progress, current_step + 1, total_steps)
        store_wordlevel_info(wordlevel_info)
        wordlevel_info_modified = read_wordlevel_info()
        linelevel_subtitles = split_text_into_lines(wordlevel_info_modified)

        # Step 5
        current_step += 1
        smooth_progress(progress, 80, 100, durations[current_step], label_progress, current_step + 1, total_steps)
        create_final_video(videofilename, linelevel_subtitles, platform, text_position, output_dir)

        # Delete the temporary audio file
        delete_temp_audio_file(audiofilename)

        # Delete the JSON file
        delete_json_file()

        messagebox.showinfo("Success", "Video processing completed!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def run_gui():
    app = ctk.CTk()
    app.title("Automatic Video Subtitles Creator")

    # Create a frame for input and output path entries
    frame_paths = ctk.CTkFrame(app)
    frame_paths.pack(pady=10, padx=10, fill="x")

    # File path entry
    label_filepath = ctk.CTkLabel(frame_paths, text="Video File:")
    label_filepath.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_filepath = ctk.CTkEntry(frame_paths, width=300)
    entry_filepath.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    btn_select_file = ctk.CTkButton(frame_paths, text="Search", command=lambda: select_file(entry_filepath))
    btn_select_file.grid(row=0, column=2, padx=5, pady=5, sticky="w")

    # Output directory entry
    label_output_dir = ctk.CTkLabel(frame_paths, text="Output Directory:")
    label_output_dir.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_output_dir = ctk.CTkEntry(frame_paths, width=300)
    entry_output_dir.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    btn_select_output_dir = ctk.CTkButton(frame_paths, text="Search", command=lambda: select_output_directory(entry_output_dir))
    btn_select_output_dir.grid(row=1, column=2, padx=5, pady=5, sticky="w")

    # Video script entry
    label_script = ctk.CTkLabel(app, text="Video Script (Optional):")
    label_script.pack(pady=5)
    entry_script = ctk.CTkTextbox(app, width=400, height=100)
    entry_script.pack(pady=5)

    # Platform selection
    label_platform = ctk.CTkLabel(app, text="Platform:")
    label_platform.pack(pady=5)
    combo_platform = ctk.CTkComboBox(app, values=["Tiktok", "Youtube", "Facebook", "Instagram"])
    combo_platform.pack(pady=5)
    combo_platform.set("Youtube")

    # Text position selection
    label_position = ctk.CTkLabel(app, text="Text Position:")
    label_position.pack(pady=5)
    combo_position = ctk.CTkComboBox(app, values=["top", "middle", "bottom"])
    combo_position.pack(pady=5)
    combo_position.set("bottom")

    # Progress bar
    label_progress = ctk.CTkLabel(app, text="Progress:")
    label_progress.pack(pady=5)
    progress = ttk.Progressbar(app, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=5)

    # Process button
    btn_process = ctk.CTkButton(app, text="Process Video", command=lambda: process_video_gui(entry_filepath, entry_script, entry_output_dir, combo_platform, combo_position, progress, label_progress))
    btn_process.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    run_gui()