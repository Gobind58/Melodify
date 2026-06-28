"""
Melodify Theme — color palette, fonts, and style constants.
Ported from the Flutter AppTheme to match the exact same aesthetic.
Optimized for desktop layout.
"""


class Theme:
    """Centralized design tokens for the entire app."""

    # ── Color Palette ────────────────────────────────────────────────
    BACKGROUND      = "#0A0A0F"
    SURFACE         = "#12121C"
    SURFACE_CARD    = "#1A1A28"
    PRIMARY         = "#7C5CBF"
    PRIMARY_LIGHT   = "#9D7FE0"
    ACCENT          = "#BF5CA0"
    ACCENT_GLOW     = "#7C2D7E"
    TEXT_PRIMARY    = "#EFEFFF"
    TEXT_SECONDARY  = "#9090B8"
    TEXT_HINT       = "#555580"
    DIVIDER         = "#252540"
    MINI_PLAYER_BG  = "#16162A"
    SIDEBAR_BG      = "#0E0E18"
    SIDEBAR_HOVER   = "#1A1A30"
    SIDEBAR_ACTIVE  = "#201840"
    SUCCESS         = "#6FCF97"
    DANGER          = "#EB5757"

    # ── Gradient stops (for canvas-based gradients) ──────────────────
    GRADIENT_PRIMARY = ("#7C5CBF", "#BF5CA0")
    GRADIENT_PLAYER  = ("#1E1040", "#0A0A14")
    GRADIENT_BG      = ("#0D0D1A", "#0A0A12")
    GRADIENT_GLOW    = ("#5E3A9A", "#9A3A7C")

    # ── Genre card gradients ─────────────────────────────────────────
    GENRE_COLORS = {
        "Pop":        ("#7C5CBF", "#BF5CA0"),
        "Hip Hop":    ("#1A1A2E", "#4A2080"),
        "Rock":       ("#7B0000", "#EB5757"),
        "Chill":      ("#0F2027", "#203A43"),
        "Electronic": ("#00B09B", "#2E6B5E"),
        "Workout":    ("#F7971E", "#BF5F1A"),
        "Classical":  ("#3A7BD5", "#5B4FE0"),
        "Jazz":       ("#56CCF2", "#2F80ED"),
    }

    # ── Album art fallback gradients ─────────────────────────────────
    ART_GRADIENTS = [
        ("#7C5CBF", "#BF5CA0"),
        ("#3A7BD5", "#5B4FE0"),
        ("#00B09B", "#2E6B5E"),
        ("#FF6B6B", "#AA3366"),
        ("#F7971E", "#BF5F1A"),
        ("#56CCF2", "#2F80ED"),
        ("#6FCF97", "#219653"),
        ("#EB5757", "#7B0000"),
    ]

    # ── Fonts ────────────────────────────────────────────────────────
    FONT_FAMILY     = "Segoe UI"
    FONT_SIZE_XS    = 11
    FONT_SIZE_SM    = 12
    FONT_SIZE_MD    = 14
    FONT_SIZE_LG    = 16
    FONT_SIZE_XL    = 20
    FONT_SIZE_XXL   = 22
    FONT_SIZE_TITLE = 28

    # ── Desktop Dimensions ───────────────────────────────────────────
    WINDOW_WIDTH    = 1100
    WINDOW_HEIGHT   = 700
    MIN_WIDTH       = 800
    MIN_HEIGHT      = 500
    SIDEBAR_WIDTH   = 230
    CORNER_RADIUS   = 12
    BOTTOM_BAR_H    = 80
    SONG_TILE_H     = 64
    ART_SIZE_SM     = 44
    ART_SIZE_MD     = 52
    ART_SIZE_LG     = 300

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """Convert hex color string to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def lerp_color(c1: str, c2: str, t: float) -> str:
        """Linearly interpolate between two hex colors."""
        r1, g1, b1 = Theme.hex_to_rgb(c1)
        r2, g2, b2 = Theme.hex_to_rgb(c2)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def with_alpha(hex_color: str, alpha: float) -> str:
        """Blend a hex color with the background at the given alpha.
        Since tkinter doesn't support true alpha, we simulate it."""
        bg = Theme.hex_to_rgb(Theme.BACKGROUND)
        fg = Theme.hex_to_rgb(hex_color)
        r = int(bg[0] + (fg[0] - bg[0]) * alpha)
        g = int(bg[1] + (fg[1] - bg[1]) * alpha)
        b = int(bg[2] + (fg[2] - bg[2]) * alpha)
        return f"#{r:02x}{g:02x}{b:02x}"
