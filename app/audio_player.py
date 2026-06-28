"""
Audio Player — pygame.mixer wrapper with full playback controls.
Handles play, pause, seek, next, previous, shuffle, repeat, and volume.
"""
import random
from enum import Enum
from typing import List, Optional, Callable

import pygame

from .models import Song


class RepeatMode(Enum):
    OFF = "off"
    ALL = "all"
    ONE = "one"


class AudioPlayer:
    """Wraps pygame.mixer.music for full-featured audio playback."""

    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

        self._queue: List[Song] = []
        self._original_queue: List[Song] = []
        self._current_index: int = -1
        self._is_playing: bool = False
        self._is_paused: bool = False
        self._volume: float = 1.0
        self._shuffle: bool = False
        self._repeat: RepeatMode = RepeatMode.OFF
        self._seek_offset: float = 0.0

        # Callbacks
        self._on_song_change: Optional[Callable] = None
        self._on_playback_change: Optional[Callable] = None

        pygame.mixer.music.set_volume(self._volume)

    # ── Properties ───────────────────────────────────────────────────
    @property
    def queue(self) -> List[Song]:
        return self._queue

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def current_song(self) -> Optional[Song]:
        if 0 <= self._current_index < len(self._queue):
            return self._queue[self._current_index]
        return None

    @property
    def is_playing(self) -> bool:
        return self._is_playing and not self._is_paused

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def shuffle_enabled(self) -> bool:
        return self._shuffle

    @property
    def repeat_mode(self) -> RepeatMode:
        return self._repeat

    @property
    def volume(self) -> float:
        return self._volume

    @property
    def position_ms(self) -> int:
        """Current playback position in milliseconds."""
        if self._is_playing or self._is_paused:
            pos = pygame.mixer.music.get_pos()
            if pos >= 0:
                return int(pos + self._seek_offset * 1000)
        return 0

    @property
    def duration_ms(self) -> int:
        """Duration of current song in milliseconds."""
        song = self.current_song
        return song.duration_ms if song else 0

    # ── Callbacks ────────────────────────────────────────────────────
    def set_on_song_change(self, callback: Callable):
        self._on_song_change = callback

    def set_on_playback_change(self, callback: Callable):
        self._on_playback_change = callback

    def _notify_song_change(self):
        if self._on_song_change:
            self._on_song_change()

    def _notify_playback_change(self):
        if self._on_playback_change:
            self._on_playback_change()

    # ── Load & Play ──────────────────────────────────────────────────
    def load_queue(self, songs: List[Song], start_index: int = 0):
        """Load a list of songs as the playback queue."""
        self._original_queue = list(songs)
        self._queue = list(songs)

        if self._shuffle:
            current = self._queue[start_index] if 0 <= start_index < len(self._queue) else None
            random.shuffle(self._queue)
            if current:
                self._queue.remove(current)
                self._queue.insert(0, current)
                start_index = 0

        self._play_at(start_index)

    def _play_at(self, index: int):
        """Play the song at the given queue index."""
        if not self._queue or index < 0 or index >= len(self._queue):
            return

        self._current_index = index
        song = self._queue[index]
        self._seek_offset = 0.0

        try:
            pygame.mixer.music.load(song.path)
            pygame.mixer.music.play()
            self._is_playing = True
            self._is_paused = False
            self._notify_song_change()
            self._notify_playback_change()
        except Exception as e:
            print(f"Error playing {song.path}: {e}")
            # Try to skip to next
            self._auto_next()

    def play(self):
        """Resume playback."""
        if self._is_paused:
            pygame.mixer.music.unpause()
            self._is_paused = False
            self._is_playing = True
            self._notify_playback_change()
        elif not self._is_playing and self.current_song:
            self._play_at(self._current_index)

    def pause(self):
        """Pause playback."""
        if self._is_playing and not self._is_paused:
            pygame.mixer.music.pause()
            self._is_paused = True
            self._notify_playback_change()

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def stop(self):
        """Stop playback."""
        pygame.mixer.music.stop()
        self._is_playing = False
        self._is_paused = False
        self._seek_offset = 0.0
        self._notify_playback_change()

    # ── Navigation ───────────────────────────────────────────────────
    def next(self):
        """Skip to next track."""
        if not self._queue:
            return
        next_index = self._current_index + 1

        if next_index >= len(self._queue):
            if self._repeat == RepeatMode.ALL:
                next_index = 0
            else:
                self.stop()
                return

        self._play_at(next_index)

    def previous(self):
        """Skip to previous track (or restart current if > 3s in)."""
        if not self._queue:
            return

        # If more than 3 seconds in, restart current song
        if self.position_ms > 3000:
            self.seek(0)
            return

        prev_index = self._current_index - 1
        if prev_index < 0:
            if self._repeat == RepeatMode.ALL:
                prev_index = len(self._queue) - 1
            else:
                prev_index = 0

        self._play_at(prev_index)

    def play_at_index(self, index: int):
        """Play a specific song by queue index."""
        self._play_at(index)

    def _auto_next(self):
        """Auto-advance logic when a song ends."""
        if self._repeat == RepeatMode.ONE:
            self._play_at(self._current_index)
        else:
            self.next()

    # ── Seek ─────────────────────────────────────────────────────────
    def seek(self, position_seconds: float):
        """Seek to a position in seconds."""
        if self.current_song:
            try:
                self._seek_offset = position_seconds
                pygame.mixer.music.play(start=position_seconds)
                if self._is_paused:
                    pygame.mixer.music.pause()
            except Exception:
                pass

    # ── Volume ───────────────────────────────────────────────────────
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._volume)

    # ── Shuffle ──────────────────────────────────────────────────────
    def toggle_shuffle(self):
        """Toggle shuffle mode."""
        self._shuffle = not self._shuffle
        current_song = self.current_song

        if self._shuffle:
            # Shuffle the queue but keep current song at current position
            remaining = [s for s in self._queue if s != current_song]
            random.shuffle(remaining)
            if current_song:
                self._queue = [current_song] + remaining
                self._current_index = 0
            else:
                self._queue = remaining
        else:
            # Restore original order
            self._queue = list(self._original_queue)
            if current_song:
                try:
                    self._current_index = self._queue.index(current_song)
                except ValueError:
                    pass

        self._notify_playback_change()

    # ── Repeat ───────────────────────────────────────────────────────
    def cycle_repeat(self):
        """Cycle through repeat modes: OFF → ALL → ONE → OFF."""
        if self._repeat == RepeatMode.OFF:
            self._repeat = RepeatMode.ALL
        elif self._repeat == RepeatMode.ALL:
            self._repeat = RepeatMode.ONE
        else:
            self._repeat = RepeatMode.OFF
        self._notify_playback_change()

    # ── Event handling ───────────────────────────────────────────────
    def check_events(self):
        """Check for pygame events (call from main loop)."""
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT + 1:
                # Song ended
                self._auto_next()

    def cleanup(self):
        """Clean up resources."""
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass
