"""
Queue Screen — displays the current playback queue.
Desktop-optimized: no embedded mini player.
"""
from typing import Callable, Optional, List

import customtkinter as ctk

from ..theme import Theme
from ..models import Playlist
from ..audio_player import AudioPlayer
from ..widgets.song_tile import SongTile


class QueueScreen(ctk.CTkFrame):
    """Shows the current playback queue with highlighted currently playing song."""

    def __init__(
        self,
        master,
        player: AudioPlayer,
        playlists: Optional[List[Playlist]] = None,
        on_queue_tap: Optional[Callable[[int], None]] = None,
        on_add_to_playlist: Optional[Callable[[str, str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=Theme.BACKGROUND, corner_radius=0, **kwargs)

        self._player = player
        self._on_queue_tap = on_queue_tap
        self._on_add_to_playlist = on_add_to_playlist
        self._playlists = playlists or []

        # ── Header ───────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 0))

        title = ctk.CTkLabel(
            header,
            text="Queue",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_TITLE, "bold"),
            anchor="w",
        )
        title.pack(fill="x")

        # ── Content ──────────────────────────────────────────────
        self._content_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._content_frame.pack(fill="both", expand=True)

        self._build_queue()

    def _build_queue(self):
        for widget in self._content_frame.winfo_children():
            widget.destroy()

        queue = self._player.queue

        if not queue:
            self._build_empty()
            return

        count_label = ctk.CTkLabel(
            self._content_frame,
            text=f"{len(queue)} songs in queue",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="w",
        )
        count_label.pack(fill="x", padx=24, pady=(12, 4))

        scroll = ctk.CTkScrollableFrame(
            self._content_frame,
            fg_color="transparent",
            scrollbar_button_color=Theme.with_alpha(Theme.PRIMARY, 0.3),
            scrollbar_button_hover_color=Theme.PRIMARY,
        )
        scroll.pack(fill="both", expand=True, padx=8)

        for i, song in enumerate(queue):
            is_playing = self._player.current_index == i
            tile = SongTile(
                scroll, song=song, is_playing=is_playing,
                on_tap=lambda idx=i: self._handle_tap(idx),
                playlists=self._playlists,
                on_add_to_playlist=self._on_add_to_playlist,
            )
            tile.pack(fill="x", pady=1)

    def _build_empty(self):
        empty = ctk.CTkFrame(self._content_frame, fg_color="transparent")
        empty.pack(expand=True)

        icon = ctk.CTkLabel(
            empty, text="🎶", font=(Theme.FONT_FAMILY, 64),
            text_color=Theme.PRIMARY_LIGHT,
        )
        icon.pack(pady=(60, 10))

        title = ctk.CTkLabel(
            empty, text="Queue is empty",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XL, "bold"),
        )
        title.pack(pady=(0, 8))

        subtitle = ctk.CTkLabel(
            empty, text="Play a song to start building your queue.",
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
        )
        subtitle.pack()

    def _handle_tap(self, index: int):
        if self._on_queue_tap:
            self._on_queue_tap(index)

    def refresh(self):
        self._build_queue()

    def update_playlists(self, playlists: List[Playlist]):
        self._playlists = playlists
