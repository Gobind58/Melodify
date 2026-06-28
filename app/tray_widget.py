"""
System Tray Widget — pystray integration for Windows taskbar controls.
Allows controlling playback from the system tray without opening the window.
"""
import threading
from typing import Callable, Optional

from PIL import Image, ImageDraw, ImageFont

from .theme import Theme
from .audio_player import AudioPlayer, RepeatMode


class TrayWidget:
    """System tray icon with playback controls and window management."""

    def __init__(
        self,
        player: AudioPlayer,
        on_show: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
    ):
        self._player = player
        self._on_show = on_show
        self._on_quit = on_quit
        self._icon = None
        self._thread = None

    def start(self):
        """Start the tray icon in a background thread."""
        try:
            import pystray
            from pystray import MenuItem, Menu
        except ImportError:
            print("pystray not installed, skipping system tray")
            return

        self._thread = threading.Thread(target=self._run_tray, daemon=True)
        self._thread.start()

    def _run_tray(self):
        """Run the tray icon (blocking, runs in its own thread)."""
        import pystray
        from pystray import MenuItem, Menu

        icon_image = self._create_icon()

        menu = Menu(
            MenuItem("Now Playing", None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("⏯  Play / Pause", self._toggle_play),
            MenuItem("⏭  Next Track", self._next_track),
            MenuItem("⏮  Previous Track", self._prev_track),
            Menu.SEPARATOR,
            MenuItem("🔀  Shuffle", self._toggle_shuffle, checked=lambda item: self._player.shuffle_enabled),
            MenuItem(
                "🔁  Repeat",
                Menu(
                    MenuItem("Off", lambda: self._set_repeat(RepeatMode.OFF),
                             checked=lambda item: self._player.repeat_mode == RepeatMode.OFF),
                    MenuItem("All", lambda: self._set_repeat(RepeatMode.ALL),
                             checked=lambda item: self._player.repeat_mode == RepeatMode.ALL),
                    MenuItem("One", lambda: self._set_repeat(RepeatMode.ONE),
                             checked=lambda item: self._player.repeat_mode == RepeatMode.ONE),
                ),
            ),
            Menu.SEPARATOR,
            MenuItem("🎵  Show Melodify", self._show_window),
            MenuItem("❌  Quit", self._quit),
        )

        self._icon = pystray.Icon(
            "melodify",
            icon_image,
            "Melodify",
            menu,
        )

        self._icon.run()

    def _create_icon(self) -> Image.Image:
        """Create a simple Melodify icon for the system tray."""
        size = 64
        img = Image.new("RGB", (size, size))
        pixels = img.load()

        # Create gradient background
        c1 = Theme.hex_to_rgb(Theme.PRIMARY)
        c2 = Theme.hex_to_rgb(Theme.ACCENT)

        for y in range(size):
            for x in range(size):
                t = (x + y) / (2 * size)
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                pixels[x, y] = (r, g, b)

        # Draw a music note
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("segoeui.ttf", 36)
        except (OSError, IOError):
            font = ImageFont.load_default()

        draw.text((16, 10), "♪", fill="white", font=font)

        # Round to a circle
        mask = Image.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size - 1, size - 1), fill=255)

        bg = Image.new("RGB", (size, size), (0, 0, 0))
        result = Image.composite(img, bg, mask)

        # Add alpha channel
        result = result.convert("RGBA")
        alpha = mask.copy()
        result.putalpha(alpha)

        return result

    def update_tooltip(self):
        """Update the tray icon tooltip with current song info."""
        if self._icon is None:
            return

        song = self._player.current_song
        if song:
            self._icon.title = f"Melodify — {song.title} - {song.artist}"
        else:
            self._icon.title = "Melodify"

    # ── Actions ──────────────────────────────────────────────────
    def _toggle_play(self):
        self._player.toggle_play_pause()

    def _next_track(self):
        self._player.next()

    def _prev_track(self):
        self._player.previous()

    def _toggle_shuffle(self):
        self._player.toggle_shuffle()

    def _set_repeat(self, mode: RepeatMode):
        while self._player.repeat_mode != mode:
            self._player.cycle_repeat()

    def _show_window(self):
        if self._on_show:
            self._on_show()

    def _quit(self):
        if self._icon:
            self._icon.stop()
        if self._on_quit:
            self._on_quit()

    def stop(self):
        """Stop the tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
