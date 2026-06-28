"""
Music Scanner — scans directories for audio files and reads metadata.
Uses mutagen for metadata extraction (title, artist, album, duration, album art).
"""
import os
import hashlib
from pathlib import Path
from typing import List, Optional

from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
from mutagen.id3 import ID3

from .models import Song

# Supported audio extensions
AUDIO_EXTENSIONS = {".mp3", ".flac", ".wav", ".ogg", ".m4a", ".wma", ".aac"}

# Minimum duration in ms to include (filters ringtones/notifications)
MIN_DURATION_MS = 30_000


def _generate_id(path: str) -> int:
    """Generate a stable numeric ID from a file path."""
    return int(hashlib.md5(path.encode()).hexdigest()[:8], 16)


def _extract_album_art(audio) -> Optional[bytes]:
    """Try to extract embedded album art from audio metadata."""
    try:
        # MP3 with ID3 tags
        if hasattr(audio, "tags") and audio.tags is not None:
            tags = audio.tags

            # ID3 tags (MP3)
            if isinstance(tags, ID3):
                for key in tags:
                    if key.startswith("APIC"):
                        return tags[key].data

            # MP4 / M4A
            if hasattr(tags, "__contains__") and "covr" in tags:
                covers = tags["covr"]
                if covers:
                    return bytes(covers[0])

        # FLAC
        if isinstance(audio, FLAC) and audio.pictures:
            return audio.pictures[0].data

    except Exception:
        pass
    return None


def _extract_metadata(filepath: str) -> Optional[Song]:
    """Extract metadata from a single audio file, returning a Song or None."""
    try:
        audio = MutagenFile(filepath)
        if audio is None:
            return None

        # Duration
        duration_ms = int((audio.info.length or 0) * 1000)
        if duration_ms < MIN_DURATION_MS:
            return None

        # Try to read tags
        title = Path(filepath).stem  # fallback to filename
        artist = "Unknown Artist"
        album = "Unknown Album"

        if audio.tags is not None:
            tags = audio.tags

            # ID3 (MP3)
            if isinstance(tags, ID3):
                title = str(tags.get("TIT2", title))
                artist = str(tags.get("TPE1", artist))
                album = str(tags.get("TALB", album))
            # FLAC / OGG / Vorbis comments
            elif hasattr(tags, "get"):
                title_list = tags.get("title") or tags.get("TITLE")
                if title_list:
                    title = str(title_list[0]) if isinstance(title_list, list) else str(title_list)

                artist_list = tags.get("artist") or tags.get("ARTIST")
                if artist_list:
                    artist = str(artist_list[0]) if isinstance(artist_list, list) else str(artist_list)

                album_list = tags.get("album") or tags.get("ALBUM")
                if album_list:
                    album = str(album_list[0]) if isinstance(album_list, list) else str(album_list)

            # MP4 / M4A
            if hasattr(tags, "__contains__"):
                if "\xa9nam" in tags:
                    title = str(tags["\xa9nam"][0])
                if "\xa9ART" in tags:
                    artist = str(tags["\xa9ART"][0])
                if "\xa9alb" in tags:
                    album = str(tags["\xa9alb"][0])

        # Album art
        art_data = _extract_album_art(audio)

        return Song(
            id=_generate_id(filepath),
            title=title,
            artist=artist,
            album=album,
            path=filepath,
            duration_ms=duration_ms,
            album_art_data=art_data,
        )

    except Exception:
        return None


def scan_directory(directory: str) -> List[Song]:
    """Recursively scan a directory for audio files and return Song objects."""
    songs = []
    directory = os.path.expanduser(directory)

    if not os.path.isdir(directory):
        return songs

    for root, _dirs, files in os.walk(directory):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in AUDIO_EXTENSIONS:
                filepath = os.path.join(root, filename)
                song = _extract_metadata(filepath)
                if song is not None:
                    songs.append(song)

    # Sort by title
    songs.sort(key=lambda s: s.title.lower())
    return songs


def scan_multiple_directories(directories: List[str]) -> List[Song]:
    """Scan multiple directories and return a combined, deduplicated song list."""
    all_songs = []
    seen_paths = set()

    for directory in directories:
        for song in scan_directory(directory):
            if song.path not in seen_paths:
                seen_paths.add(song.path)
                all_songs.append(song)

    all_songs.sort(key=lambda s: s.title.lower())
    return all_songs


def get_default_music_dirs() -> List[str]:
    """Return default directories to scan for music."""
    dirs = []

    # User's Music folder
    music_dir = os.path.expanduser("~/Music")
    if os.path.isdir(music_dir):
        dirs.append(music_dir)

    # On Windows, also check common locations
    if os.name == "nt":
        # Public Music
        public_music = os.path.join(os.environ.get("PUBLIC", ""), "Music")
        if os.path.isdir(public_music):
            dirs.append(public_music)

    return dirs if dirs else [os.path.expanduser("~/Music")]
