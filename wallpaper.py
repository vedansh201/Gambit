import ctypes
import os
import time
from pathlib import Path
import requests


class WallpaperError(Exception):
    pass

def get_wallpaper_folder(folder_path):
     if not folder_path:
          raise WallpaperError("No wallpaper folder has been selected.")
     folder = Path(folder_path).expanduser()

     try:
          folder.mkdir(parents=True, exist_ok=True)

     except OSError as e:
          raise WallpaperError(
               f"Couldn't create the wallpaper folder :{e}",
               f"Failed to create wallpaper folder: {e}"
          )


     return folder



def download_image(url, wallpaper_id, folder_path):
     if not url or not url.lower().startswith("http"):
          raise WallpaperError(
               "the image is invalid"
          )
     folder = get_wallpaper_folder(folder_path)

     ext = ".jpg"
     lowered =url.lower()

     for candidate in (".jpg", "jpeg", "png", "bmp", "webp" ):
          if candidate in lowered:
               ext = candidate
               break


     file_path = folder / f"wallpaper_{wallpaper_id}{ext}"
     try:
          response = requests.get(
               url,
               timeout=30

          )

     except requests.exceptions.ConnectionError:
          raise WallpaperError("no internet connection")
     except requests.exceptions.Timeout:
          raise WallpaperError("connection timed out")
     except requests.exceptions.RequestException as e:
          raise WallpaperError(f"failed to download image: {e}")
     if response.status_code != 200:
          raise WallpaperError(
               f"failed to download image"
               f"(status {response.status_code})."
          )
     try:
          with open(file_path, "wb") as f:
               f.write(response.content)

     except OSError as e:
          raise WallpaperError(
               f"failed to save image : {e}"

          )
     return str(file_path)

def get_current_wallpaper():
    SPI_GETDESKWALLPAPER = 0x0073

    buffer = ctypes.create_unicode_buffer(260)

    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_GETDESKWALLPAPER,
        260,
        buffer,
        0
    )

    if result:
        return os.path.abspath(buffer.value)


    return ""


def cleanup_old_wallpapers(folder_path, days=14):
    folder = get_wallpaper_folder(folder_path)
    current_wallpaper = get_current_wallpaper()
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    deleted_count = 0
    try:
        files = folder.iterdir()

    except OSError:
        return 0
    for file_path in files:
        if not file_path.is_file():
            continue
        if not file_path.name.startswith("wallpaper_"):
            continue
        try:
            if os.path.abspath(str(file_path)) == current_wallpaper:
                continue
        except OSError:
            continue
        try:
            modified_time = file_path.stat().st_mtime

            if modified_time < cutoff_time:
                file_path.unlink()
                deleted_count += 1
        except OSError:
            continue
    return deleted_count


def set_windows_wallpaper(file_path):
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02

    abs_path = os.path.abspath(file_path)

    if not os.path.exists(abs_path):
        raise WallpaperError(
            "wallpaper file does not exist on disk."
        )

    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        abs_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

    if not result:
        raise WallpaperError("Windows refused to set the wallpaper.")