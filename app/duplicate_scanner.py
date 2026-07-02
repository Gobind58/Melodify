"""
Duplicate Scanner — detects duplicate songs by matching title, artist, and duration.
Groups duplicates and recommends which copy to keep (prefers one with album art).
"""
import re
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .models import Song


@dataclass
class DuplicateGroup:
    """A group of songs that appear to be duplicates."""
    key: Tuple[str, str, int]  # (normalized_title, normalized_artist, duration_ms_bucket)
    songs: List[Song] = field(default_factory=list)
    recommended_keep: Optional[Song] = None

    @property
    def count(self) -> int:
        return len(self.songs)

    @property
    def title_display(self) -> str:
        """Use the first song's original title for display."""
        return self.songs[0].title if self.songs else ""

    @property
    def artist_display(self) -> str:
        return self.songs[0].artist if self.songs else ""


def _normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, strip, remove special chars."""
    text = text.lower().strip()
    # Remove common noise like (Official Video), [Remix], feat. etc.
    text = re.sub(r'\(.*?\)|\[.*?\]', '', text)
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^\w\s]', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _duration_bucket(duration_ms: int, tolerance_ms: int = 3000) -> int:
    """Bucket duration to allow minor differences (default ±3 seconds)."""
    return duration_ms // tolerance_ms


def find_duplicates(songs: List[Song]) -> List[DuplicateGroup]:
    """
    Find duplicate songs by matching normalized title + artist + approximate duration.

    Returns a list of DuplicateGroup objects, each containing 2+ songs
    that are likely duplicates. Groups are sorted by song count (most dupes first).
    """
    groups: dict = {}

    for song in songs:
        norm_title = _normalize_text(song.title)
        norm_artist = _normalize_text(song.artist)
        dur_bucket = _duration_bucket(song.duration_ms)

        key = (norm_title, norm_artist, dur_bucket)

        if key not in groups:
            groups[key] = DuplicateGroup(key=key)
        groups[key].songs.append(song)

    # Filter to only groups with 2+ songs (actual duplicates)
    duplicate_groups = [g for g in groups.values() if g.count >= 2]

    # Pick the recommended keep for each group
    for group in duplicate_groups:
        # Prefer: has album art > shorter path (likely more organized) > first found
        group.songs.sort(key=lambda s: (
            0 if s.album_art_data else 1,
            len(s.path),
        ))
        group.recommended_keep = group.songs[0]

    # Sort groups: most duplicates first, then alphabetically
    duplicate_groups.sort(key=lambda g: (-g.count, g.title_display.lower()))

    return duplicate_groups


def get_file_size_str(path: str) -> str:
    """Get human-readable file size."""
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except OSError:
        return "—"
