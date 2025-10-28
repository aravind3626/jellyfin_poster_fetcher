import os
import requests
import xml.etree.ElementTree as ET
from imdb import IMDb

# === CONFIGURATION ===
OMDB_API_KEY = 'xxxxxx'      # your omdb api key
POSTER_PROVIDER_1 = 'omdb'   # Primary: 'omdb'
POSTER_PROVIDER_2 = 'imdb'   # Fallback: 'imdb'
OVERWRITE = False            # Set to False to skip folders that already have folder.jpg

# === STEP 1: Generate NFO using IMDbPY ===
def generate_nfo_from_imdb(folder_path):
    movie_title = os.path.basename(folder_path)
    ia = IMDb()
    results = ia.search_movie(movie_title)

    if not results:
        print(f"[NFO] Movie not found on IMDb: {movie_title}")
        return

    movie = results[0]
    ia.update(movie)

    title = movie.get('title')
    year = movie.get('year')
    plot = movie.get('plot outline', 'N/A')
    rating = movie.get('rating', 'N/A')
    poster_url = movie.get('full-size cover url')
    imdb_id = movie.movieID

    # Build NFO content
    nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
  <title>{title}</title>
  <year>{year}</year>
  <plot>{plot}</plot>
  <rating>{rating}</rating>
  <poster>{poster_url}</poster>
  <imdbid>tt{imdb_id}</imdbid>
</movie>
"""
    nfo_path = os.path.join(folder_path, "movie.nfo")
    with open(nfo_path, 'w', encoding='utf-8') as f:
        f.write(nfo_content)
    print(f"[NFO] Created: {nfo_path}")

# === STEP 2: Extract IMDb ID from NFO ===
def extract_imdbid_from_nfo(nfo_path):
    try:
        tree = ET.parse(nfo_path)
        root = tree.getroot()
        imdbid = root.findtext('imdbid')
        return imdbid.strip() if imdbid else None
    except Exception as e:
        print(f"[ERROR] Failed to parse IMDb ID from NFO: {nfo_path} — {e}")
        return None

# === STEP 2b: Extract title and year from NFO ===
def extract_title_year_from_nfo(nfo_path):
    try:
        tree = ET.parse(nfo_path)
        root = tree.getroot()
        title = root.findtext('title')
        year = root.findtext('year')
        return title.strip() if title else None, year.strip() if year else None
    except Exception as e:
        print(f"[ERROR] Failed to extract title/year from NFO: {nfo_path} — {e}")
        return None, None

# === STEP 3: Download poster from OMDb ===
def download_poster_from_omdb(imdbid, folder_path):
    url = f"http://www.omdbapi.com/?i={imdbid}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data.get('Response') == 'True':
        poster_url = data.get('Poster')
        if poster_url and poster_url != 'N/A':
            return download_image(poster_url, folder_path, source='OMDb')
    print(f"[OMDb] Poster not found for {imdbid}")
    return False

# === STEP 4: Download poster from IMDbPY using title + year ===
def download_poster_from_imdb_using_title(title, year, folder_path):
    ia = IMDb()
    try:
        results = ia.search_movie(title)
        if not results:
            print(f"[IMDb] No search results for title: {title}")
            return False

        # Try to match year if provided
        movie = None
        for result in results:
            if str(result.get('year')) == str(year):
                movie = result
                break
        if not movie:
            movie = results[0]  # fallback to first result

        ia.update(movie)
        poster_url = movie.get('full-size cover url') or movie.get('cover url')
        if poster_url:
            return download_image(poster_url, folder_path, source='IMDb')
        print(f"[IMDb] Poster not found for {title} ({year})")
    except Exception as e:
        print(f"[ERROR] IMDbPY failed for {title} ({year}): {e}")
    return False

# === STEP 5: Download and save image as folder.jpg ===
def download_image(url, folder_path, source):
    poster_path = os.path.join(folder_path, "folder.jpg")
    if os.path.exists(poster_path) and not OVERWRITE:
        print(f"[SKIP] folder.jpg already exists and OVERWRITE is False: {poster_path}")
        print(f"[SKIP] Folder skipped: {folder_path}")
        return False

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        with open(poster_path, 'wb') as f:
            f.write(r.content)
        print(f"[{source}] Poster saved as: {poster_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download from {source}: {e}")
        return False

# === MAIN PROCESSING ===
def process_subfolders(root_folder):
    for entry in os.scandir(root_folder):
        if not entry.is_dir():
            continue

        folder_path = entry.path
        print(f"\n📁 Processing: {folder_path}")

        # Step 1: Generate NFO
        generate_nfo_from_imdb(folder_path)

        # Step 2: Extract IMDb ID
        nfo_path = os.path.join(folder_path, "movie.nfo")
        if not os.path.exists(nfo_path):
            print("[SKIP] No NFO found.")
            continue

        imdbid = extract_imdbid_from_nfo(nfo_path)
        title, year = extract_title_year_from_nfo(nfo_path)

        if not imdbid or not title:
            print("[SKIP] Missing IMDb ID or title in NFO.")
            continue

        # Step 3: Try poster from provider 1
        success = False
        if POSTER_PROVIDER_1 == 'omdb':
            success = download_poster_from_omdb(imdbid, folder_path)
        elif POSTER_PROVIDER_1 == 'imdb':
            success = download_poster_from_imdb_using_title(title, year, folder_path)

        # Step 4: Fallback to provider 2 if needed
        if not success:
            print(f"[INFO] Trying fallback provider: {POSTER_PROVIDER_2}")
            if POSTER_PROVIDER_2 == 'omdb':
                download_poster_from_omdb(imdbid, folder_path)
            elif POSTER_PROVIDER_2 == 'imdb':
                download_poster_from_imdb_using_title(title, year, folder_path)

# === Example usage ===
root_folder = r"W:\media\music\artist"
process_subfolders(root_folder)

print ("\n✅ All done!")