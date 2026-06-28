"""
Home Screen — greeting, app title, and scrollable song list.
Desktop-optimized: no embedded mini player (handled by main.py bottom bar).
"""
from datetime import datetime
from typing import List, Callable, Optional

import customtkinter as ctk

from ..theme import Theme
from ..models import Song, Playlist
from ..audio_player import AudioPlayer
from ..widgets.song_tile import SongTile


class HomeScreen(ctk.CTkFrame):
    """Main home screen with greeting header and scrollable song list."""

    def __init__(
        self,
        master,
        player: AudioPlayer,
        songs: List[Song],
        playlists: Optional[List[Playlist]] = None,
        on_song_tap: Optional[Callable[[int], None]] = None,
        on_add_to_playlist: Optional[Callable[[str, str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=Theme.BACKGROUND, corner_radius=0, **kwargs)

        self._player = player
        self._songs = songs
        self._playlists = playlists or []
        self._on_song_tap = on_song_tap
        self._on_add_to_playlist = on_add_to_playlist

        # ── Header ───────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header.pack(fill="x", padx=24, pady=(20, 0))
        header.pack_propagate(False)

        greeting_text = self._get_greeting()
        greeting_label = ctk.CTkLabel(
            header,
            text=greeting_text,
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD),
            anchor="w",
        )
        greeting_label.pack(fill="x", anchor="w")

        title_label = ctk.CTkLabel(
            header,
            text="Welcome to Melodify",
            text_color=Theme.PRIMARY_LIGHT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_TITLE, "bold"),
            anchor="w",
        )
        title_label.pack(fill="x", anchor="w", pady=(2, 0))

        # ── Content ──────────────────────────────────────────────
        if not songs:
            self._build_empty_view()
        else:
            self._build_song_list()

    def _get_greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning ☀️"
        elif hour < 17:
            return "Good Afternoon 🌤️"
        elif hour < 21:
            return "Good Evening 🌆"
        return "Good Night 🌙"

    def _build_empty_view(self):
        """Show empty state."""
        empty = ctk.CTkFrame(self, fg_color="transparent")
        empty.pack(expand=True, fill="both")

        icon = ctk.CTkLabel(
            empty, text="🎵",
            font=(Theme.FONT_FAMILY, 64),
            text_color=Theme.PRIMARY_LIGHT,
        )
        icon.pack(pady=(60, 10))

        title = ctk.CTkLabel(
            empty,
            text="No music found",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XL, "bold"),
        )
        title.pack(pady=(0, 8))

        subtitle = ctk.CTkLabel(
            empty,
            text="Add some music files to your Music folder,\nor click 'Add Folder' in the sidebar.",
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            justify="center",
        )
        subtitle.pack()

    def _build_song_list(self):
        """Build the scrollable song list."""
        # Section header with count
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(16, 8))

        section_header = ctk.CTkLabel(
            header_frame,
            text="All Songs",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LG + 2, "bold"),
            anchor="w",
        )
        section_header.pack(side="left")

        count_label = ctk.CTkLabel(
            header_frame,
            text=f"{len(self._songs)} songs",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="e",
        )
        count_label.pack(side="right")

        # Scrollable list
        self._scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Theme.with_alpha(Theme.PRIMARY, 0.3),
            scrollbar_button_hover_color=Theme.PRIMARY,
        )
        self._scroll_frame.pack(fill="both", expand=True, padx=8)

        for i, song in enumerate(self._songs):
            is_playing = self._player.current_index == i
            tile = SongTile(
                self._scroll_frame,
                song=song,
                is_playing=is_playing,
                on_tap=lambda idx=i: self._handle_song_tap(idx),
                playlists=self._playlists,
                on_add_to_playlist=self._on_add_to_playlist,
            )
            tile.pack(fill="x", pady=1)

    def _handle_song_tap(self, index: int):
        if self._on_song_tap:
            self._on_song_tap(index)

    def refresh(self):
        """Refresh — no embedded mini player to update."""
        pass

    def update_playlists(self, playlists: List[Playlist]):
        """Update the playlist references for context menus."""
        self._playlists = playlists
