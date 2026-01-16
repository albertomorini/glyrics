import sys
import json
import requests
import urllib.parse
from pathlib import Path
from tinytag import TinyTag
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT
import lyricsgenius as genius


REGISTER_NAME = "glyrics.json"
SUPPORTED_EXTENSIONS = {".m4a", ".mp3", ".flac"}  # use a set for faster lookup

## GENIUS STUFF
APIkey_genius= open("./genius_APIKEY.txt","r").read()
genius = genius.Genius(APIkey_genius,sleep_time=1)
genius.skip_non_songs = False #we search also the songs without lyrics (eg soundtrack) in the way to mark them as founded (already searched).
genius.remove_section_headers = True

########################################################################
# UTILITY
def store_register(register,folder_path):
	try:
		with open(Path(folder_path,REGISTER_NAME),"w",encoding="utf-8") as f:
			json.dump(register, f, ensure_ascii=False, indent=2)
	except Exception as e:
		print("Error storing register: ",e)

def load_register(folder_path):
	try:
		with open(Path(folder_path,REGISTER_NAME), "r", encoding="utf-8") as f: # reading music folder's register
			return json.load(f)
	except Exception:
		print(f"Warning: {folder_path} does not exist or is not valid JSON; creating one")
		store_register({"lyrics_found":[],"lyrics_missing":[],"counter":{"m4a":0,"mp3":0,"flac":0}},folder_path)
		return load_register(folder_path)

def list_songs(root):
    return [p for p in Path(root).rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]

########################################################################
# GENIUS INTEGRATION AND FILE MANAGEMENT

#return None if the lyrics isn't found, could be because the songs hasn't enough info (title, artist)
def get_lyrics_genius(pathSong):
	metaData = TinyTag.get(pathSong)
	info = genius.search_song(metaData.title.split("(")[0],metaData.artist) #split to remove the "feat"/"remix" etc. look at readme.md
	return info.lyrics

# https://lyricsovh.docs.apiary.io/#reference/0/lyrics-of-a-song/search
def get_lyrics_lyricsovh(song_path):
	metadata = TinyTag.get(song_path)

	if(metadata.title == None and metadata.artist == None):
		dummy_split = song_path.split("/")
		dummy_ext = get_extension(song_path)
		song_title = str(dummy_split[-1]).replace(dummy_ext,"").split("(")[0].strip()
		song_artist = dummy_split[-3]
	else:
		song_title = metadata.title.split("(")[0].strip()
		song_artist = metadata.artist.split("&")[0].strip()


	song_title = urllib.parse.quote(song_title, safe="") ##.split("(")[0]  #split to remove the "feat"/"remix" etc. look at readme.md
	song_artist = urllib.parse.quote(song_artist, safe="") # # OVH seems to want just the main artist

	dummy_url = "https://api.lyrics.ovh/v1/"+song_artist+"/"+song_title
	res = requests.get(dummy_url)
	if(res.status_code==200):
		return res.json().get("lyrics")
	else:
		try: # if not found, try to seach it on genius.com
			print("Lyrics OVH not found, trying on genius.com for: "+song_title, " by ", song_artist)
			return get_lyrics_genius(song_path)
		except Exception as e:
			print("Lyrics missing for: ",song_title, " by ", song_artist)
			return None


#store the lyrics into song tag
def store_lyrics2song(song_path, lyrics_text):
	song_path = str(song_path)
	dummy_ext= get_extension(song_path)
	try:
		if(dummy_ext == ".m4a"):
			song = MP4(song_path)
			song["©lyr"] = lyrics_text
			song.save()
		elif(dummy_ext == ".mp3"):
			song = ID3(song_path)
			song["USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics_text))
			song.save()
		elif(dummy_ext == ".flac"):
			song = FLAC(song_path)
			print(song)
			song["LYRICS"] = lyrics_text
			song.save()
		return [True,dummy_ext]
	except Exception as e:
		print("ERROR storing lyrics in the song: ",song_path," ~ error: ",e)
		return [False,None]


#DANGER: erase the lyrics of the songs
def flushLyrics(song_path):
	dummy_ext= get_extension(song_path)
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

#return True if the song has already a lyrics (means has already a lyrics tag)
def lyrics_already_exists(song_path):
	dummy_ext= get_extension(song_path)
	try:
		if(dummy_ext == ".m4a"):
			song = MP4(song_path)
			if(song["©lyr"]!= None):
				return True
		elif(dummy_ext == ".flac" and song["LYRICS"]!= None):
			song = FLAC(song_path)
			if(song["LYRICS"]!= None):
				return True
		return False
	except Exception as e:
		#the lyrics tag doesn't exists
		return False

## return the extension of the file dot included (.flac/.m4a/.mp3)
def get_extension(song_path):
	return song_path[-4:].lower() #just the extension

########################################################################


def add_lyrics_directory(folder_path):
	register = load_register(folder_path)

	all_songs = list_songs(folder_path)
	not_searched = list(set(str(s) for s in all_songs) - set(register.get("lyrics_found")))
	for s in not_searched:
		s_str = str(Path(s))
		if(not lyrics_already_exists(s)): ## if already present a Lyrics tag, skip
			try:
				dummy_lyrics = get_lyrics_lyricsovh(s)
				if(dummy_lyrics != None):
					storing_res = store_lyrics2song(s,dummy_lyrics)
					register.get("counter")[get_extension(s).replace(".","",)] += 1 # remove the dot from the extension

				if(dummy_lyrics != None and  len(dummy_lyrics)>1 and storing_res[0] and s_str not in register.get("lyrics_found")):
					register.get("lyrics_found").append(s_str)
					print("Added successfully for: ",s_str)
					if(s_str in register.get("lyrics_missing")): # pop if missing, now found
						register["lyrics_missing"].remove(s_str)

				else:
					if(s_str not in register.get("lyrics_missing")): # avoid duplication
						register.get("lyrics_missing").append(s_str)
			except Exception as e:
				print("ERROR PROCESSING: ",s_str," ~ ",e)
				register.get("lyrics_missing").append(s_str)
		else: ## set as OK in the dicts, in order to avoid unuseful checks next time
			register.get("lyrics_found").append(s_str)
			register.get("counter")[get_extension(s).replace(".","",)] += 1 # remove the dot from the extension

	## consistency ~ remove potential duplicates
	register["lyrics_found"] = list(set(register.get("lyrics_found")))
	register["lyrics_missing"] = list(set(register.get("lyrics_missing")))
	store_register(register,folder_path)

def flush_lyrics_directory(folder_path):
	store_register({"lyrics_found":[],"lyrics_missing":[],"counter":{"m4a":0,"mp3":0,"flac":0}},folder_path) ## init the register
	all_songs = list_songs(folder_path)
	for s in all_songs:
		flush_lyrics_directory(s)
########################################################################

## LOGIC AND ALGORITHM
def main():
	if len(sys.argv) < 3:
		print("Usage: python3 glyrics.py <Flush|Search> <FolderPath>")
		return
	else:
		command = sys.argv[1].upper()
		folder_path = sys.argv[2]

	match command.upper():
		case "FLUSH":
			print("Flushing lyrics...")
			if(str(input("DANGER: type 'suRe' if you're really sure \n this will be remove lyrics from indicated path! ")) == 'suRe'):
				flush_lyrics_directory(folder_path)
		case "SEARCH":
			add_lyrics_directory(folder_path)
		case _:
			print("Unknown command")

	## TODO: include also self modality instead of two file, allows also single file operations

main()