# Glyrics ~ a lyrics injector for your music library

Glyrics automatically fetches lyrics from <a hfref="genius.com">Genius</a> and embeds them directly into your audio files.

Supports any well-structured music library. <br/>
Successfully tested with:
- Apple Music (iTunes, iPhone, macOS)
- Jellyfin
- Plex
- Auxio / Phocid (Android)

Supported formats: mp3, m4a, flac


## How It Works

`glyrics.py`
- Supports MP3, M4A, FLAC.

For each song:
1. Checks glyrics.json to see if lyrics were already retrieved.
2. If found, lyrics are embedded into the file.
3. The script then stores an MD5 hash of the song name to avoid future redundant searches.

`glyricsSelf.py`
> Works only with M4A, FLAC. Not compatible with MP3 because MP3 stores lyrics in different tag structures (see Problems below).

1. Checks the "©lyr" and "LYRICS" tags: If empty, fetches lyrics and embeds them.
- do not store JSON file/registers

## Usage:
```shell 
$ python3 glyrics.py mode "path" 
```

- mode:
	- search — fetch and embed lyrics
	- flush — remove existing lyrics

- path:
	- Path to your music folder
	- Recursive — scans all subfolders
	- Example: /Media/Music/

### Requirements:

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

- os
- sys
- lyricsgenius
- tinytag
- mutagen

### Showcases
![Output](./imgExample/github1.gif)


## Known Issues:

1) Genius search inconsistencies: Tracks with “feat.” or “remix” variations may return incorrect or foreign-language lyrics.
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