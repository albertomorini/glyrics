# Glyrics lyrics for Apple Music

glyrics scans your music's directory and next, for each song will search the lyrics on genius.com (searching by the info retrieved from tags title and artist).
Found the lyrics? Store it into the song.

It's mainly made for iTunes/Apple Music/iPhoneMusic, works only with M4A and MP3 audio.

## Requirements:

- is required a good folder's structure, like iTunes does:

> 	
	artist1/
		album1/
		album2/
	artist2/
	  	album1/
	....

- Python3 and some libraries:
	- os
	- sys
	- lyricsgenius
	- tinytag
	- mutagen

**Some pics** (more into imgExample/)
![Output](https://github.com/albertomorini/glyrics/blob/main/imgExample/github1.gif)


## How it works

1) glyrics.py -> works with M4A and MP3, for each song check if previously has been found the lyrics searching into glyrics.json, a 'preferences' file created the first time you run glyrics, into the file is stored the MD5 of all the songs that glyrics has found.
So, we don't check if the song has already a tag for lyrics, we just compute the MD5 and check into our little 'database'.

2) glyricsSelf.py -> works only with M4A, for each song check if there's an existing lyrics stored (checking the tag "©lyr"), if not it will search etc.

**GENIUS API KEY**

You need one to use genius, I provided mine, isn't a security problem in my opinion, it allows you just to download/search lyrics.

## Usage:

`$ python3 glyrics.py mode "path"`
	- mode = "search" for search/add lyrics, "flush" for delete the existing lyrics
	- path is the path to your music folder (is recursive, found every song stored in every subfolder) like /Media/Music/...

## PROBLEMS:

1) Genius's search: if a song has featuring or is a remix i remove that info.
Why? Because can brings us different results.

	eg. title="Pain 1993 (feat. Playboi Carti)", artist="Drake"
		download the lyrics in (i guess) Cyrillic languages.

		instead, title = "Pain 1993", artist="Drake"
		download the lyrics in English language.
**working on it**

2) We can't do a self glyrics for MP3, because it's an awful format cause doesn't have a defined single tag like M4A ("©lyr"), MP3 has "USLT:desc:eng".. Maybe we can use a regular expression "USLT*" to search the tag. *Working on it*

![Output](https://github.com/albertomorini/glyrics/blob/main/imgExample/problem_mp3Tag.png)


## TODO
- [ ] correct the artist/title tags, eg. artist="Drake & Kanye West" song="Glow" is wrong, because the artist is "Drake" and the song is "Glow (feat. Kanye West)".. so search on genius the song get the righ info.
