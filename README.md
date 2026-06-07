# 🌌 Nebula Downloader

Nebula Downloader is a high-performance, cross-platform desktop application that allows you to easily download YouTube videos and audio. Featuring a sleek, modern, "deep space" dark-mode user interface powered by CustomTkinter, it supports everything from quick single-file downloads to full playlists, complete with high-quality metadata and thumbnail embedding.

## ✨ Features

- **Sleek Modern UI:** A beautiful dark-themed interface with vibrant purple accents.
- **Built-in Search:** Search YouTube directly from the app or simply paste a URL.
- **Video & Audio Downloads:** 
  - **Video:** Download in Best, 1080p, 720p, or 480p quality.
  - **Audio:** Extract and convert to MP3 with rich bitrates (320kbps, 192kbps, 128kbps).
- **Playlist Support:** Easily batch download entire YouTube playlists.
- **Rich Metadata:** Automatically embeds thumbnails, video titles, and artist tags directly into the downloaded MP4 and MP3 files.
- **Standalone Execution:** No need to mess with paths; pre-compiled releases are bundled directly with FFmpeg.

## 🖥️ Supported Platforms

Nebula Downloader is built with cross-platform compatibility in mind and natively supports:
- **Windows** (10 / 11)
- **macOS** (Intel & Apple Silicon)
- **Linux** (Ubuntu, Debian, Fedora, etc.)

## 🚀 Installation

### Option 1: Pre-compiled Executable (Easiest)
If you don't want to install Python or mess with the command line, simply download the ready-to-use application.

1. Go to the **Releases** page of this repository.
2. Download the version corresponding to your Operating System:
   - `NebulaDownloaderPro-Windows.exe`
   - `NebulaDownloaderPro-macOS`
   - `NebulaDownloaderPro-Linux`
3. Run the application! *(Note: The standalone executables come with FFmpeg pre-bundled, so no extra installations are required).*

### Option 2: Run from Source
If you are a developer or prefer running the raw Python code, follow these steps:

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/Nebula-Downloader.git
cd Nebula-Downloader
```

**2. Install dependencies:**
Make sure you have Python 3.8+ installed.
```bash
pip install -r requirements.txt
```
*(Note: If you don't have a `requirements.txt` yet, simply run: `pip install yt-dlp customtkinter pillow requests`)*

**3. Install FFmpeg (Required for Audio Extraction & Metadata):**
Because running from source doesn't bundle FFmpeg, you will need it installed on your system:
- **Windows:** Download from gyan.dev or install via winget: `winget install ffmpeg`
- **macOS:** Install via Homebrew: `brew install ffmpeg`
- **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install ffmpeg`

**4. Run the app:**
```bash
python main.py
```

## 🛠️ How to Use

1. **Search or Paste:** Enter a YouTube link or a search keyword in the top bar.
2. **Select Media:** If searching, click on the desired video from the resulting list.
3. **Configure Settings:** Choose your download folder, output format (Video/Audio), and desired quality. Toggle the "Batch" switch if you are downloading a full playlist.
4. **Download:** Click **"START DOWNLOAD"** and wait for the magic to happen. Your file explorer will automatically open the folder once completed!

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change. 

## ⚠️ Disclaimer
This tool is intended for educational and personal use only. Please respect YouTube's Terms of Service and only download content for which you own the rights or have explicit permission to download.

---

*Built with ❤️ using Python, CustomTkinter, and yt-dlp.*
