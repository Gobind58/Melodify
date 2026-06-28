"""
Search Screen — search bar, genre categories, and filtered results.
Desktop-optimized: no embedded mini player.
"""
from typing import List, Callable, Optional

import customtkinter as ctk

from ..theme import Theme
from ..models import Song, Playlist
from ..audio_player import AudioPlayer
from ..widgets.song_tile import SongTile


class SearchScreen(ctk.CTkFrame):
    """Search screen with text input, genre grid, and filtered song results."""

    GENRES = list(Theme.GENRE_COLORS.keys())

    def __init__(
        self,
        master,
        player: AudioPlayer,
        songs: List[Song],
        playlists: Optional[List[Playlist]] = None,
        on_song_tap: Optional[Callable[[int, bool], None]] = None,
        on_add_to_playlist: Optional[Callable[[str, str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=Theme.BACKGROUND, corner_radius=0, **kwargs)

        self._player = player
        self._all_songs = songs
        self._filtered_songs: List[Song] = []
        self._on_song_tap = on_song_tap
        self._on_add_to_playlist = on_add_to_playlist
        self._playlists = playlists or []
        self._search_query = ""

        # ── Header ───────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 0))

        title = ctk.CTkLabel(
            header,
            text="Search",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_TITLE, "bold"),
            anchor="w",
        )
        title.pack(fill="x")

        # ── Search Bar ───────────────────────────────────────────
        self._search_frame = ctk.CTkFrame(
            self,
            fg_color=Theme.SURFACE_CARD,
            corner_radius=12,
            border_color=Theme.DIVIDER,
            border_width=1,
        )
        self._search_frame.pack(fill="x", padx=20, pady=(12, 0))

        search_inner = ctk.CTkFrame(self._search_frame, fg_color="transparent")
        search_inner.pack(fill="x", padx=12, pady=6)

        search_icon = ctk.CTkLabel(
            search_inner, text="🔍",
            font=(Theme.FONT_FAMILY, 14),
            text_color=Theme.TEXT_HINT, width=24,
        )
        search_icon.pack(side="left", padx=(0, 8))

        self._search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="Songs, artists, albums…",
            placeholder_text_color=Theme.TEXT_HINT,
            text_color=Theme.TEXT_PRIMARY,
            fg_color="transparent",
            border_width=0,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD),
            height=30,
        )
        self._search_entry.pack(side="left", fill="x", expand=True)
        self._search_entry.bind("<KeyRelease>", self._on_search)

        self._clear_btn = ctk.CTkButton(
            search_inner, text="✕", width=24, height=24,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, 14), corner_radius=12,
            command=self._clear_search,
        )
        self._clear_btn.pack_forget()

        self._search_entry.bind("<FocusIn>", self._on_focus_in)
        self._search_entry.bind("<FocusOut>", self._on_focus_out)

        # ── Content ──────────────────────────────────────────────
        self._content_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._content_frame.pack(fill="both", expand=True)

        self._show_genres()

    def _on_focus_in(self, event=None):
        self._search_frame.configure(
            border_color=Theme.with_alpha(Theme.PRIMARY, 0.6),
        )

    def _on_focus_out(self, event=None):
        self._search_frame.configure(border_color=Theme.DIVIDER)

    def _on_search(self, event=None):
        query = self._search_entry.get().strip().lower()
        self._search_query = query

        if query:
            self._clear_btn.pack(side="right", padx=(4, 0))
            self._filtered_songs = [
                s for s in self._all_songs
                if query in s.title.lower()
                or query in s.artist.lower()
                or query in s.album.lower()
            ]
            self._show_results()
        else:
            self._clear_btn.pack_forget()
            self._show_genres()

    def _clear_search(self):
        self._search_entry.delete(0, "end")
        self._search_query = ""
        self._clear_btn.pack_forget()
        self._show_genres()

    def _show_genres(self):
        """Display the genre category grid."""
        for widget in self._content_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkLabel(
            self._content_frame,
            text="Browse Categories",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LG + 2, "bold"),
            anchor="w",
        )
        header.pack(fill="x", padx=24, pady=(16, 12))

        grid_frame = ctk.CTkFrame(self._content_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=20)

        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)

        for i, genre in enumerate(self.GENRES):
            colors = Theme.GENRE_COLORS[genre]
            row = i // 4
            col = i % 4

            card = ctk.CTkFrame(
                grid_frame, fg_color=colors[0],
                corner_radius=12, height=70, cursor="hand2",
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            card.pack_propagate(False)

            label = ctk.CTkLabel(
                card, text=genre,
                text_color="white",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD, "bold"),
                anchor="sw",
            )
            label.pack(fill="both", expand=True, padx=14, pady=10, anchor="sw")

            for w in [card, label]:
                w.bind("<Button-1>", lambda e, g=genre: self._search_genre(g))

        for i in range((len(self.GENRES) + 3) // 4):
            grid_frame.grid_rowconfigure(i, weight=1)

    def _search_genre(self, genre: str):
        self._search_entry.delete(0, "end")
        self._search_entry.insert(0, genre)
        self._on_search()

    def _show_results(self):
        """Display filtered search results."""
        for widget in self._content_frame.winfo_children():
            widget.destroy()

        if not self._filtered_songs:
            empty = ctk.CTkFrame(self._content_frame, fg_color="transparent")
            empty.pack(expand=True)

            icon = ctk.CTkLabel(
                empty, text="🔍", font=(Theme.FONT_FAMILY, 48),
                text_color=Theme.PRIMARY_LIGHT,
            )
            icon.pack(pady=(40, 10))

            msg = ctk.CTkLabel(
                empty,
                text=f'No results for "{self._search_query}"',
                text_color=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD),
            )
            msg.pack()
            return

        count_label = ctk.CTkLabel(
            self._content_frame,
            text=f"{len(self._filtered_songs)} results",
            text_color=Theme.TEXT_SECONDARY,
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

        for i, song in enumerate(self._filtered_songs):
            is_playing = (
                self._player.current_song is not None
                and self._player.current_song.id == song.id
            )
            tile = SongTile(
                scroll, song=song, is_playing=is_playing,
                on_tap=lambda idx=i: self._handle_result_tap(idx),
                playlists=self._playlists,
                on_add_to_playlist=self._on_add_to_playlist,
            )
            tile.pack(fill="x", pady=1)

    def _handle_result_tap(self, filtered_index: int):
        song = self._filtered_songs[filtered_index]
        try:
            real_index = self._all_songs.index(song)
        except ValueError:
            real_index = filtered_index

        if self._on_song_tap:
            self._on_song_tap(real_index, True)

    def refresh(self):
        if self._search_query:
            self._show_results()

    def update_playlists(self, playlists: List[Playlist]):
        self._playlists = playlists
