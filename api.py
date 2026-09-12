import requests
from urllib.parse import quote

BASE_URL = "https://wallpapers.com/api/v1"


class ApiError(Exception):
    
    pass


def search_wallpapers(query, per_page=15):

    if not query or not query.strip():
        raise ApiError("Please enter a wallpaper genre.")

    slug = quote(query.strip().lower().replace(" ", "-"))

    url = f"{BASE_URL}/keyword/{slug}"

    params = {
        "limit": min(per_page, 60)
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15
        )

    except requests.exceptions.ConnectionError:
        raise ApiError(
            "No internet connection. Please check your network."
        )

    except requests.exceptions.Timeout:
        raise ApiError(
            "The Wallpapers.com request timed out. "
            "Please try again later."
        )

    except requests.exceptions.RequestException as e:
        raise ApiError(
            f"Network error while contacting Wallpapers.com: {e}"
        )

    if response.status_code == 404:
        raise ApiError(
            f"No wallpapers found for '{query}'. "
            "Try another search term."
        )

    if response.status_code == 429:
        raise ApiError(
            "Wallpapers.com rate limit reached. Please try again later."
        )

    if response.status_code != 200:
        raise ApiError(
            f"Wallpapers.com returned an error "
            f"(status {response.status_code})."
        )

    try:
        data = response.json()
    except ValueError:
        raise ApiError(
            "Wallpapers.com returned an invalid response."
        )

    # Wallpapers.com puts the results inside "items".
    wallpapers = data.get("items", [])

    if not wallpapers:
        raise ApiError(
            f"No wallpapers found for '{query}'. "
            "Try another search term."
        )

    results = []

    for item in wallpapers:
        if not isinstance(item, dict):
            continue

        wallpaper_id = item.get("id")

        # "high" is the actual image.
        image_url = item.get("high")

        if wallpaper_id is None or not image_url:
            continue

        results.append({
            "id": wallpaper_id,
            "url": image_url,
            "page_url": item.get("url"),
            "credit_url": item.get("credit_url"),
            "credit_text": item.get("credit"),
        })

    if not results:
        raise ApiError(
            f"Wallpapers.com returned no usable wallpapers for '{query}'."
        )

    return results