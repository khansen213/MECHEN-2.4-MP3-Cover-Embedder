# MECHEN 2.4" MP3 Cover Embedder

This tool is designed to embed album covers into the metadata of MP3 files specifically for the 2.4" MECHEN MP3 player. It provides a user-friendly GUI to select MP3 files and cover images, and supports resizing the cover image to fit the device's specific dimensions. Please note that this project has no affiliation with the MECHEN company or its products. All rights and products belong to MECHEN. This program addresses a formatting issue that prevents MP3Tag from embedding cover art correctly for this device.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [FAQ](#faq)
- [Disclaimer](#disclaimer)
- [Sources](#sources)
- [License](#license)

## Features

- Embed album covers into MP3 files' metadata
- User-friendly GUI for easy navigation
- Select MP3 folder and cover image
- Supports resizing cover images to 240x240 pixels
- Save settings and preferences

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/MECHEN-2.4-MP3-Cover-Embedder.git
    ```

2. **Navigate to the Project Directory**:
    ```bash
    cd MECHEN-2.4-MP3-Cover-Embedder
    ```

3. **Install the Required Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Program**:
    ```bash
    python mp3_album_cover_embedder.py
    ```

## Usage

1. **Open the Program**:
    Run the script to open the GUI.

2. **Select the MP3 Folder**:
    Go to `File` > `Change Music Folder` to select the folder containing your MP3 files.

3. **Select a Cover Image**:
    When prompted, choose a cover image to embed into the MP3 files.

4. **Start the Embedding Process**:
    Click `Start Processing` and follow the on-screen instructions to embed the cover image.

5. **Save Settings**:
    Adjust settings such as the embed folder path and auto-save preferences under the `Settings` menu.

## FAQ

**Q1: How do I change the music folder?**
- Go to `File` > `Change Music Folder` to select a new folder.

**Q2: How do I select a cover image?**
- After clicking `Start Processing`, you will be prompted to select a cover image file.

**Q3: Can I resize the cover image?**
- Yes, you can choose to resize the cover image to 240x240 pixels during the embedding process.

**Q4: How do I view detailed instructions?**
- Go to `Help` > `Instructions` for a detailed guide on using the program.

**Q5: What should I do if the program cannot read some files?**
- The program will display a warning with a list of corrupted or unreadable files. You can try using different files or downloading them again.

## Disclaimer

This project is not affiliated with, endorsed by, or connected to the MECHEN company or its products in any way. All rights and products belong to MECHEN. This program is provided as a tool to enable cover art embedding specifically for the MECHEN 2.4" MP3 player, addressing a known issue with MP3Tag's formatting.

## Sources

- **ChatGPT (OpenAI)**: Assisted in developing and debugging the program.
- **Python Documentation**: Reference for the libraries used.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

### Authors

- [Your Name]
- ChatGPT (OpenAI)

For more information or support, please contact mp3.m4r.gitproject@gmail.com.
