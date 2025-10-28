# 🎬 IMDb & OMDb Poster Fetcher with NFO Generator for Jellyfin/Plex/Emby

This Python script automates the creation of `.nfo` metadata files and downloads movie posters for a folder-based media library. It uses [IMDbPY](https://github.com/alberanid/imdbpy) and [OMDb API](http://www.omdbapi.com/) to fetch metadata and posters, ensuring compatibility with media managers like **Kodi** and **Plex**.

****** Tested for Jellyfin, should work for Plex and Emby as well, just check on what name the poster should be saved and modify accordingly *******

---

## 📦 Features

- Extracts movie title from folder name and fetches metadata from IMDb
- Generates `.nfo` files with title, year, plot, rating, poster URL, and IMDb ID
- Downloads poster image as `folder.jpg` using:
  - ✅ Primary provider: OMDb (via IMDb ID)
  - 🔁 Fallback provider: IMDbPY (via title + year)
- Skips folders with existing posters if `OVERWRITE = False`
- Logs skipped folders and failed lookups

---

## 🛠 Requirements

- Python 3.7+
- [IMDbPY](https://pypi.org/project/IMDbPY/) → `pip install IMDbPY`
- [Requests](https://pypi.org/project/requests/) → `pip install requests`
- OMDb API key → [Get one here](http://www.omdbapi.com/apikey.aspx)

---

## ⚙️ Configuration

Edit the top of the script to set your preferences:

```python
OMDB_API_KEY = 'your_omdb_api_key_here'
POSTER_PROVIDER_1 = 'omdb'   # Primary: 'omdb' or 'imdb'
POSTER_PROVIDER_2 = 'imdb'   # Fallback: 'omdb' or 'imdb'
OVERWRITE = False            # Set to True to overwrite existing folder.jpg
```

---

## 📁 Folder Structure

Each movie should be in its own folder named after the movie title:

```
W:\media\music\A. R. Rahman\
├── Varalaaru\
│   └── movie.nfo       # generated
│   └── folder.jpg      # poster
├── Roja\
│   └── ...
```

---

## 🚀 How It Works

1. Scans each subfolder in the root directory
2. Uses folder name to search IMDb and generate `.nfo`
3. Extracts IMDb ID, title, and year from `.nfo`
4. Downloads poster from OMDb using IMDb ID
5. If OMDb fails, retries using IMDbPY with title + year
6. Saves poster as `folder.jpg` in the movie folder

---

## 🧪 Example Usage

```python
root_folder = r"W:\media\music\A. R. Rahman"
process_subfolders(root_folder)
```

---

## 🧠 Notes

- IMDbPY may not return posters when queried by IMDb ID directly. This script works around that by using title + year for fallback.
- OMDb is more reliable for poster URLs, especially for mainstream titles.
- For regional or older films, IMDbPY via title search is often more accurate.

---

## 📌 License

This script is provided as-is for personal use. No warranties or guarantees. Attribution appreciated if reused.

```
Let me know if you'd like to add badges, usage screenshots, or a sample `.nfo` output to the README.
