import os
import random
import sys
from datetime import date

from PyQt6.QtCore import (Qt, QTimer, QPointF, QPropertyAnimation, QSequentialAnimationGroup, QPauseAnimation, QEasingCurve, QAbstractAnimation,)
from PyQt6.QtGui import QFont, QFontDatabase, QPainter, QIcon

from PyQt6.QtWidgets import (QApplication, QFileDialog, QFrame, QGraphicsScene, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget,)

import api
import settings as settings_module
import wallpaper


ACCENT = "#1FC3FF"
ACCENT_HOVER = "#49D2FF"
ACCENT_PRESSED = "#0F9BD1"
ACCENT_DISABLED_BG = "#1B3A47"
ACCENT_DISABLED_TEXT = "#6C8892"


BG_MAIN = "#000000"
BG_CARD = "#C65F0F"
BG_INPUT = "#B45109"
BORDER = "#8A3D06"
BORDER_HOVER = "#6F3004"
TEXT_MAIN = "#000000"
TEXT_MUTED = "#1E1208"

FONTS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fonts"
)

LOGO_FONT_FAMILY = "Segoe UI"


def load_logo_font():
    global LOGO_FONT_FAMILY

    print(
        f"[font] Looking for fonts in: {FONTS_DIR}"
    )

    if not os.path.isdir(FONTS_DIR):
        print(
            "[font] The 'fonts' folder does not exist."
        )
        return

    print(
        f"[font] Files found in fonts/: "
        f"{os.listdir(FONTS_DIR)}"
    )

    candidates = [
        "GreatVibes-Regular.ttf",
        "GreatVibes-Regular.otf",
        "Sacrifice.otf",
        "Sacrifice.ttf",
        "sacrifice.otf",
        "sacrifice.ttf",
    ]

    for filename in candidates:

        path = os.path.join(
            FONTS_DIR,
            filename
        )

        if os.path.exists(path):

            print(
                f"[font] Found file: {path}"
            )

            font_id = (
                QFontDatabase.addApplicationFont(
                    path
                )
            )

            if font_id == -1:
                print(
                    "[font] Failed to load font."
                )
                continue

            families = (
                QFontDatabase
                .applicationFontFamilies(
                    font_id
                )
            )

            print(
                f"[font] Loaded successfully: "
                f"{families}"
            )

            if families:
                LOGO_FONT_FAMILY = families[0]
                return

    print(
        "[font] No matching font was found. "
        "Using Segoe UI."
    )


def pick_new_wallpaper(
    genre,
    used_ids
):

    results = api.search_wallpapers(
        genre,
        per_page=15
    )

    unused = [
        r
        for r in results
        if r["id"] not in used_ids
    ]

    if unused:
        candidates = unused
    else:
        candidates = results

    return random.choice(
        candidates
    )
def run_daily_update(
    app_settings,
    status_callback=None
):

    genre = (
        app_settings
        .get("genre", "")
        .strip()
    )

    if not genre:
        return (False, "No wallpaper genre was found.")

    folder = (
        app_settings
        .get("wallpaper_folder", "")
        .strip()
    )

    if not folder:
        return (
            False,
            "No wallpaper folder has been selected."
        )

    today_str = date.today().isoformat()

    if (
        app_settings.get(
            "last_changed_date"
        )
        == today_str
    ):

        wallpaper.cleanup_old_wallpapers(
            folder,
            days=14
        )

        return (
            True,
            "Wallpaper already updated today."
        )

    try:

        if status_callback:
            status_callback(f"Searching for '{genre}' wallpapers...")

        used_ids = app_settings.get(
            "used_wallpaper_ids",
            [])

        chosen = pick_new_wallpaper(
            genre,
            used_ids
        )
        if status_callback:
            status_callback("Downloading your wallpaper...")

        file_path = wallpaper.download_image(
            chosen["url"],
            chosen["id"],
            folder
        )

        if status_callback:
            status_callback("Setting your new wallpaper...")

        wallpaper.set_windows_wallpaper(file_path)

        used_ids.append(chosen["id"])

        app_settings[
            "used_wallpaper_ids"
        ] = used_ids[-200:]

        app_settings[
            "last_changed_date"
        ] = today_str

        settings_module.save_settings(
            app_settings
        )

        if status_callback:
            status_callback(
                "Cleaning up old wallpapers..."
            )

        wallpaper.cleanup_old_wallpapers(
            folder,
            days=14
        )

        return (
            True,
            f"Wallpaper updated for '{genre}'."
        )

    except (
        api.ApiError,
        wallpaper.WallpaperError
    ) as e:

        return (
            False,
            str(e)
        )

    except Exception as e:

        return (
            False,
            f"Unexpected error: {e}"
        )

class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Gambit_icon.png"
        )

        self.setWindowIcon(QIcon(icon_path))

        self.settings = (settings_module.load_settings())

        self.setWindowTitle("Gambit")
        self.setFixedSize( 600, 720)
        self.setObjectName("root")

        self.build_ui()
        self.refresh_labels()

        self.run_check(interactive=False)

    def build_ui(self):

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins( 42, 32, 42, 28)

        main_layout.setSpacing(18)


        title = QLabel("Gambit")

        title_font = QFont(
            LOGO_FONT_FAMILY,
            44,
            QFont.Weight.Normal
        )
        title.setFont(title_font)

        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("title")

        main_layout.addWidget(title)
        subtitle = QLabel("YOUR DESKTOP. YOUR MOVE.")

        subtitle_font = QFont(
            "Segoe UI",
            9
        )

        subtitle_font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing,
            3
        )

        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitle")
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(6)
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins( 0, 0, 0, 0)
        content_layout.setSpacing(18)
        wallpaper_card = QFrame()
        wallpaper_card.setObjectName("mainCard")
        card_layout = QVBoxLayout(wallpaper_card)
        card_layout.setContentsMargins(24, 22, 24, 24)
        card_layout.setSpacing(10)  
        card_title = QLabel("Your Wallpaper")
        card_title_font = QFont(
            "Segoe UI",
            12,
            QFont.Weight.Bold
        )
        card_title_font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing,
            1
        )
        card_title.setFont(card_title_font)
        card_title.setObjectName("cardTitle")
        card_layout.addWidget(card_title)       
        card_description = QLabel("Wanna see magic ?")
        card_description.setObjectName("description")
        card_layout.addWidget(card_description)
        card_layout.addSpacing(4)

        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("e.g. cyberpunk city, anime, mountains...")
        self.genre_input.setText(
            self.settings.get(
                "genre",
                ""
            )
        )
        self.genre_input.setMinimumHeight(46)
        card_layout.addWidget(self.genre_input)      
        self.apply_button = QPushButton("CHANGE WALLPAPER")
        self.apply_button.setMinimumHeight(46)
        self.apply_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_button.clicked.connect(self.on_apply_genre)
        card_layout.addWidget(self.apply_button)
        content_layout.addWidget(wallpaper_card)
        folder_title = QLabel("DOWNLOAD LOCATION")
        self._style_section_title(folder_title)
        content_layout.addWidget(folder_title)
        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)
        self.folder_input = QLineEdit()
        self.folder_input.setText(
            self.settings.get(
                "wallpaper_folder",
                ""
            )
        )

        self.folder_input.setMinimumHeight(42)
        folder_row.addWidget(self.folder_input)
        self.browse_button = QPushButton("Browse")
        self.browse_button.setObjectName("secondaryButton")
        self.browse_button.setMinimumHeight(42)
        self.browse_button.setMinimumWidth(88)
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_button.clicked.connect(self.browse_folder)
        folder_row.addWidget(self.browse_button)
        content_layout.addLayout(folder_row)
        info_row = QHBoxLayout()
        info_row.setSpacing(10)
        self.current_card = (
            self.create_info_card(
                "CURRENT",
                "..."
            )
        )
        self.last_card = (
            self.create_info_card(
                "LAST CHANGE",
                "..."
            )
        )
        self.next_card = (
            self.create_info_card(
                "NEXT CHANGE",
                "..."
            )
        )
        info_row.addWidget(self.current_card)
        info_row.addWidget(self.last_card)
        info_row.addWidget(self.next_card)
        content_layout.addLayout(info_row)
        status_title = QLabel("STATUS")
        self._style_section_title(status_title)
        content_layout.addWidget(status_title)
        self.status_frame = QFrame()
        self.status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(16, 13, 16, 13)
        status_layout.setSpacing(10)
        self.status_dot = QLabel("\u25CF")
        self.status_dot.setObjectName("statusDot")
        status_layout.addWidget(self.status_dot)
        self.status_label = QLabel("Starting Gabit...")
        self.status_label.setObjectName("status")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(
            self.status_label,
            1
        )
        content_layout.addWidget(self.status_frame)
        content_layout.addStretch()
        footer = QLabel(
            "New wallpaper every day  ·  "
            "Old wallpapers expire after 14 days"
        )
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(footer)
        content_widget.setStyleSheet(self._stylesheet())
        margins = (main_layout.contentsMargins())
        available_width = (
            self.width()
            - margins.left()
            - margins.right()
        )
        content_widget.setFixedWidth(available_width)
        content_widget.adjustSize()
        content_size = (content_widget.size())
        scene = QGraphicsScene(self)
        proxy = scene.addWidget(content_widget)
        proxy.setTransformOriginPoint(
            QPointF(
                content_size.width() / 2,
                content_size.height() / 2
            )
        )
        scene.setSceneRect(
            0,
            0,
            content_size.width(),
            content_size.height()
        )
        view = QGraphicsView(scene)
        view.setFrameShape(QFrame.Shape.NoFrame)
        view.setStyleSheet("background: transparent; border: none;")
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setFixedSize(
            content_size.width() + 2,
            content_size.height() + 2
        )
        self.flip_proxy = proxy
        self.flip_group = None
        main_layout.addWidget(view)
        main_layout.addStretch()
        self.setLayout(main_layout)
        self.setStyleSheet(self._stylesheet())
        self.flip_timer = QTimer(self)
        self.flip_timer.timeout.connect(self.trigger_flip)
        self.flip_timer.start(60000)

    def trigger_flip(self):

        if (
            self.genre_input.hasFocus()
            or self.folder_input.hasFocus()
        ):
            return

        if (
            self.flip_group is not None
            and self.flip_group.state()
            == QAbstractAnimation.State.Running
        ):
            return

        flip_down = QPropertyAnimation(
            self.flip_proxy,
            b"rotation"
        )

        flip_down.setDuration(700)
        flip_down.setStartValue(0)
        flip_down.setEndValue(180)
        flip_down.setEasingCurve(QEasingCurve.Type.InOutQuad)
        hold = QPauseAnimation(5000)
        flip_up = QPropertyAnimation(
            self.flip_proxy,
            b"rotation"
        )

        flip_up.setDuration(700)
        flip_up.setStartValue(180)
        flip_up.setEndValue(360)
        flip_up.setEasingCurve(QEasingCurve.Type.InOutQuad)
        group = QSequentialAnimationGroup(self)
        group.addAnimation(flip_down)
        group.addAnimation(hold)
        group.addAnimation(flip_up)
        group.finished.connect(
            lambda: self.flip_proxy.setRotation(
                0
            )
        )

        self.flip_group = group
        self.flip_group.start()


    def _style_section_title(
        self,
        label
    ):

        font = QFont(
            "Segoe UI",
            8,
            QFont.Weight.Bold
        )

        font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing,
            1.5
        )

        label.setFont(font)

        label.setObjectName("sectionTitle")

    def _stylesheet(self):

        return f"""

            QWidget {{
                background-color: transparent;
                color: #000000;
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 10pt;
            }}

            QWidget#root {{
                background-color: #000000;
            }}

            QWidget#contentWidget {{
                background-color: transparent;
            }}


            QLabel#title {{
                background-color: transparent;
                color: #FFFFFF;
                padding-top: 4px;
            }}

            QLabel#subtitle {{
                background-color: transparent;
                color: #FFFFFF;
                padding-bottom: 4px;
            }}


            QLabel#sectionTitle {{
                background-color: transparent;
                color: #000000;
                padding-top: 2px;
                padding-bottom: 2px;
                font-weight: bold;
            }}


            QFrame#mainCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}

            /* WHITE */
            QLabel#cardTitle {{
                background-color: transparent;
                color: #FFFFFF;
            }}

            /* BLACK */
            QLabel#description {{
                background-color: transparent;
                color: {TEXT_MUTED};
                font-size: 9pt;
                padding-bottom: 2px;
            }}


            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 3px;
                padding: 8px 14px;
                color: #000000;
                selection-background-color: {ACCENT};
                selection-color: #000000;
            }}

            QLineEdit:hover {{
                border: 1px solid {BORDER_HOVER};
            }}

            QLineEdit:focus {{
                border: 1px solid #000000;
                background-color: {BG_INPUT};
            }}

            QLineEdit::placeholder {{
                color: #3A2819;
            }}


            QPushButton {{
                background-color: {ACCENT};
                border: none;
                border-radius: 3px;
                padding: 8px 18px;
                color: #000000;
                font-weight: bold;
                letter-spacing: 1px;
            }}

            QPushButton:hover {{
                background-color: {ACCENT_HOVER};
            }}

            QPushButton:pressed {{
                background-color: {ACCENT_PRESSED};
            }}

            QPushButton:disabled {{
                background-color: {ACCENT_DISABLED_BG};
                color: #000000;
            }}


            QPushButton#secondaryButton {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                color: #000000;
                font-weight: bold;
            }}

            QPushButton#secondaryButton:hover {{
                background-color: {BG_CARD};
                border: 1px solid #000000;
            }}

            QPushButton#secondaryButton:pressed {{
                background-color: {BORDER};
            }}


            QFrame#infoCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}

            QLabel#infoTitle {{
                background-color: transparent;
                color: #000000;
                font-size: 7.5pt;
                font-weight: bold;
            }}

            QLabel#infoValue {{
                background-color: transparent;
                color: #000000;
                font-size: 10.5pt;
                font-weight: bold;
                padding-top: 2px;
            }}


            QFrame#statusFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}

            QLabel#statusDot {{
                background-color: transparent;
                color: {ACCENT};
                font-size: 10pt;
            }}

            QLabel#status {{
                background-color: transparent;
                color: #000000;
                font-size: 9pt;
            }}


            QLabel#footer {{
                background-color: transparent;
                color: #000000;
                font-size: 8pt;
                padding-top: 6px;
            }}
        """

    def create_info_card(
        self,
        title,
        value
    ):

        card = QFrame()
        card.setObjectName("infoCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins( 14, 12, 14, 12)
        layout.setSpacing(6)
        title_label = QLabel(title)
        title_font = QFont(
            "Segoe UI",
            7,
            QFont.Weight.Bold
        )
        title_font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing,
            0.8
        )
        title_label.setFont(title_font)
        title_label.setObjectName("infoTitle")
        value_label = QLabel(value)
        value_label.setObjectName("infoValue")
        value_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.value_label = value_label

        return card

    def refresh_labels(self):

        genre = (
            self.settings.get(
                "genre",
                ""
            )
            or "None set"
        )

        today_str = date.today().isoformat()

        if (
            self.settings.get(
                "last_changed_date"
            )
            == today_str
        ):

            last_changed = "Today"
            next_change = "Tomorrow"

        elif self.settings.get(
            "last_changed_date"
        ):

            last_changed = (
                self.settings[
                    "last_changed_date"
                ]
            )
            next_change = "Today"
        else:
            last_changed = "Never"
            next_change = "Today"

        self.current_card.value_label.setText(genre)
        self.last_card.value_label.setText(last_changed)
        self.next_card.value_label.setText(next_change)

    def set_status(
        self,
        message,
        state="info"
    ):

        colors = {
            "info": ACCENT,
            "success": "#3DD68C",
            "error": "#FF6B6B",
        }

        self.status_dot.setStyleSheet(
            f"color: {colors.get(state, ACCENT)};"
            f"font-size: 10pt;"
        )

        self.status_label.setText(message)
        QApplication.processEvents()


    def browse_folder(self):

        current_folder = (
            self.settings.get(
                "wallpaper_folder",
                ""
            )
        )
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Wallpaper Folder",
            current_folder
        )
        if folder:
            self.folder_input.setText(
                folder
            )

            self.settings[
                "wallpaper_folder"
            ] = folder

            settings_module.save_settings(
                self.settings
            )

            self.set_status(
                "Wallpaper folder updated.",
                state="success"
            )

    def on_apply_genre(self):

        genre = (
            self.genre_input
            .text()
            .strip()
        )

        if not genre:

            QMessageBox.warning(
                self,
                "Gambit",
                "Please enter a wallpaper genre first."
            )

            return

        folder = (
            self.folder_input
            .text()
            .strip()
        )

        if not folder:

            QMessageBox.warning(
                self,
                "Gambit",
                "Please choose a wallpaper folder first."
            )

            return

        self.settings["genre"] = genre

        self.settings["wallpaper_folder"] = folder

        self.settings["last_changed_date"] = ""

        settings_module.save_settings(self.settings)

        self.refresh_labels()

        self.run_check(interactive=True)

    def run_check(
        self,
        interactive
    ):

        self.apply_button.setEnabled(False)

        self.apply_button.setText("WORKING")

        self.set_status(
            "Checking today's wallpaper",
            state="info"
        )

        success, message = (
            run_daily_update(
                self.settings,
                status_callback=self.set_status
            )
        )

        self.refresh_labels()

        if success:
            self.set_status(
                message,
                state="success"
            )

        else:
            self.set_status(
                message,
                state="error"
            )

            if interactive:
                QMessageBox.warning(
                    self,
                    "Gambit",
                    message
                )

        self.apply_button.setEnabled(True)

        self.apply_button.setText("CHANGE WALLPAPER")


def run_silent_check():
    app_settings = (
        settings_module.load_settings()
    )


    success, message = (
        run_daily_update(
            app_settings
        )
    )

    print(
        (
            "[OK] "
            if success
            else "[ERROR] "
        )
        + message
    )


def main():
    if "--check" in sys.argv:
        run_silent_check()
        return

    app = QApplication(
        sys.argv
    )

    load_logo_font()
    window = MainWindow()
    window.show()
    sys.exit(
        app.exec()
    )
if __name__ == "__main__":
    main()