"""
Data models for Melodify.
"""
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Song:
    """Represents a single audio track with metadata."""
    id: int
    title: str
    artist: str
    album: str
    path: str
    duration_ms: int
    album_art_data: Optional[bytes] = field(default=None, repr=False)

    @property
    def duration_formatted(self) -> str:
        """Format duration as MM:SS."""
        total_seconds = self.duration_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds as a float."""
        return self.duration_ms / 1000.0

    @property
    def initial(self) -> str:
        """First character of the title, uppercase, for fallback art."""
        return self.title[0].upper() if self.title else "♪"


@dataclass
class Playlist:
    """Represents a user-created playlist."""
    id: str
    name: str
    created_at: str
    song_paths: List[str] = field(default_factory=list)

    @property
    def song_count(self) -> int:
        return len(self.song_paths)
