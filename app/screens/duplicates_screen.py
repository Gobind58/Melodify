"""
Duplicates Screen — shows grouped duplicate songs with selection & deletion UI.
"""
import os
from typing import List, Callable, Optional, Set

import customtkinter as ctk

from ..theme import Theme
from ..models import Song
from ..duplicate_scanner import DuplicateGroup, find_duplicates, get_file_size_str


class DuplicatesScreen(ctk.CTkFrame):
    """Screen for discovering and managing duplicate songs."""

    def __init__(
        self,
        master,
        songs: List[Song],
        on_delete: Optional[Callable[[List[str]], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=Theme.BACKGROUND, corner_radius=0, **kwargs)

        self._songs = songs
        self._on_delete = on_delete
        self._selected_paths: Set[str] = set()
        self._groups: List[DuplicateGroup] = []
        self._checkboxes: dict = {}  # path -> CTkCheckBox
        self._checkbox_vars: dict = {}  # path -> BooleanVar

        # ── Header ───────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 0))

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")

        title = ctk.CTkLabel(
            title_row,
            text="🔄  Duplicate Finder",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_TITLE, "bold"),
            anchor="w",
        )
        title.pack(side="left", fill="x", expand=True)

        # Action buttons
        self._actions = ctk.CTkFrame(title_row, fg_color="transparent")
        self._actions.pack(side="right")

        self._select_all_btn = ctk.CTkButton(
            self._actions, text="⚡ Select All Duplicates",
            width=160, height=34,
            fg_color=Theme.SURFACE_CARD,
            hover_color=Theme.with_alpha(Theme.DUPLICATE_WARN, 0.2),
            text_color=Theme.DUPLICATE_WARN,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            corner_radius=17,
            border_color=Theme.with_alpha(Theme.DUPLICATE_WARN, 0.3),
            border_width=1,
            command=self._select_all_duplicates,
        )

        self._delete_btn = ctk.CTkButton(
            self._actions, text="🗑 Delete Selected (0)",
            width=150, height=34,
            fg_color=Theme.SURFACE_CARD,
            hover_color=Theme.with_alpha(Theme.DANGER, 0.2),
            text_color=Theme.DANGER,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            corner_radius=17,
            border_color=Theme.with_alpha(Theme.DANGER, 0.3),
            border_width=1,
            command=self._delete_selected,
        )

        self._subtitle = ctk.CTkLabel(
            header,
            text="Scanning for duplicates…",
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="w",
        )
        self._subtitle.pack(fill="x", pady=(4, 0))

        # ── Content ──────────────────────────────────────────────
        self._content_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._content_frame.pack(fill="both", expand=True)

        self._build_content()

    def _build_content(self):
        """Scan for duplicates and build the UI."""
        for widget in self._content_frame.winfo_children():
            widget.destroy()

        self._groups = find_duplicates(self._songs)
        self._selected_paths.clear()
        self._checkboxes.clear()
        self._checkbox_vars.clear()

        if not self._groups:
            self._build_empty()
            self._subtitle.configure(text="No duplicates found in your library")
            self._select_all_btn.pack_forget()
            self._delete_btn.pack_forget()
            return

        total_dupes = sum(g.count - 1 for g in self._groups)
        self._subtitle.configure(
            text=f"Found {len(self._groups)} groups with {total_dupes} duplicate files"
        )

        # Show action buttons
        self._select_all_btn.pack(side="left", padx=4)
        self._delete_btn.pack(side="left", padx=4)

        # Scrollable area
        scroll = ctk.CTkScrollableFrame(
            self._content_frame,
            fg_color="transparent",
            scrollbar_button_color=Theme.with_alpha(Theme.PRIMARY, 0.3),
            scrollbar_button_hover_color=Theme.PRIMARY,
        )
        scroll.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        for group in self._groups:
            self._build_group_card(scroll, group)

    def _build_empty(self):
        """Show empty state when no duplicates found."""
        empty = ctk.CTkFrame(self._content_frame, fg_color="transparent")
        empty.pack(expand=True)

        icon = ctk.CTkLabel(
            empty, text="✅",
            font=(Theme.FONT_FAMILY, 64),
            text_color=Theme.SUCCESS,
        )
        icon.pack(pady=(60, 10))

        title = ctk.CTkLabel(
            empty,
            text="No duplicates found!",
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XL, "bold"),
        )
        title.pack(pady=(0, 8))

        subtitle = ctk.CTkLabel(
            empty,
            text="Your music library is clean — no duplicate songs detected.",
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
        )
        subtitle.pack()

    def _build_group_card(self, parent, group: DuplicateGroup):
        """Build a card showing a group of duplicate songs."""
        card = ctk.CTkFrame(
            parent,
            fg_color=Theme.SURFACE_CARD,
            corner_radius=12,
            border_color=Theme.DIVIDER,
            border_width=1,
        )
        card.pack(fill="x", padx=8, pady=6)

        # Group header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))

        # Badge showing count
        badge = ctk.CTkFrame(
            header,
            fg_color=Theme.with_alpha(Theme.DUPLICATE_WARN, 0.15),
            corner_radius=10,
            width=60, height=22,
        )
        badge.pack(side="left", padx=(0, 10))
        badge.pack_propagate(False)

        ctk.CTkLabel(
            badge,
            text=f"{group.count} copies",
            text_color=Theme.DUPLICATE_WARN,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XS, "bold"),
        ).pack(expand=True)

        ctk.CTkLabel(
            header,
            text=group.title_display,
            text_color=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MD, "bold"),
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            header,
            text=group.artist_display,
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="e",
        ).pack(side="right")

        # Song entries
        for song in group.songs:
            is_recommended = song == group.recommended_keep
            self._build_song_entry(card, song, is_recommended)

        # Bottom padding
        ctk.CTkFrame(card, fg_color="transparent", height=4).pack()

    def _build_song_entry(self, parent, song: Song, is_recommended: bool):
        """Build a single song entry within a duplicate group."""
        entry = ctk.CTkFrame(
            parent,
            fg_color=Theme.with_alpha(Theme.SUCCESS, 0.05) if is_recommended else "transparent",
            corner_radius=8,
            height=44,
        )
        entry.pack(fill="x", padx=12, pady=2)
        entry.pack_propagate(False)

        # Checkbox
        var = ctk.BooleanVar(value=False)
        self._checkbox_vars[song.path] = var

        cb = ctk.CTkCheckBox(
            entry,
            text="",
            variable=var,
            width=24, height=24,
            checkbox_width=18, checkbox_height=18,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_LIGHT,
            border_color=Theme.TEXT_HINT,
            corner_radius=4,
            command=lambda p=song.path: self._on_checkbox_toggle(p),
        )
        cb.pack(side="left", padx=(12, 8), pady=10)
        self._checkboxes[song.path] = cb

        # Keep badge
        if is_recommended:
            keep_badge = ctk.CTkFrame(
                entry,
                fg_color=Theme.with_alpha(Theme.SUCCESS, 0.15),
                corner_radius=8,
                width=44, height=20,
            )
            keep_badge.pack(side="left", padx=(0, 8))
            keep_badge.pack_propagate(False)

            ctk.CTkLabel(
                keep_badge,
                text="KEEP",
                text_color=Theme.SUCCESS,
                font=(Theme.FONT_FAMILY, 9, "bold"),
            ).pack(expand=True)

        # File path (shortened)
        path_display = self._shorten_path(song.path)
        ctk.CTkLabel(
            entry,
            text=path_display,
            text_color=Theme.TEXT_SECONDARY if not is_recommended else Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        # File size
        size_str = get_file_size_str(song.path)
        ctk.CTkLabel(
            entry,
            text=size_str,
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XS),
            width=60,
        ).pack(side="right", padx=(0, 8))

        # Duration
        ctk.CTkLabel(
            entry,
            text=song.duration_formatted,
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XS),
            width=40,
        ).pack(side="right", padx=(0, 4))

        # Art indicator
        art_text = "🖼" if song.album_art_data else "—"
        ctk.CTkLabel(
            entry,
            text=art_text,
            text_color=Theme.TEXT_HINT,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XS),
            width=20,
        ).pack(side="right", padx=(0, 8))

    def _shorten_path(self, path: str, max_len: int = 60) -> str:
        """Shorten a file path for display."""
        if len(path) <= max_len:
            return path
        parts = path.split(os.sep)
        if len(parts) <= 3:
            return path
        return os.sep.join(parts[:2]) + os.sep + "…" + os.sep + os.sep.join(parts[-2:])

    def _on_checkbox_toggle(self, path: str):
        """Handle checkbox toggle."""
        var = self._checkbox_vars.get(path)
        if var:
            if var.get():
                self._selected_paths.add(path)
            else:
                self._selected_paths.discard(path)
        self._update_delete_button()

    def _select_all_duplicates(self):
        """Select all non-recommended duplicates."""
        self._selected_paths.clear()
        for group in self._groups:
            for song in group.songs:
                if song != group.recommended_keep:
                    self._selected_paths.add(song.path)
                    var = self._checkbox_vars.get(song.path)
                    if var:
                        var.set(True)
                else:
                    var = self._checkbox_vars.get(song.path)
                    if var:
                        var.set(False)
        self._update_delete_button()

    def _update_delete_button(self):
        """Update the delete button text with selection count."""
        count = len(self._selected_paths)
        self._delete_btn.configure(text=f"🗑 Delete Selected ({count})")
        if count > 0:
            self._delete_btn.configure(
                fg_color=Theme.with_alpha(Theme.DANGER, 0.15),
                text_color=Theme.DANGER,
            )
        else:
            self._delete_btn.configure(
                fg_color=Theme.SURFACE_CARD,
                text_color=Theme.DANGER,
            )

    def _delete_selected(self):
        """Delete selected files after confirmation."""
        if not self._selected_paths:
            return

        count = len(self._selected_paths)

        # Confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Deletion")
        dialog.geometry("420x200")
        dialog.configure(fg_color=Theme.SURFACE)
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - 420) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - 200) // 2
        dialog.geometry(f"+{x}+{y}")

        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            content,
            text="⚠️  Confirm Deletion",
            text_color=Theme.DUPLICATE_WARN,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LG, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            content,
            text=f"Are you sure you want to permanently delete {count} file{'s' if count > 1 else ''}?\nThis action cannot be undone.",
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            anchor="w", justify="left",
        ).pack(fill="x", pady=(8, 16))

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")

        def confirm():
            dialog.destroy()
            paths = list(self._selected_paths)
            if self._on_delete:
                self._on_delete(paths)

        ctk.CTkButton(
            btn_frame, text="Cancel", width=100, height=36,
            fg_color=Theme.SURFACE_CARD,
            hover_color=Theme.CARD_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM),
            corner_radius=18,
            border_color=Theme.DIVIDER, border_width=1,
            command=dialog.destroy,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text=f"Delete {count} Files", width=140, height=36,
            fg_color=Theme.DANGER,
            hover_color="#C04040",
            text_color="white",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SM, "bold"),
            corner_radius=18,
            command=confirm,
        ).pack(side="left")

    def refresh(self):
        """Rebuild duplicate list."""
        self._build_content()

    def update_songs(self, songs: List[Song]):
        """Update the song list and rescan."""
        self._songs = songs
        self._build_content()
