# Glyrics 2.0 ~ a lyrics injector for your music library

<b style="color: green">New version!! </b>

Glyrics used to fetch lyrics from <a hfref="genius.com">Genius</a> and embeds them directly into your audio files.

**Now, combine** <a hfrefg="https://lyrics.ovh">lyrics.ovh</a> **and genius.com**

**Supported formats**: 
1. mp3
1. m4a
1. flac

**Successfully tested with:**
- Apple Music (iTunes, iPhone, macOS)
- Jellyfin
- Plex
- KODI
- Auxio / Phocid (Android)


## Usage:
```shell 
$ python3 glyrics.py mode "path" 
```

- **mode**:
	- `search` — fetch and embed lyrics
	- `flush` — remove existing lyrics

- **path**:
	- Path to your music folder
	- Recursive — scans all subfolders
	- Example: /mnt/MEDIA/MUSIC/ or /myFavAritst/myFavAlbum


### main logic

Crate a dict (glyrics.json) to store the already searched songs (found and missing), just search the new and missing songs.. This in order to avoid duplicated and unwanted requests

For each new or missing song:
1. search on lyrics.ovh the lyrics
2. if lyrics found and OK --> embed text into file (w/ mutagen) and flag song as found
3. else search lyrics in genius.com --> repeat 2 and if not found, flag song as missing

Genius.com is a second choice because the request are limited, like 100 every hour, so use it just as redundance

In version 1 there was `glyricsSelf.py` which worked only with M4A, FLAC, NOT compatible with MP3 because MP3 stores lyrics in different tag structures (see Problems below).
- that code checks the "©lyr" and "LYRICS" tags: If empty, fetches lyrics and embeds them.

In new version has been integrated in the search function in order to lay up API calls and avoid lyrics overwrites.

> if you want to overwrite an old lyrics, use the flush mode and then do the search


## Requirements:

- is required a good folder's structure, like iTunes/Plex does:
> 	
	artist1/
		album1/
		album2/
	artist2/
	  	album1/
	....

- Python3 with:
	- os
	- sys
	- lyricsgenius
	- tinytag
	- mutagen

<hr/>

### Python Dependencies:

- sys
- json
- requests
- urllib.parse
- pathlib
- tinytag
- mutagen
- lyricsgenius


### Showcases
![Output](./imgExample/github1.gif)


## Known Issues:

1) Genius but also LyricsOVH search inconsistencies: Tracks with “feat.” or “remix” variations may return incorrect or foreign-language lyrics.
*example*
```ini
	title="Pain 1993 (feat. Playboi Carti)"
	artist="Drake"
	→ Might return lyrics in Cyrillic.
```
BUT
```ini
	title="Pain 1993"
	artist="Drake"
	→ Returns correct English lyrics.
```

**working on it**

2) No MP3 “self check”
- M4A files use a clear and consistent lyrics tag: "©lyr".
- MP3 files, however, use ID3 tags like: `USLT:desc:eng`
  - This varies between files and makes detection unreliable. A possible solution is to detect them via pattern matching (e.g., USLT*).

MP3 tags

![Output](imgExample/problem_mp3Tag.png)


### TODO
- [ ] Improve parsing of artist/title to better handle cases like:
- Example:
  - Current: artist="Drake & Kanye West", song="Glow"
  - Expected: artist="Drake", song="Glow (feat. Kanye West)"
  - *Then search Genius with the corrected metadata.*