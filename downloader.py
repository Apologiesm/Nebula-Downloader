import yt_dlp
import os
import sys
import shutil
import platform
from typing import Optional, List, Tuple, Dict, Any, Callable

class YouTubeDownloader:
    def __init__(self, progress_callback: Optional[Callable[[float], None]] = None):
        self.progress_callback = progress_callback
        self.ffmpeg_path = self._find_ffmpeg()
        self.cancel_requested = False

    def _find_ffmpeg(self) -> Optional[str]:
        """Locate FFmpeg binary in bundled folder or system PATH."""
        is_windows = platform.system() == "Windows"
        ffmpeg_bin = "ffmpeg.exe" if is_windows else "ffmpeg"
        
        # 1. Check if running as PyInstaller bundle
        if getattr(sys, '_MEIPASS', None):
            bundled_path = os.path.join(sys._MEIPASS, 'ffmpeg', 'bin', ffmpeg_bin)
            if os.path.exists(bundled_path):
                return os.path.dirname(bundled_path)
        
        # 2. Check local project folder
        rel_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', ffmpeg_bin)
        if os.path.exists(rel_path):
            return os.path.dirname(rel_path)

        # 3. Check system PATH
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            return os.path.dirname(system_ffmpeg)
            
        return None

    def _get_ydl_opts(self, base_opts: Dict[str, Any], download_playlist: bool = False) -> Dict[str, Any]:
        """Add FFmpeg location and basic settings to options."""
        opts = base_opts.copy()
        opts['noplaylist'] = not download_playlist
        if self.ffmpeg_path:
            opts['ffmpeg_location'] = self.ffmpeg_path
        return opts

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        if self.cancel_requested:
            raise Exception("Download cancelled by user")
            
        if d['status'] == 'downloading' and self.progress_callback:
            try:
                p = d['_percent_str'].replace('%', '').strip()
                self.progress_callback(float(p))
            except (ValueError, KeyError):
                pass
        elif d['status'] == 'finished' and self.progress_callback:
            self.progress_callback(100.0)

    def get_info(self, url: str) -> Dict[str, Any]:
        """Fetch basic info and available formats for the URL."""
        ydl_opts = self._get_ydl_opts({})
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'formats': info.get('formats', []),
                'webpage_url': info.get('webpage_url')
            }

    def search_youtube(self, query: str, max_results: int = 5) -> List[Tuple[str, str, str]]:
        """Search YouTube for a query and return a list of (title, url, thumbnail) tuples."""
        try:
            ydl_opts = self._get_ydl_opts({})
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{max_results}:{query}"
                result = ydl.extract_info(search_query, download=False)
                
                if 'entries' in result:
                    return [(entry.get('title', 'Unknown Title'), 
                             entry.get('webpage_url'), 
                             entry.get('thumbnail')) 
                            for entry in result['entries'] if entry]
                return []
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def download_video(self, url: str, quality: str = 'best', output_path: str = '.') -> None:
        """Download video with specified quality and embed thumbnail."""
        if self.ffmpeg_path:
            format_map = {
                'Best': 'bestvideo+bestaudio/best',
                'best': 'bestvideo+bestaudio/best',
                '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            }
        else:
            format_map = {
                'Best': 'best',
                'best': 'best',
                '1080p': 'best[height<=1080]',
                '720p': 'best[height<=720]',
                '480p': 'best[height<=480]',
            }
        
        selected_format = format_map.get(quality, 'best')

        ydl_opts = self._get_ydl_opts({
            'format': selected_format,
            'progress_hooks': [self._progress_hook],
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'writethumbnail': True,
            'postprocessors': [
                {
                    # 1. Force WebP thumbnails into JPG format so MP4s can embed them
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg',
                },
                {
                    # 2. Add video metadata (Title, Author) FIRST
                    'key': 'FFmpegMetadata', 
                },
                {
                    # 3. Embed the thumbnail LAST
                    'key': 'EmbedThumbnail',
                }
            ],
        }, download_playlist=False)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_audio(self, url: str, quality: str = 'high', output_path: str = '.') -> None:
        """Download audio and convert to MP3 with specified bitrate, embed thumbnail, and metadata."""
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg is not found. Audio extraction to MP3 requires FFmpeg.")

        bitrate_map = {
            'High (320kbps)': '320',
            'Medium (192kbps)': '192',
            'Low (128kbps)': '128',
            'high': '320',
            'medium': '192',
            'low': '128',
        }
        
        selected_bitrate = bitrate_map.get(quality, '192')

        ydl_opts = self._get_ydl_opts({
            'format': 'bestaudio/best',
            'progress_hooks': [self._progress_hook],
            'writethumbnail': True,
            'postprocessors': [
                {
                    # 1. Extract the audio to MP3
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': selected_bitrate,
                },
                {
                    # 2. Convert WebP thumbnails to JPG so MP3 files accept them
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg',
                },
                {
                    # 3. Embed Title/Artist data BEFORE the thumbnail
                    'key': 'FFmpegMetadata',
                },
                {
                    # 4. Embed the Cover Art LAST
                    'key': 'EmbedThumbnail',
                },
            ],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        }, download_playlist=False)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_playlist(self, url: str, mode: str, quality: str, output_path: str = '.') -> None:
        """Download an entire playlist."""
        ydl_opts = self._get_ydl_opts({}, download_playlist=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' not in info:
                raise RuntimeError("The provided URL is not a playlist.")
            
            entries = list(info['entries'])
            total_items = len(entries)

            for index, entry in enumerate(entries, 1):
                if self.cancel_requested:
                    raise Exception("Playlist download cancelled by user")
                
                video_url = entry.get('webpage_url')
                title = entry.get('title', 'Unknown Title')
                
                if self.progress_callback:
                    self.progress_callback(f"Item {index}/{total_items}: {title[:30]}...")

                if mode == "Video":
                    self.download_video(video_url, quality, output_path)
                else:
                    self.download_audio(video_url, quality, output_path)