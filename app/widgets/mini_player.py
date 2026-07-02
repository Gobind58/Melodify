"""
Mini Player Widget — full-width bottom bar with album art, info, controls, and progress.
Desktop-optimized layout spanning the entire window width.
"""
from typing import Callable, Optional

import customtkinter as ctk

from ..theme import Theme
from ..audio_player import AudioPlayer
from .album_art import AlbumArt


class MiniPlayer(ctk.CTkFrame):
    """Desktop bottom bar with song info, progress slider, and playback controls."""

    def __init__(
        self,
        master,
        player: AudioPlayer,
        on_expand: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=Theme.MINI_PLAYER_BG,
            corner_radius=0,
            height=Theme.BOTTOM_BAR_H,
            border_color=Theme.DIVIDER,
            border_width=1,
            **kwargs,
        )
        self.pack_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        self._player = player
        self._on_expand = on_expand
        self._art_widget = None
        self._updating_slider = False
        self._current_song_id = None  # Track to avoid re-creating art every tick

        # ── Left: Album Art + Song Info ──────────────────────────
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsw", padx=(12, 0))

        # Art container with glow effect
        self._art_container = ctk.CTkFrame(left_frame, fg_color="transparent", width=54, height=54)
        self._art_container.pack(side="left", padx=(0, 10), pady=12)
        self._art_container.pack_propagate(False)

        self._art_glow = ctk.CTkFrame(
            self._art_container,
            fg_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            corner_radius=12, width=54, height=54,
        )
        self._art_glow.place(relx=0.5, rely=0.5, anchor="center")
        self._art_glow.lower()

        self._art_frame = ctk.CTkFrame(self._art_container, fg_color="transparent", width=50, height=50)
        self._art_frame.place(relx=0.5, rely=0.5, anchor="center")
        self._art_frame.pack_propagate(False)

        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent", width=220)
        info_frame.pack(side="left")
        info_frame.pack_propagate(False)

        self._title_label = ctk.CTkLabel(
            info_frame,
            text="No song playing",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD, "bold"),
            anchor="w",
        )
        self._title_label.pack(fill="x", anchor="w", pady=(0, 1))

        self._artist_label = ctk.CTkLabel(
            info_frame,
            text="",
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="w",
        )
        self._artist_label.pack(fill="x", anchor="w")

        # Click to expand
        for w in [left_frame, info_frame, self._title_label, self._artist_label]:
            w.configure(cursor="hand2")
            w.bind("<Button-1>", self._handle_expand)

        # ── Center: Controls + Progress ──────────────────────────
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=1, sticky="nsew", padx=20)

        # Controls row
        controls = ctk.CTkFrame(center_frame, fg_color="transparent")
        controls.pack(pady=(8, 2))

        self._shuffle_btn = ctk.CTkButton(
            controls, text="🔀", width=32, height=32,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, 13), corner_radius=16,
            command=self._toggle_shuffle,
        )
        self._shuffle_btn.pack(side="left", padx=4)

        self._prev_btn = ctk.CTkButton(
            controls, text="⏮", width=36, height=36,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 16), corner_radius=18,
            command=player.previous,
        )
        self._prev_btn.pack(side="left", padx=2)

        self._play_btn = ctk.CTkButton(
            controls, text="▶", width=40, height=40,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_LIGHT,
            text_color="white",
            font=(Theme.FONT_FAMILY, 18), corner_radius=20,
            command=player.toggle_play_pause,
        )
        self._play_btn.pack(side="left", padx=4)

        self._next_btn = ctk.CTkButton(
            controls, text="⏭", width=36, height=36,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 16), corner_radius=18,
            command=player.next,
        )
        self._next_btn.pack(side="left", padx=2)

        self._repeat_btn = ctk.CTkButton(
            controls, text="🔁", width=32, height=32,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, 13), corner_radius=16,
            command=self._cycle_repeat,
        )
        self._repeat_btn.pack(side="left", padx=4)

        # Progress row
        progress_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=8, pady=(0, 8))

        self._elapsed_label = ctk.CTkLabel(
            progress_frame, text="--:--",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XS),
            width=40,
        )
        self._elapsed_label.pack(side="left")

        self._progress_slider = ctk.CTkSlider(
            progress_frame,
            from_=0, to=100, number_of_steps=1000,
            height=4,
            fg_color=Theme.with_alpha(Theme.PRIMARY, 0.2),
            progress_color=Theme.PRIMARY,
            button_color="white",
            button_hover_color=Theme.PRIMARY_LIGHT,
            button_length=10,
            command=self._on_seek,
        )
        self._progress_slider.set(0)
        self._progress_slider.pack(side="left", fill="x", expand=True, padx=6)
        self._progress_slider.bind("<ButtonPress-1>", lambda e: setattr(self, '_updating_slider', True))
        self._progress_slider.bind("<ButtonRelease-1>", self._on_slider_release)

        self._total_label = ctk.CTkLabel(
            progress_frame, text="--:--",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XS),
            width=40,
        )
        self._total_label.pack(side="right")

        # ── Right: Volume ────────────────────────────────────────
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="nse", padx=(0, 16))

        vol_icon = ctk.CTkLabel(
            right_frame, text="🔊",
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_SECONDARY,
        )
        vol_icon.pack(side="left", padx=(0, 4), pady=28)

        self._volume_slider = ctk.CTkSlider(
            right_frame,
            from_=0, to=1, number_of_steps=100,
            width=100, height=4,
            fg_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            progress_color=Theme.with_alpha(Theme.PRIMARY, 0.6),
            button_color=Theme.PRIMARY,
            button_hover_color=Theme.PRIMARY_LIGHT,
            button_length=8,
            command=self._on_volume,
        )
        self._volume_slider.set(player.volume)
        self._volume_slider.pack(side="left", pady=28)

    # ── Handlers ─────────────────────────────────────────────────
    def _handle_expand(self, event=None):
        if self._on_expand:
            self._on_expand()

    def _toggle_shuffle(self):
        self._player.toggle_shuffle()
        self._update_control_states()

    def _cycle_repeat(self):
        self._player.cycle_repeat()
        self._update_control_states()

    def _on_seek(self, value):
        self._updating_slider = True

    def _on_slider_release(self, event):
        value = self._progress_slider.get()
        duration = self._player.duration_ms / 1000.0
        if duration > 0:
            self._player.seek((value / 100.0) * duration)
        self._updating_slider = False

    def _on_volume(self, value):
        self._player.set_volume(value)

    def _format_time(self, ms: int) -> str:
        total = ms // 1000
        return f"{total // 60:02d}:{total % 60:02d}"

    def _update_control_states(self):
        """Update shuffle/repeat button visual states."""
        from ..audio_player import RepeatMode

        if self._player.shuffle_enabled:
            self._shuffle_btn.configure(text_color=Theme.PRIMARY_LIGHT)
        else:
            self._shuffle_btn.configure(text_color=Theme.TEXT_HINT)

        mode = self._player.repeat_mode
        if mode == RepeatMode.OFF:
            self._repeat_btn.configure(text="🔁", text_color=Theme.TEXT_HINT)
        elif mode == RepeatMode.ALL:
            self._repeat_btn.configure(text="🔁", text_color=Theme.PRIMARY_LIGHT)
        elif mode == RepeatMode.ONE:
            self._repeat_btn.configure(text="🔂", text_color=Theme.PRIMARY_LIGHT)

    def _update_album_art(self, song):
        """Update album art only when the song actually changes."""
        song_id = song.id if song else None
        if song_id == self._current_song_id:
            return
        self._current_song_id = song_id

        # Destroy old art widget
        for widget in self._art_frame.winfo_children():
            widget.destroy()

        if song:
            self._art_widget = AlbumArt(
                self._art_frame,
                art_data=song.album_art_data,
                size=46,
                title=song.title,
                corner_radius=8,
            )
            self._art_widget.pack(expand=True)
            self._art_widget.configure(cursor="hand2")
            self._art_widget.bind("<Button-1>", self._handle_expand)
            # Show glow when playing
            self._art_glow.configure(fg_color=Theme.with_alpha(Theme.PRIMARY, 0.20))
        else:
            self._art_widget = None
            self._art_glow.configure(fg_color="transparent")

    def update_display(self):
        """Update everything to reflect current playback state."""
        song = self._player.current_song

        if song is None:
            self._title_label.configure(text="No song playing")
            self._artist_label.configure(text="")
            self._play_btn.configure(text="▶")
            self._elapsed_label.configure(text="--:--")
            self._total_label.configure(text="--:--")
            self._progress_slider.set(0)
            self._update_album_art(None)
            return

        # Truncate long titles
        title = song.title if len(song.title) <= 35 else song.title[:32] + "…"
        artist = song.artist if len(song.artist) <= 40 else song.artist[:37] + "…"
        self._title_label.configure(text=title)
        self._artist_label.configure(text=artist)

        # Play/Pause
        self._play_btn.configure(text="⏸" if self._player.is_playing else "▶")

        # Progress
        pos = self._player.position_ms
        dur = self._player.duration_ms
        self._elapsed_label.configure(text=self._format_time(pos))
        self._total_label.configure(text=self._format_time(dur))

        if not self._updating_slider and dur > 0:
            self._progress_slider.set((pos / dur) * 100)

        self._update_control_states()

        # Update album art only when song changes
        self._update_album_art(song)
