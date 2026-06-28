"""
Melodify — A premium desktop music player built with Python.
Entry point: sidebar layout, bottom player bar, system tray integration.
"""
import os
import threading
from typing import List, Optional

import customtkinter as ctk

from app.theme import Theme
from app.models import Song, Playlist
from app.audio_player import AudioPlayer
from app.music_scanner import scan_multiple_directories, get_default_music_dirs
from app.playlist_manager import PlaylistManager
from app.tray_widget import TrayWidget
from app.screens.home_screen import HomeScreen
from app.screens.search_screen import SearchScreen
from app.screens.queue_screen import QueueScreen
from app.screens.player_screen import PlayerScreen
from app.screens.playlist_screen import PlaylistScreen
from app.widgets.sidebar import Sidebar
from app.widgets.mini_player import MiniPlayer


class MelodifyApp(ctk.CTk):
    """Main application window for Melodify — desktop layout."""

    def __init__(self):
        super().__init__()

        # ── Window Setup ─────────────────────────────────────────
        self.title("Melodify")
        self.geometry(f"{Theme.WINDOW_WIDTH}x{Theme.WINDOW_HEIGHT}")
        self.minsize(Theme.MIN_WIDTH, Theme.MIN_HEIGHT)
        self.configure(fg_color=Theme.BACKGROUND)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── State ────────────────────────────────────────────────
        self._songs: List[Song] = []
        self._player = AudioPlayer()
        self._playlist_mgr = PlaylistManager()
        self._current_screen = "home"
        self._showing_player = False
        self._music_dirs = get_default_music_dirs()

        # Player callbacks
        self._player.set_on_song_change(self._on_song_changed)
        self._player.set_on_playback_change(self._on_playback_changed)

        # ── System Tray ──────────────────────────────────────────
        self._tray = TrayWidget(
            player=self._player,
            on_show=self._show_from_tray,
            on_quit=self._quit_app,
        )
        self._tray.start()

        # ── Build loading screen ─────────────────────────────────
        self._build_loading_screen()

        # ── Start scanning ───────────────────────────────────────
        self._scan_thread = threading.Thread(target=self._scan_music, daemon=True)
        self._scan_thread.start()

        # ── Update loop ──────────────────────────────────────────
        self._start_update_loop()

        # ── Close → minimize to tray ─────────────────────────────
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ═══════════════════════════════════════════════════════════════
    # LOADING SCREEN
    # ═══════════════════════════════════════════════════════════════

    def _build_loading_screen(self):
        self._loading_frame = ctk.CTkFrame(self, fg_color=Theme.BACKGROUND, corner_radius=0)
        self._loading_frame.pack(fill="both", expand=True)

        center = ctk.CTkFrame(self._loading_frame, fg_color="transparent")
        center.place(relx=0.5, rely=0.45, anchor="center")

        spinner = ctk.CTkFrame(center, fg_color=Theme.PRIMARY, width=72, height=72, corner_radius=36)
        spinner.pack()
        spinner.pack_propagate(False)

        ctk.CTkLabel(
            spinner, text="♪", text_color="white",
            font=(Theme.FONT_FAMILY, 28, "bold"),
        ).pack(expand=True)

        self._loading_label = ctk.CTkLabel(
            center, text="Scanning your music library…",
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD),
        )
        self._loading_label.pack(pady=(20, 0))

        ctk.CTkButton(
            center, text="📁  Add Music Folder",
            fg_color=Theme.SURFACE_CARD,
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.2),
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            corner_radius=20, height=36, width=180,
            border_color=Theme.DIVIDER, border_width=1,
            command=self._add_folder,
        ).pack(pady=(24, 0))

    # ═══════════════════════════════════════════════════════════════
    # MAIN UI — SIDEBAR + CONTENT + BOTTOM BAR
    # ═══════════════════════════════════════════════════════════════

    def _build_main_ui(self):
        """Build the desktop layout after scanning."""
        if hasattr(self, "_loading_frame") and self._loading_frame.winfo_exists():
            self._loading_frame.destroy()

        # ── Root frame ───────────────────────────────────────────
        self._root_frame = ctk.CTkFrame(self, fg_color=Theme.BACKGROUND, corner_radius=0)
        self._root_frame.pack(fill="both", expand=True)

        # ── Bottom bar (mini player) ─────────────────────────────
        self._mini_player = MiniPlayer(
            self._root_frame,
            player=self._player,
            on_expand=self._show_player,
        )
        self._mini_player.pack(fill="x", side="bottom")

        # ── Top area: sidebar + content ──────────────────────────
        self._top_frame = ctk.CTkFrame(self._root_frame, fg_color=Theme.BACKGROUND, corner_radius=0)
        self._top_frame.pack(fill="both", expand=True)

        # ── Sidebar ──────────────────────────────────────────────
        self._sidebar = Sidebar(
            self._top_frame,
            playlists=self._playlist_mgr.playlists,
            on_nav=self._on_nav,
            on_playlist_select=self._on_playlist_select,
            on_new_playlist=self._create_new_playlist,
            on_add_folder=self._add_folder,
        )
        self._sidebar.pack(fill="y", side="left")

        # ── Sidebar divider ──────────────────────────────────────
        divider = ctk.CTkFrame(self._top_frame, fg_color=Theme.DIVIDER, width=1)
        divider.pack(fill="y", side="left")

        # ── Content pane ─────────────────────────────────────────
        self._content_pane = ctk.CTkFrame(
            self._top_frame, fg_color=Theme.BACKGROUND, corner_radius=0,
        )
        self._content_pane.pack(fill="both", expand=True)

        # ── Create screens ───────────────────────────────────────
        self._screens = {}
        self._create_screens()

        # Show home
        self._show_screen("home")

    def _create_screens(self):
        """Create all screen instances."""
        self._screens["home"] = HomeScreen(
            self._content_pane,
            player=self._player,
            songs=self._songs,
            playlists=self._playlist_mgr.playlists,
            on_song_tap=self._play_song,
            on_add_to_playlist=self._add_song_to_playlist,
        )

        self._screens["search"] = SearchScreen(
            self._content_pane,
            player=self._player,
            songs=self._songs,
            playlists=self._playlist_mgr.playlists,
            on_song_tap=self._play_song_from_search,
            on_add_to_playlist=self._add_song_to_playlist,
        )

        self._screens["queue"] = QueueScreen(
            self._content_pane,
            player=self._player,
            playlists=self._playlist_mgr.playlists,
            on_queue_tap=self._play_from_queue,
            on_add_to_playlist=self._add_song_to_playlist,
        )

        self._screens["player"] = PlayerScreen(
            self._content_pane,
            player=self._player,
            on_back=self._hide_player,
        )

    def _show_screen(self, key: str):
        """Show a screen by key."""
        self._current_screen = key
        self._showing_player = False

        for screen in self._screens.values():
            screen.pack_forget()

        # Remove any playlist screen
        if "playlist_view" in self._screens:
            self._screens["playlist_view"].pack_forget()
            self._screens["playlist_view"].destroy()
            del self._screens["playlist_view"]

        if key in self._screens:
            self._screens[key].pack(fill="both", expand=True)
            self._screens[key].refresh()

        self._sidebar.set_active(key)

    # ═══════════════════════════════════════════════════════════════
    # NAVIGATION
    # ═══════════════════════════════════════════════════════════════

    def _on_nav(self, key: str):
        """Handle sidebar navigation click."""
        self._show_screen(key)

    def _on_playlist_select(self, playlist_id: str):
        """Show a playlist's songs in the content pane."""
        playlist = self._playlist_mgr.get_playlist(playlist_id)
        if not playlist:
            return

        # Hide all current screens
        for screen in self._screens.values():
            screen.pack_forget()

        # Remove old playlist view if exists
        if "playlist_view" in self._screens:
            self._screens["playlist_view"].destroy()

        # Create playlist screen
        self._screens["playlist_view"] = PlaylistScreen(
            self._content_pane,
            player=self._player,
            playlist=playlist,
            all_songs=self._songs,
            playlists=self._playlist_mgr.playlists,
            on_song_tap=self._play_from_playlist,
            on_rename=self._rename_playlist,
            on_delete=self._delete_playlist,
            on_remove_song=self._remove_song_from_playlist,
            on_add_to_playlist=self._add_song_to_playlist,
        )
        self._screens["playlist_view"].pack(fill="both", expand=True)
        self._current_screen = f"playlist:{playlist_id}"

    def _show_player(self):
        """Show the full player screen."""
        if not self._player.current_song:
            return

        self._showing_player = True
        for screen in self._screens.values():
            screen.pack_forget()

        self._screens["player"].on_song_changed()
        self._screens["player"].pack(fill="both", expand=True)

    def _hide_player(self):
        """Go back from the player to the previous screen."""
        self._screens["player"].pack_forget()
        self._showing_player = False

        # Re-show the previous screen
        if self._current_screen.startswith("playlist:"):
            pid = self._current_screen.split(":")[1]
            self._on_playlist_select(pid)
        elif self._current_screen in self._screens:
            self._screens[self._current_screen].pack(fill="both", expand=True)
            self._screens[self._current_screen].refresh()

    # ═══════════════════════════════════════════════════════════════
    # PLAYBACK
    # ═══════════════════════════════════════════════════════════════

    def _play_song(self, index: int):
        self._player.load_queue(self._songs, start_index=index)
        self._show_player()

    def _play_song_from_search(self, real_index: int, from_search: bool = False):
        self._player.load_queue(self._songs, start_index=real_index)
        self._show_player()

    def _play_from_queue(self, index: int):
        self._player.play_at_index(index)
        self._show_player()

    def _play_from_playlist(self, index: int, songs: List[Song]):
        """Play from a playlist's song list."""
        self._player.load_queue(songs, start_index=index)
        self._show_player()

    # ═══════════════════════════════════════════════════════════════
    # PLAYLISTS
    # ═══════════════════════════════════════════════════════════════

    def _create_new_playlist(self):
        """Open dialog to create a new playlist."""
        dialog = ctk.CTkInputDialog(
            text="Enter playlist name:",
            title="New Playlist",
        )
        name = dialog.get_input()
        if name and name.strip():
            self._playlist_mgr.create_playlist(name.strip())
            self._refresh_sidebar_playlists()

    def _rename_playlist(self, playlist_id: str, new_name: str):
        self._playlist_mgr.rename_playlist(playlist_id, new_name)
        self._refresh_sidebar_playlists()
        # Re-open the playlist to refresh
        self._on_playlist_select(playlist_id)

    def _delete_playlist(self, playlist_id: str):
        self._playlist_mgr.delete_playlist(playlist_id)
        self._refresh_sidebar_playlists()
        self._show_screen("home")

    def _add_song_to_playlist(self, playlist_id: str, song_path: str):
        self._playlist_mgr.add_song_to_playlist(playlist_id, song_path)

    def _remove_song_from_playlist(self, playlist_id: str, song_path: str):
        self._playlist_mgr.remove_song_from_playlist(playlist_id, song_path)
        # Refresh the current playlist view
        if self._current_screen == f"playlist:{playlist_id}":
            self._on_playlist_select(playlist_id)

    def _refresh_sidebar_playlists(self):
        """Update sidebar with latest playlists."""
        playlists = self._playlist_mgr.playlists
        self._sidebar.update_playlists(playlists)

        # Update playlist references in all screens
        for screen in self._screens.values():
            if hasattr(screen, "update_playlists"):
                screen.update_playlists(playlists)

    # ═══════════════════════════════════════════════════════════════
    # SCANNING
    # ═══════════════════════════════════════════════════════════════

    def _scan_music(self):
        self._songs = scan_multiple_directories(self._music_dirs)
        self.after(0, self._on_scan_complete)

    def _on_scan_complete(self):
        self._build_main_ui()

    def _add_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Select Music Folder")
        if folder:
            self._music_dirs.append(folder)
            if hasattr(self, "_loading_label") and self._loading_label.winfo_exists():
                self._loading_label.configure(text=f"Scanning {os.path.basename(folder)}…")
            self._scan_thread = threading.Thread(target=self._scan_music, daemon=True)
            self._scan_thread.start()

    # ═══════════════════════════════════════════════════════════════
    # CALLBACKS
    # ═══════════════════════════════════════════════════════════════

    def _on_song_changed(self):
        self.after(0, self._refresh_all)

    def _on_playback_changed(self):
        self.after(0, self._refresh_all)

    def _refresh_all(self):
        try:
            self._mini_player.update_display()
            self._tray.update_tooltip()

            if self._showing_player:
                self._screens["player"].refresh()
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════
    # UPDATE LOOP
    # ═══════════════════════════════════════════════════════════════

    def _start_update_loop(self):
        self._update()

    def _update(self):
        try:
            self._player.check_events()

            if hasattr(self, "_mini_player"):
                self._mini_player.update_display()

            if self._showing_player and "player" in self._screens:
                self._screens["player"].refresh()

        except Exception:
            pass

        self.after(200, self._update)

    # ═══════════════════════════════════════════════════════════════
    # WINDOW MANAGEMENT & TRAY
    # ═══════════════════════════════════════════════════════════════

    def _on_close(self):
        """Minimize to tray instead of quitting."""
        self.withdraw()

    def _show_from_tray(self):
        """Restore window from tray."""
        self.after(0, self._restore_window)

    def _restore_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _quit_app(self):
        """Actually quit the application."""
        self.after(0, self._cleanup_and_quit)

    def _cleanup_and_quit(self):
        self._tray.stop()
        self._player.cleanup()
        self.destroy()


def main():
    app = MelodifyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
