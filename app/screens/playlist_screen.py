"""
Playlist Screen — displays songs in a specific playlist with management options.
"""
from typing import List, Callable, Optional

import customtkinter as ctk

from ..theme import Theme
from ..models import Song, Playlist
from ..audio_player import AudioPlayer
from ..widgets.song_tile import SongTile


class PlaylistScreen(ctk.CTkFrame):
    """Shows songs in a specific playlist with rename, delete, and remove-song options."""

    def __init__(
        self,
        master,
        player: AudioPlayer,
        playlist: Playlist,
        all_songs: List[Song],
        playlists: Optional[List[Playlist]] = None,
        on_song_tap: Optional[Callable[[int, List[Song]], None]] = None,
        on_rename: Optional[Callable[[str, str], None]] = None,
        on_delete: Optional[Callable[[str], None]] = None,
        on_remove_song: Optional[Callable[[str, str], None]] = None,
        on_add_to_playlist: Optional[Callable[[str, str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=Theme.BACKGROUND, corner_radius=0, **kwargs)

        self._player = player
        self._playlist = playlist
        self._all_songs = all_songs
        self._playlists = playlists or []
        self._on_song_tap = on_song_tap
        self._on_rename = on_rename
        self._on_delete = on_delete
        self._on_remove_song = on_remove_song
        self._on_add_to_playlist = on_add_to_playlist

        # Resolve song objects from paths
        self._songs = self._resolve_songs()

        # ── Header ───────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 0))

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")

        self._title_label = ctk.CTkLabel(
            title_row,
            text=f"🎶  {playlist.name}",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_TITLE, "bold"),
            anchor="w",
        )
        self._title_label.pack(side="left", fill="x", expand=True)

        # Action buttons
        actions = ctk.CTkFrame(title_row, fg_color="transparent")
        actions.pack(side="right")

        rename_btn = ctk.CTkButton(
            actions, text="✏️ Rename", width=80, height=32,
            fg_color=Theme.SURFACE_CARD,
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.2),
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            corner_radius=16,
            border_color=Theme.DIVIDER, border_width=1,
            command=self._handle_rename,
        )
        rename_btn.pack(side="left", padx=4)

        delete_btn = ctk.CTkButton(
            actions, text="🗑 Delete", width=80, height=32,
            fg_color=Theme.SURFACE_CARD,
            hover_color=Theme.with_alpha(Theme.DANGER, 0.2),
            text_color=Theme.DANGER,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            corner_radius=16,
            border_color=Theme.with_alpha(Theme.DANGER, 0.3), border_width=1,
            command=self._handle_delete,
        )
        delete_btn.pack(side="left", padx=4)

        # Song count
        count_label = ctk.CTkLabel(
            header,
            text=f"{len(self._songs)} songs",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="w",
        )
        count_label.pack(fill="x", pady=(4, 0))

        # ── Content ──────────────────────────────────────────────
        self._content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._content_frame.pack(fill="both", expand=True)

        self._build_song_list()

    def _resolve_songs(self) -> List[Song]:
        """Resolve song paths to Song objects."""
        path_to_song = {s.path: s for s in self._all_songs}
        return [path_to_song[p] for p in self._playlist.song_paths if p in path_to_song]

    def _build_song_list(self):
        for widget in self._content_frame.winfo_children():
            widget.destroy()

        if not self._songs:
            self._build_empty()
            return

        scroll = ctk.CTkScrollableFrame(
            self._content_frame,
            fg_color="transparent",
            scrollbar_button_color=Theme.with_alpha(Theme.PRIMARY, 0.3),
            scrollbar_button_hover_color=Theme.PRIMARY,
        )
        scroll.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        for i, song in enumerate(self._songs):
            is_playing = (
                self._player.current_song is not None
                and self._player.current_song.id == song.id
            )
            tile = SongTile(
                scroll, song=song, is_playing=is_playing,
                on_tap=lambda idx=i: self._handle_song_tap(idx),
                playlists=self._playlists,
                on_add_to_playlist=self._on_add_to_playlist,
                show_remove=True,
                on_remove=lambda s=song: self._handle_remove_song(s),
            )
            tile.pack(fill="x", pady=1)

    def _build_empty(self):
        empty = ctk.CTkFrame(self._content_frame, fg_color="transparent")
        empty.pack(expand=True)

        icon = ctk.CTkLabel(
            empty, text="📋", font=(Theme.FONT_FAMILY, 48),
            text_color=Theme.PRIMARY_LIGHT,
        )
        icon.pack(pady=(40, 10))

        msg = ctk.CTkLabel(
            empty, text="This playlist is empty",
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD),
        )
        msg.pack()

        hint = ctk.CTkLabel(
            empty,
            text="Right-click any song and select 'Add to Playlist' to add songs.",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
        )
        hint.pack(pady=(4, 0))

    def _handle_song_tap(self, index: int):
        if self._on_song_tap:
            self._on_song_tap(index, self._songs)

    def _handle_rename(self):
        if self._on_rename:
            dialog = ctk.CTkInputDialog(
                text=f"Rename '{self._playlist.name}':",
                title="Rename Playlist",
            )
            new_name = dialog.get_input()
            if new_name and new_name.strip():
                self._on_rename(self._playlist.id, new_name.strip())

    def _handle_delete(self):
        if self._on_delete:
            self._on_delete(self._playlist.id)

    def _handle_remove_song(self, song: Song):
        if self._on_remove_song:
            self._on_remove_song(self._playlist.id, song.path)

    def refresh(self):
        self._songs = self._resolve_songs()
        self._build_song_list()

    def update_playlists(self, playlists: List[Playlist]):
        self._playlists = playlists
