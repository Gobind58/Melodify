"""
Song Tile Widget — a clickable list item with right-click context menu.
"""
from typing import Callable, Optional, List
import tkinter as tk

import customtkinter as ctk

from ..theme import Theme
from ..models import Song, Playlist
from .album_art import AlbumArt


class SongTile(ctk.CTkFrame):
    """A single row in the song list with album art, title, artist, duration, and context menu."""

    def __init__(
        self,
        master,
        song: Song,
        is_playing: bool = False,
        track_number: int = 0,
        on_tap: Optional[Callable] = None,
        playlists: Optional[List[Playlist]] = None,
        on_add_to_playlist: Optional[Callable[[str, str], None]] = None,
        on_play_next: Optional[Callable[[Song], None]] = None,
        on_add_to_queue: Optional[Callable[[Song], None]] = None,
        show_remove: bool = False,
        on_remove: Optional[Callable] = None,
        **kwargs,
    ):
        self._song = song
        self._is_playing = is_playing
        self._on_tap = on_tap
        self._playlists = playlists or []
        self._on_add_to_playlist = on_add_to_playlist
        self._on_play_next = on_play_next
        self._on_add_to_queue = on_add_to_queue
        self._show_remove = show_remove
        self._on_remove = on_remove

        # Colors based on playing state
        bg = Theme.with_alpha(Theme.PRIMARY, 0.12) if is_playing else "transparent"
        border_color = Theme.with_alpha(Theme.PRIMARY, 0.30) if is_playing else Theme.BACKGROUND
        border_width = 1 if is_playing else 0

        super().__init__(
            master,
            fg_color=bg,
            corner_radius=10,
            border_color=border_color,
            border_width=border_width,
            height=Theme.SONG_TILE_H,
            cursor="hand2",
            **kwargs,
        )

        self.pack_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        # Bind clicks
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Button-3>", self._show_context_menu)

        # ── Track Number / Playing Indicator ─────────────────────
        if track_number > 0 or is_playing:
            indicator_frame = ctk.CTkFrame(self, fg_color="transparent", width=32)
            indicator_frame.grid(row=0, column=0, padx=(8, 0), pady=10)
            indicator_frame.pack_propagate(False)
            indicator_frame.bind("<Button-1>", self._handle_click)

            if is_playing:
                # Animated-look playing dot
                dot = ctk.CTkFrame(
                    indicator_frame,
                    fg_color=Theme.PLAYING_DOT,
                    width=8, height=8, corner_radius=4,
                )
                dot.pack(expand=True)
            else:
                ctk.CTkLabel(
                    indicator_frame,
                    text=str(track_number),
                    text_color=Theme.TEXT_HINT,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
                ).pack(expand=True)

            art_col = 1
        else:
            art_col = 0

        # ── Album Art ────────────────────────────────────────────
        self._art = AlbumArt(
            self,
            art_data=song.album_art_data,
            size=Theme.ART_SIZE_SM,
            title=song.title,
            corner_radius=8,
        )
        self._art.grid(row=0, column=art_col, padx=(10 if art_col == 0 else 4, 8), pady=10)
        self._art.bind("<Button-1>", self._handle_click)
        self._art.bind("<Button-3>", self._show_context_menu)

        info_col = art_col + 1
        self.grid_columnconfigure(info_col, weight=1)

        # ── Info ─────────────────────────────────────────────────
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=info_col, sticky="nsew", pady=10)
        info_frame.bind("<Button-1>", self._handle_click)
        info_frame.bind("<Button-3>", self._show_context_menu)

        title_color = Theme.PRIMARY_LIGHT if is_playing else Theme.TEXT_PRIMARY
        title_weight = "bold" if is_playing else "normal"

        self._title_label = ctk.CTkLabel(
            info_frame,
            text=song.title,
            text_color=title_color,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD, title_weight),
            anchor="w",
        )
        self._title_label.pack(fill="x", anchor="w")
        self._title_label.bind("<Button-1>", self._handle_click)
        self._title_label.bind("<Button-3>", self._show_context_menu)

        self._artist_label = ctk.CTkLabel(
            info_frame,
            text=song.artist,
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="w",
        )
        self._artist_label.pack(fill="x", anchor="w")
        self._artist_label.bind("<Button-1>", self._handle_click)
        self._artist_label.bind("<Button-3>", self._show_context_menu)

        # ── Right side (duration + optional remove) ──────────────
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=info_col + 1, padx=(0, 8))

        self._duration_label = ctk.CTkLabel(
            right_frame,
            text=song.duration_formatted,
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            width=45,
        )
        self._duration_label.pack(side="left")
        self._duration_label.bind("<Button-1>", self._handle_click)

        if show_remove and on_remove:
            remove_btn = ctk.CTkButton(
                right_frame,
                text="✕",
                width=28, height=28,
                fg_color="transparent",
                hover_color=Theme.with_alpha(Theme.DANGER, 0.2),
                text_color=Theme.TEXT_HINT,
                font=(Theme.FONT_FAMILY, 12),
                corner_radius=14,
                command=on_remove,
            )
            remove_btn.pack(side="left", padx=(4, 0))

        # ── Hover effect ─────────────────────────────────────────
        if not is_playing:
            self._setup_hover()

    def _handle_click(self, event=None):
        if self._on_tap:
            self._on_tap()

    def _show_context_menu(self, event):
        """Show right-click context menu."""
        menu = tk.Menu(self, tearoff=0,
                       bg=Theme.SURFACE_CARD,
                       fg=Theme.TEXT_PRIMARY,
                       activebackground=Theme.PRIMARY,
                       activeforeground="white",
                       font=(Theme.FONT_FAMILY, 10),
                       relief="flat",
                       borderwidth=1)

        if self._on_play_next:
            menu.add_command(label="▶  Play Next",
                           command=lambda: self._on_play_next(self._song))

        if self._on_add_to_queue:
            menu.add_command(label="📋  Add to Queue",
                           command=lambda: self._on_add_to_queue(self._song))

        if self._playlists and self._on_add_to_playlist:
            menu.add_separator()
            playlist_menu = tk.Menu(menu, tearoff=0,
                                   bg=Theme.SURFACE_CARD,
                                   fg=Theme.TEXT_PRIMARY,
                                   activebackground=Theme.PRIMARY,
                                   activeforeground="white",
                                   font=(Theme.FONT_FAMILY, 10),
                                   relief="flat")

            for pl in self._playlists:
                playlist_menu.add_command(
                    label=f"  🎶  {pl.name}",
                    command=lambda pid=pl.id: self._on_add_to_playlist(pid, self._song.path),
                )

            menu.add_cascade(label="➕  Add to Playlist", menu=playlist_menu)

        if self._show_remove and self._on_remove:
            menu.add_separator()
            menu.add_command(label="🗑  Remove from Playlist",
                           command=self._on_remove)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _setup_hover(self):
        hover_color = Theme.CARD_HOVER

        def on_enter(e):
            self.configure(fg_color=hover_color)

        def on_leave(e):
            self.configure(fg_color="transparent")

        for widget in [self, self._art, self._title_label, self._artist_label, self._duration_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
