import sys
import json
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


#store the lyrics into song tag
def store_lyrics2song(song_path, lyrics_text):
	song_path = str(song_path)
	dummy_ext=song_path[-4:].lower() #just the extension
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


def add_lyrics_directory(folder_path):
	register = load_register(folder_path)
	print(register)

	all_songs = list_songs(folder_path)
	not_searched = list(set(all_songs) - set(register.get("lyrics_found")))
	for s in not_searched:
		s_str = str(Path(s))
		try:
			dummy_lyrics = get_lyrics_genius(s)
			storing_res = store_lyrics2song(s,dummy_lyrics)
			register.get("counter")[storing_res[1][-3:]] += 1 # remove the dot from the extension
			if(storing_res[0]):
				register.get("lyrics_found").append(s_str)
				print("Added successfully for: ",s_str)
			else:
				register.get("lyrics_missing").append(s_str)
		except Exception as e:
			print("ERROR PROCESSING: ",s_str," ~ ",e)
			register.get("lyrics_missing").append(s_str)

	print(register)
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