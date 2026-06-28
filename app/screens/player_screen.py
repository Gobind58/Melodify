"""
Player Screen — full player with album art, progress, and controls.
Desktop-optimized: shows as content pane, no embedded mini player.
"""
from typing import Callable, Optional

import customtkinter as ctk

from ..theme import Theme
from ..audio_player import AudioPlayer, RepeatMode
from ..widgets.album_art import AlbumArt


class PlayerScreen(ctk.CTkFrame):
    """Full player view with large album art and playback controls."""

    def __init__(
        self,
        master,
        player: AudioPlayer,
        on_back: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="#140C28", corner_radius=0, **kwargs)

        self._player = player
        self._on_back = on_back
        self._updating_slider = False

        # ── Top Bar ──────────────────────────────────────────────
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=50)
        top_bar.pack(fill="x", padx=12, pady=(12, 0))
        top_bar.pack_propagate(False)

        back_btn = ctk.CTkButton(
            top_bar, text="← Back", width=80, height=36,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD),
            corner_radius=18,
            command=self._handle_back,
        )
        back_btn.pack(side="left")

        now_playing = ctk.CTkLabel(
            top_bar, text="NOW PLAYING",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XS, "bold"),
        )
        now_playing.pack(expand=True)

        spacer = ctk.CTkFrame(top_bar, fg_color="transparent", width=80)
        spacer.pack(side="right")

        # ── Main content — horizontal layout for desktop ─────────
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=32, pady=16)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Left: Album Art
        self._art_frame = ctk.CTkFrame(content, fg_color="transparent")
        self._art_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self._art_widget = None
        self._update_album_art()

        # Right: Info + Controls
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(20, 0))

        # Song Info
        info_frame = ctk.CTkFrame(right, fg_color="transparent")
        info_frame.pack(fill="x", pady=(40, 0))

        self._title_label = ctk.CTkLabel(
            info_frame, text="—",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 26, "bold"),
            anchor="w", wraplength=350,
        )
        self._title_label.pack(fill="x")

        self._artist_label = ctk.CTkLabel(
            info_frame, text="",
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LG),
            anchor="w",
        )
        self._artist_label.pack(fill="x", pady=(4, 0))

        self._album_label = ctk.CTkLabel(
            info_frame, text="",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD),
            anchor="w",
        )
        self._album_label.pack(fill="x", pady=(2, 0))

        # Progress
        progress_frame = ctk.CTkFrame(right, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(30, 0))

        self._progress_slider = ctk.CTkSlider(
            progress_frame,
            from_=0, to=100, number_of_steps=1000,
            height=6,
            fg_color=Theme.with_alpha(Theme.PRIMARY, 0.2),
            progress_color=Theme.PRIMARY,
            button_color="white",
            button_hover_color=Theme.PRIMARY_LIGHT,
            button_length=14,
            command=self._on_seek,
        )
        self._progress_slider.set(0)
        self._progress_slider.pack(fill="x", pady=(0, 6))
        self._progress_slider.bind("<ButtonPress-1>", lambda e: setattr(self, '_updating_slider', True))
        self._progress_slider.bind("<ButtonRelease-1>", self._on_slider_release)

        time_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        time_frame.pack(fill="x")

        self._elapsed_label = ctk.CTkLabel(
            time_frame, text="00:00",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM), anchor="w",
        )
        self._elapsed_label.pack(side="left")

        self._total_label = ctk.CTkLabel(
            time_frame, text="00:00",
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM), anchor="e",
        )
        self._total_label.pack(side="right")

        # Controls
        controls = ctk.CTkFrame(right, fg_color="transparent")
        controls.pack(pady=(24, 0))

        self._shuffle_btn = ctk.CTkButton(
            controls, text="🔀", width=44, height=44,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, 18), corner_radius=22,
            command=self._toggle_shuffle,
        )
        self._shuffle_btn.pack(side="left", padx=8)

        ctk.CTkButton(
            controls, text="⏮", width=48, height=48,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 22), corner_radius=24,
            command=player.previous,
        ).pack(side="left", padx=4)

        self._play_btn = ctk.CTkButton(
            controls, text="▶", width=64, height=64,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.ACCENT,
            text_color="white",
            font=(Theme.FONT_FAMILY, 28), corner_radius=32,
            command=player.toggle_play_pause,
        )
        self._play_btn.pack(side="left", padx=8)

        ctk.CTkButton(
            controls, text="⏭", width=48, height=48,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 22), corner_radius=24,
            command=player.next,
        ).pack(side="left", padx=4)

        self._repeat_btn = ctk.CTkButton(
            controls, text="🔁", width=44, height=44,
            fg_color="transparent",
            hover_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, 18), corner_radius=22,
            command=self._cycle_repeat,
        )
        self._repeat_btn.pack(side="left", padx=8)

        # Volume
        vol_frame = ctk.CTkFrame(right, fg_color="transparent")
        vol_frame.pack(fill="x", pady=(24, 0))

        ctk.CTkLabel(
            vol_frame, text="🔈",
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_SECONDARY,
        ).pack(side="left")

        self._volume_slider = ctk.CTkSlider(
            vol_frame,
            from_=0, to=1, number_of_steps=100,
            height=4,
            fg_color=Theme.with_alpha(Theme.PRIMARY, 0.15),
            progress_color=Theme.with_alpha(Theme.PRIMARY, 0.7),
            button_color=Theme.PRIMARY,
            button_hover_color=Theme.PRIMARY_LIGHT,
            button_length=10,
            command=lambda v: player.set_volume(v),
        )
        self._volume_slider.set(player.volume)
        self._volume_slider.pack(side="left", fill="x", expand=True, padx=8)

        ctk.CTkLabel(
            vol_frame, text="🔊",
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_SECONDARY,
        ).pack(side="right")

    def _handle_back(self):
        if self._on_back:
            self._on_back()

    def _update_album_art(self):
        for widget in self._art_frame.winfo_children():
            widget.destroy()

        song = self._player.current_song
        self._art_widget = AlbumArt(
            self._art_frame,
            art_data=song.album_art_data if song else None,
            size=Theme.ART_SIZE_LG,
            title=song.title if song else "",
            corner_radius=20,
        )
        self._art_widget.pack(expand=True)

    def _on_seek(self, value):
        self._updating_slider = True

    def _on_slider_release(self, event):
        value = self._progress_slider.get()
        duration = self._player.duration_ms / 1000.0
        if duration > 0:
            self._player.seek((value / 100.0) * duration)
        self._updating_slider = False

    def _toggle_shuffle(self):
        self._player.toggle_shuffle()
        self._update_controls()

    def _cycle_repeat(self):
        self._player.cycle_repeat()
        self._update_controls()

    def _update_controls(self):
        self._shuffle_btn.configure(
            text_color=Theme.PRIMARY_LIGHT if self._player.shuffle_enabled else Theme.TEXT_SECONDARY
        )

        mode = self._player.repeat_mode
        if mode == RepeatMode.OFF:
            self._repeat_btn.configure(text="🔁", text_color=Theme.TEXT_SECONDARY)
        elif mode == RepeatMode.ALL:
            self._repeat_btn.configure(text="🔁", text_color=Theme.PRIMARY_LIGHT)
        elif mode == RepeatMode.ONE:
            self._repeat_btn.configure(text="🔂", text_color=Theme.PRIMARY_LIGHT)

        self._play_btn.configure(text="⏸" if self._player.is_playing else "▶")

    def _format_time(self, ms: int) -> str:
        total = ms // 1000
        return f"{total // 60:02d}:{total % 60:02d}"

    def refresh(self):
        song = self._player.current_song
        if song:
            self._title_label.configure(text=song.title)
            self._artist_label.configure(text=song.artist)
            self._album_label.configure(text=song.album)

            pos = self._player.position_ms
            dur = self._player.duration_ms
            self._elapsed_label.configure(text=self._format_time(pos))
            self._total_label.configure(text=self._format_time(dur))

            if not self._updating_slider and dur > 0:
                self._progress_slider.set((pos / dur) * 100)

        self._update_controls()

    def on_song_changed(self):
        self._update_album_art()
        self.refresh()
