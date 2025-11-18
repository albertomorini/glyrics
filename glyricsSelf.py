import os
import sys
import lyricsgenius as genius
from tinytag import TinyTag
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

## GENIUS STUFF
APIkey_genius= open("./genius_APIKEY.txt","r").read()
genius = genius.Genius(APIkey_genius)
genius.skip_non_songs = False #we search also the songs without lyrics (eg soundtrack) in the way to mark them as founded (already searched).

########################################################################

#return None if the lyrics isn't found, could be because the songs hasn't enough info (title, artist)
def searchLyrics(pathSong):
	try:
		metaData = TinyTag.get(pathSong)
		info = genius.search_song(metaData.title.split("(")[0],metaData.artist) #split to remove the "feat"/"remix" etc. look at readme.md
		return info.lyrics

	except Exception as e:
		return None

#return True if the song has alreay a lyrics (means has already a lyrics tag)
def lyricsExists(song_path):
	dummy_ext=song_path[-4:].lower() #just the extension
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

#store the lyrics into song tag
def storeLyrics(song_path, song_lyrics_text):
	dummy_ext=song_path[-4:].lower() #just the extension
	try:
		if(dummy_ext == ".m4a"):
			song = MP4(song_path)
			song["©lyr"] = song_lyrics_text
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



########################################################################

#DANGER: erase the lyrics of the songs
def flushLyrics(path):
	dummy_ext=song_path[-4:].lower() #just the extension
	try:
		if(dummy_ext == ".m4a"):
			song = MP4(song_path)
			song.pop("©lyr")
			song.save()
		elif(dummy_ext == ".flac"):
			song = FLAC(song_path)
			song.pop("LYRICS")
			song.save()
		return [True,dummy_ext]
	except Exception as e:
		print(e)
		return [False,None]


#process each song by searching and saving the lyrics
def scanFolder(path,isFlush=False):
	for root, directories, files in os.walk(path, topdown=True):
		for name in files:
			song_path=str(os.path.join(root, name))
			if(isFlush):
				flushLyrics(song_path)
			elif(not lyricsExists(song_path)): #if do not have the lyrics 
				lyricstxt = searchLyrics(song_path)
				res_store = storeLyrics(song_path,lyricstxt)


########################################################################

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
		scanFolder(sys.argv[2])
		print("Done!")
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