# 🎥 Automatic Video Subtitles Creator

This project is an automatic video subtitles creator that uses Python to process video files, extract audio, transcribe audio, and generate subtitles according to the social media platform you want to publish on.

## 🚀 Features

- **Alignment Process**: An advanced alignment process to correct speech-to-text (STT) output using the original video script.
- **Subtitle Positioning**: Allows selection of subtitles position based on the uploading platform (YouTube, Facebook, TikTok, Instagram) to ensure the text fits with their HUD.
- **Graphical User Interface (GUI)**: A user-friendly GUI for easy interaction with the tool.

## Acknowledgments

This project is a fork of [Supertranslate.ai](https://github.com/ramsrigouthamg/Supertranslate.ai) by Ramsri Goutham Golla. Explicit permission was obtained from the original author to use, modify, and distribute the code.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Create a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

You can run the application either through the command line or the GUI.

### Command Line

#### Basic Usage
To process a video without a script:
    ```sh
    python main.py --video path/to/your/video.mp4
    ```

#### Full Command

A full example with all options:

    ```sh
    python main.py --video path/to/your/video.mp4 --script "Your optional script here" --platform Youtube --text_position low --output_dir path/to/output/directory
    ```

### GUI 

Simply run the following command to start the GUI:

    ```sh
    python main.py --gui
    ```

## Project Structure

    ```
    my_project/
    │
    ├── LICENSE
    ├── README.md
    ├── main.py
    ├── text_alignment.py
    ├── subtitle_generation.py
    ├── video_processing.py
    ├── gui.py
    ├── requirements.txt
    ├── input/         # Folder for input video files (empty)
    ├── output/        # Folder for output video files (empty)
    └── .gitignore
    ```

## 🤝 Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.