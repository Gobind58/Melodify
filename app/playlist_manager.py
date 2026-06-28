"""
Playlist Manager — CRUD operations for playlists with JSON persistence.
"""
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional

from .models import Playlist


class PlaylistManager:
    """Manages playlists — create, read, update, delete with JSON file persistence."""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.expanduser("~"), ".melodify")
        self._data_dir = data_dir
        self._file_path = os.path.join(data_dir, "playlists.json")
        self._playlists: List[Playlist] = []

        os.makedirs(data_dir, exist_ok=True)
        self._load()

    # ── Properties ───────────────────────────────────────────────
    @property
    def playlists(self) -> List[Playlist]:
        return list(self._playlists)

    # ── CRUD ─────────────────────────────────────────────────────
    def create_playlist(self, name: str) -> Playlist:
        """Create a new playlist with the given name."""
        playlist = Playlist(
            id=str(uuid.uuid4())[:8],
            name=name.strip(),
            created_at=datetime.now().isoformat(),
            song_paths=[],
        )
        self._playlists.append(playlist)
        self._save()
        return playlist

    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """Get a playlist by ID."""
        for p in self._playlists:
            if p.id == playlist_id:
                return p
        return None

    def rename_playlist(self, playlist_id: str, new_name: str) -> bool:
        """Rename a playlist."""
        playlist = self.get_playlist(playlist_id)
        if playlist:
            playlist.name = new_name.strip()
            self._save()
            return True
        return False

    def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist by ID."""
        for i, p in enumerate(self._playlists):
            if p.id == playlist_id:
                self._playlists.pop(i)
                self._save()
                return True
        return False

    def add_song_to_playlist(self, playlist_id: str, song_path: str) -> bool:
        """Add a song to a playlist (avoids duplicates)."""
        playlist = self.get_playlist(playlist_id)
        if playlist and song_path not in playlist.song_paths:
            playlist.song_paths.append(song_path)
            self._save()
            return True
        return False

    def remove_song_from_playlist(self, playlist_id: str, song_path: str) -> bool:
        """Remove a song from a playlist."""
        playlist = self.get_playlist(playlist_id)
        if playlist and song_path in playlist.song_paths:
            playlist.song_paths.remove(song_path)
            self._save()
            return True
        return False

    # ── Persistence ──────────────────────────────────────────────
    def _load(self):
        """Load playlists from JSON file."""
        if not os.path.exists(self._file_path):
            self._playlists = []
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._playlists = [
                Playlist(
                    id=p["id"],
                    name=p["name"],
                    created_at=p.get("created_at", ""),
                    song_paths=p.get("song_paths", []),
                )
                for p in data.get("playlists", [])
            ]
        except (json.JSONDecodeError, KeyError, TypeError):
            self._playlists = []

    def _save(self):
        """Save playlists to JSON file."""
        data = {
            "playlists": [
                {
                    "id": p.id,
                    "name": p.name,
                    "created_at": p.created_at,
                    "song_paths": p.song_paths,
                }
                for p in self._playlists
            ]
        }

        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"Error saving playlists: {e}")
