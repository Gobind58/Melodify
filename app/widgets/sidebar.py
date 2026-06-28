"""
Sidebar Widget — vertical navigation with tabs and playlist list.
"""
from typing import Callable, Optional, List

import customtkinter as ctk

from ..theme import Theme
from ..models import Playlist


class Sidebar(ctk.CTkFrame):
    """Vertical sidebar with navigation items, playlists, and action buttons."""

    NAV_ITEMS = [
        {"key": "home",   "label": "Home",   "icon": "🏠"},
        {"key": "search", "label": "Search", "icon": "🔍"},
        {"key": "queue",  "label": "Queue",  "icon": "🎵"},
    ]

    def __init__(
        self,
        master,
        playlists: List[Playlist],
        on_nav: Optional[Callable[[str], None]] = None,
        on_playlist_select: Optional[Callable[[str], None]] = None,
        on_new_playlist: Optional[Callable] = None,
        on_add_folder: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=Theme.SIDEBAR_BG,
            corner_radius=0,
            width=Theme.SIDEBAR_WIDTH,
            **kwargs,
        )
        self.pack_propagate(False)

        self._on_nav = on_nav
        self._on_playlist_select = on_playlist_select
        self._on_new_playlist = on_new_playlist
        self._on_add_folder = on_add_folder
        self._current_key = "home"
        self._nav_buttons = {}
        self._playlist_buttons = {}
        self._playlists = playlists

        # ── App Logo / Title ─────────────────────────────────────
        logo_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        logo_frame.pack(fill="x", padx=16, pady=(16, 8))
        logo_frame.pack_propagate(False)

        logo_label = ctk.CTkLabel(
            logo_frame,
            text="♪  Melodify",
            text_color=Theme.PRIMARY_LIGHT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XL, "bold"),
            anchor="w",
        )
        logo_label.pack(fill="x", expand=True, anchor="w")

        # ── Navigation Items ─────────────────────────────────────
        nav_label = ctk.CTkLabel(
            self,
            text="MENU",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XS, "bold"),
            anchor="w",
        )
        nav_label.pack(fill="x", padx=20, pady=(8, 4))

        for item in self.NAV_ITEMS:
            btn = self._create_nav_button(item["key"], item["icon"], item["label"])
            btn.pack(fill="x", padx=8, pady=1)
            self._nav_buttons[item["key"]] = btn

        # ── Divider ──────────────────────────────────────────────
        divider = ctk.CTkFrame(self, fg_color=Theme.DIVIDER, height=1)
        divider.pack(fill="x", padx=16, pady=(12, 8))

        # ── Playlists Section ────────────────────────────────────
        playlist_header = ctk.CTkFrame(self, fg_color="transparent")
        playlist_header.pack(fill="x", padx=16, pady=(0, 4))

        playlist_label = ctk.CTkLabel(
            playlist_header,
            text="PLAYLISTS",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XS, "bold"),
            anchor="w",
        )
        playlist_label.pack(side="left", fill="x", expand=True)

        add_pl_btn = ctk.CTkButton(
            playlist_header,
            text="+",
            width=24,
            height=24,
            fg_color="transparent",
            hover_color=Theme.SIDEBAR_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, 16, "bold"),
            corner_radius=12,
            command=self._handle_new_playlist,
        )
        add_pl_btn.pack(side="right")

        # Scrollable playlist list
        self._playlist_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Theme.with_alpha(Theme.PRIMARY, 0.2),
            scrollbar_button_hover_color=Theme.PRIMARY,
        )
        self._playlist_frame.pack(fill="both", expand=True, padx=4)

        self._rebuild_playlist_list()

        # ── Bottom Actions ───────────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=8, pady=(4, 12))

        add_folder_btn = ctk.CTkButton(
            bottom,
            text="📁  Add Folder",
            fg_color="transparent",
            hover_color=Theme.SIDEBAR_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="w",
            height=36,
            corner_radius=8,
            command=self._handle_add_folder,
        )
        add_folder_btn.pack(fill="x", padx=4)

        # Update initial state
        self._update_nav_highlight()

    def _create_nav_button(self, key: str, icon: str, label: str) -> ctk.CTkButton:
        """Create a sidebar navigation button."""
        btn = ctk.CTkButton(
            self,
            text=f"  {icon}   {label}",
            fg_color="transparent",
            hover_color=Theme.SIDEBAR_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD),
            anchor="w",
            height=40,
            corner_radius=10,
            command=lambda: self._handle_nav(key),
        )
        return btn

    def _create_playlist_button(self, playlist: Playlist) -> ctk.CTkButton:
        """Create a sidebar playlist entry."""
        btn = ctk.CTkButton(
            self._playlist_frame,
            text=f"  🎶  {playlist.name}",
            fg_color="transparent",
            hover_color=Theme.SIDEBAR_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="w",
            height=34,
            corner_radius=8,
            command=lambda pid=playlist.id: self._handle_playlist(pid),
        )
        return btn

    def _handle_nav(self, key: str):
        self._current_key = key
        self._update_nav_highlight()
        if self._on_nav:
            self._on_nav(key)

    def _handle_playlist(self, playlist_id: str):
        self._current_key = f"playlist:{playlist_id}"
        self._update_nav_highlight()
        if self._on_playlist_select:
            self._on_playlist_select(playlist_id)

    def _handle_new_playlist(self):
        if self._on_new_playlist:
            self._on_new_playlist()

    def _handle_add_folder(self):
        if self._on_add_folder:
            self._on_add_folder()

    def _update_nav_highlight(self):
        """Update visual state of all nav buttons."""
        for key, btn in self._nav_buttons.items():
            if key == self._current_key:
                btn.configure(
                    fg_color=Theme.SIDEBAR_ACTIVE,
                    text_color=Theme.PRIMARY_LIGHT,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Theme.TEXT_SECONDARY,
                )

        for pid, btn in self._playlist_buttons.items():
            full_key = f"playlist:{pid}"
            if full_key == self._current_key:
                btn.configure(
                    fg_color=Theme.SIDEBAR_ACTIVE,
                    text_color=Theme.PRIMARY_LIGHT,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Theme.TEXT_SECONDARY,
                )

    def _rebuild_playlist_list(self):
        """Rebuild the playlist buttons from the current playlist data."""
        for widget in self._playlist_frame.winfo_children():
            widget.destroy()
        self._playlist_buttons.clear()

        for playlist in self._playlists:
            btn = self._create_playlist_button(playlist)
            btn.pack(fill="x", pady=1)
            self._playlist_buttons[playlist.id] = btn

    def update_playlists(self, playlists: List[Playlist]):
        """Update the displayed playlists."""
        self._playlists = playlists
        self._rebuild_playlist_list()
        self._update_nav_highlight()

    def set_active(self, key: str):
        """Programmatically set the active nav item."""
        self._current_key = key
        self._update_nav_highlight()
