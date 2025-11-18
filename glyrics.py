import os
import sys
import json
import hashlib
from tinytag import TinyTag
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT
import lyricsgenius as genius

## GENIUS STUFF
APIkey_genius= open("./genius_APIKEY.txt","r").read()
genius = genius.Genius(APIkey_genius)
genius.skip_non_songs = False #we search also the songs without lyrics (eg soundtrack) in the way to mark them as founded (already searched).

########################################################################
# UTILITY

def serializeJSON(dir_path, filename, dataDictionary):
	with open(os.path.join(dir_path, filename), "w", encoding="utf-8") as f:
		json.dump(dataDictionary, f, ensure_ascii=False, indent=2)

def readJson(path):
	try:
		with open(path, "r", encoding="utf-8") as f:
			return json.load(f)
	except Exception:
		print(f"Warning: {path} does not exist or is not valid JSON")
		return None

def doMD5(str_value):
	return hashlib.md5(str_value.encode('utf-8')).hexdigest()

########################################################################
# GENIUS INTEGRATION AND FILE MANAGEMENT

#return None if the lyrics isn't found, could be because the songs hasn't enough info (title, artist)
def searchLyrics(pathSong):
	try:
		metaData = TinyTag.get(pathSong)
		info = genius.search_song(metaData.title.split("(")[0],metaData.artist) #split to remove the "feat"/"remix" etc. look at readme.md
		return info.lyrics

	except Exception as e:
		return None

#store the lyrics into song tag
def storeLyrics(song_path, song_lyrics_text):
	dummy_ext=song_path[-4:].lower() #just the extension
	try:
		if(dummy_ext == ".m4a"):
			song = MP4(song_path)
			song["©lyr"] = song_lyrics_text
			song.save()
		elif(dummy_ext == ".mp3"):
			song = ID3(song_path)
			song["USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=song_lyrics_text))
			song.save()
		elif(dummy_ext == ".flac"):
			song = FLAC(song_path)
			print(song)
			song["LYRICS"] = song_lyrics_text
			song.save()
		return [True,dummy_ext]
	except Exception as e:
		print(e)
		return [False,None]


#DANGER: erase the lyrics of the songs
def flushLyrics(song_path):
	dummy_ext=song_path[-4:].lower() #just the extension
	try:
		if(dummy_ext == ".m4a"):
			song = MP4(song_path)
			song.pop("©lyr")
			song.save()
		elif(dummy_ext == ".mp3"):
			song = ID3(song_path)
			song.pop("USLT::'eng'")
			song.save()
		elif(dummy_ext == ".flac"):
			song = FLAC(song_path)
			song.pop("LYRICS")
			song.save()
		return [True,dummy_ext]
	except Exception as e:
		print(e)
		return [False,None]

########################################################################
## LOGIC AND ALGORITHM

#search a previous registry of song searched, if there isn't will create a new one
def checkRegistry(path, filename):
	pref = readJson(os.path.join(path,filename))
	if(pref==None):
		pref = {
			"alreadySearched": [],
			"mp3":0,
			"m4a":0,
			"flac":0
		}
	return pref


#process each song by searching and saving the lyrics
def scanFolder(path,isFlush=False):
	dictSongs = checkRegistry(path, "glyrics.json") #configuration file, stored on @param path
	for root, directories, files in os.walk(path, topdown=True):
		for name in files:
			song_path=str(os.path.join(root, name))
			if(isFlush):
				flushLyrics(song_path)
			elif(str(doMD5(song_path)) not in dictSongs.get("alreadySearched") and name[0]!='.'): #if song is never been searched or hasn't got lyricstxt and file is not a hidden one
				lyricstxt = searchLyrics(song_path)
				res_store = storeLyrics(song_path,lyricstxt)
				if(res_store[0]): ##lyrics found and stored
					dictSongs.get("alreadySearched").append(doMD5(song_path))
					try:
						dictSongs[res_store[1]] += 1
					except Exception as e:
						pass


	return dictSongs

#############################################################################
#start the program, let choose two option: "Flush" -> erease the previous lyrics, "search" -> scan the folder
def main():
	if len(sys.argv) < 3:
		print("Usage: python3 glyrics.py <Flush|Search> <FolderPath>")
		return
	
	command = sys.argv[1].upper()
	folder_path = sys.argv[2]

	if command == "FLUSH":
		if (str(input("DANGER:: Insert 'suRe' if you're really sure\n"))=='suRe'):
			scanFolder(sys.argv[2],True)
	elif(sys.argv[1].upper()=="SEARCH"):
		dictSongs = scanFolder(sys.argv[2])
		print(dictSongs)
		serializeJSON(sys.argv[2],"glyrics.json",dictSongs)
		print("Scan complete!")
	else:
		print("Searching for a default configuration...")
		try:
			config = open(".config.txt","r")
			print("Configuration founded! Loading it")
			scanFolder(config.read().rstrip()) ##give the path to the scan folder
		except Exception:
			print("No file '.config.txt' with a path founded")
			print("Try to run with $python3 glyrics.py Flush/Search $Path")

main()