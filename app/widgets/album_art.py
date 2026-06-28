"""
Album Art Widget — displays embedded album art or a stylish gradient fallback.
"""
import io
from typing import Optional

import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont

from ..theme import Theme


class AlbumArt(ctk.CTkLabel):
    """Displays album art with a gradient letter fallback."""

    # Cache for generated images to avoid re-creating
    _cache: dict = {}

    def __init__(
        self,
        master,
        art_data: Optional[bytes],
        size: int = 48,
        title: str = "",
        corner_radius: int = 10,
        **kwargs,
    ):
        self._size = size
        self._corner_radius = corner_radius

        # Generate the image
        photo = self._create_image(art_data, size, title, corner_radius)

        super().__init__(
            master,
            image=photo,
            text="",
            width=size,
            height=size,
            fg_color="transparent",
            **kwargs,
        )
        # Keep a reference to prevent garbage collection
        self._photo = photo

    def _create_image(
        self,
        art_data: Optional[bytes],
        size: int,
        title: str,
        corner_radius: int,
    ) -> ctk.CTkImage:
        """Create the display image — either from embedded data or gradient fallback."""
        if art_data:
            try:
                img = Image.open(io.BytesIO(art_data))
                img = img.convert("RGB")
                img = img.resize((size * 2, size * 2), Image.LANCZOS)
                img = self._round_corners(img, corner_radius * 2)
                return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
            except Exception:
                pass

        # Fallback: gradient with initial letter
        img = self._create_fallback(size * 2, title, corner_radius * 2)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))

    def _create_fallback(self, size: int, title: str, corner_radius: int) -> Image.Image:
        """Create a gradient image with the first letter of the title."""
        # Pick gradient based on title hash
        idx = abs(hash(title)) % len(Theme.ART_GRADIENTS)
        color1, color2 = Theme.ART_GRADIENTS[idx]
        rgb1 = Theme.hex_to_rgb(color1)
        rgb2 = Theme.hex_to_rgb(color2)

        # Create gradient
        img = Image.new("RGB", (size, size))
        pixels = img.load()
        for y in range(size):
            for x in range(size):
                t = (x + y) / (2 * size)
                r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * t)
                g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * t)
                b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * t)
                pixels[x, y] = (r, g, b)

        # Draw initial letter
        draw = ImageDraw.Draw(img)
        initial = title[0].upper() if title else "♪"
        font_size = int(size * 0.38)

        try:
            font = ImageFont.truetype("segoeui.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()

        # Center the text
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) // 2
        y = (size - text_h) // 2 - bbox[1]
        draw.text((x, y), initial, fill="white", font=font)

        # Round corners
        img = self._round_corners(img, corner_radius)
        return img

    @staticmethod
    def _round_corners(img: Image.Image, radius: int) -> Image.Image:
        """Apply rounded corners to an image."""
        if radius <= 0:
            return img

        # Create a mask with rounded rectangle
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle(
            [(0, 0), (img.size[0] - 1, img.size[1] - 1)],
            radius=radius,
            fill=255,
        )

        # Apply mask
        result = img.copy()
        # Create a background matching our theme
        bg = Image.new("RGB", img.size, Theme.hex_to_rgb(Theme.BACKGROUND))
        result = Image.composite(result, bg, mask)
        return result


def create_album_art_image(
    art_data: Optional[bytes],
    size: int,
    title: str = "",
    corner_radius: int = 10,
) -> ctk.CTkImage:
    """Utility function to create a CTkImage for album art without creating a widget."""
    widget = AlbumArt.__new__(AlbumArt)
    return widget._create_image(art_data, size, title, corner_radius)
