import os
import sys
import lyricsgenius as genius
from tinytag import TinyTag
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT
import hashlib
import json

## GENIUS STUFF
APIkey_genius= open("./genius_APIKEY.txt","r").read()
genius = genius.Genius(APIkey_genius)
genius.skip_non_songs = False #we search also the songs without lyrics (eg soundtrack) in the way to mark them as founded (already searched).

########################################################################
# UTILITY

def serializeJSON(dir, filename, dataDictionary):
	with open(dir+"/"+filename,"w", encoding='utf-8') as fileToStore:
   		json.dump(dataDictionary, fileToStore, ensure_ascii=False)

def readJson(path):
	try:
		with open(path) as dataStored:
			return json.load(dataStored)
	except Exception as e:
		print("Exception: config file not exists/not a json")
		return None

def doMD5(digest):
	return hashlib.md5(digest.encode()).hexdigest()

########################################################################

#return None if the lyrics isn't found, could be because the songs hasn't enough info (title, artist)
def searchLyrics(pathSong):
	try:
		metaData = TinyTag.get(pathSong)
		info = genius.search_song(metaData.title.split("(")[0],metaData.artist) #split to remove the "feat"/"remix" etc. look at readme.md
		return info.lyrics

	except Exception as e:
		return None

#store the lyrics to the M4A song
def storeLyricsM4A(pathSong, lyrics):
	try:
		song = MP4(pathSong)
		song["©lyr"] = lyrics
		song.save()
		return True
	except Exception as e:
		return False

#store the lyrics to the MP3 song
def storeLyricsMP3(pathSong, lyrics):
	try:
		song = ID3(pathSong)
		song["USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
		song.save()
		return True
	except Exception as e:
		return False

########################################################################


#DANGER: erase the lyrics of the songs
def flushLyrics(path):
	x = str(input("Insert 'suRe' if you're really sure\n"))
	if (x=='suRe'):
		for root, directories, files in os.walk(path, topdown=True):
			for name in files:
				pathTmp=str(os.path.join(root, name))
				try:
					if(pathTmp.endswith(".m4a")):
						song = MP4(pathTmp)
						song.pop("©lyr")
						song.save()
						print("Removed lyrics for :",name)
					elif(pathTmp.endswith(".mp3")):
						song = ID3(i)
						song.pop("USLT::'eng'")
						song.save()
						print("Removed lyrics for :",name)
					
				except Exception as e: ## whenever a single song do not have the lyrics we will skip it
					pass

#search a previous registry of song searched, if there isn't will create a new one
def checkRegistry(path):
	pref = readJson(path)
	if(pref==None):
		pref = {
			"alreadySearched": [],
			"numMP3":0,
			"numM4A":0
		}
	return pref


#process each song by searching and saving the lyrics
def scanFolder(path):
	dictSongs = checkRegistry(path+"/glyrics.json") #configuration file, stored on @param path
	for root, directories, files in os.walk(path, topdown=True):
		for name in files:
			pathTmp=str(os.path.join(root, name))
			if(doMD5(pathTmp) not in dictSongs.get("alreadySearched")): #if song is never been searched or hasn't got lyrics

				lyrics = searchLyrics(pathTmp)
				if(pathTmp.endswith(".m4a")):
					dictSongs["numM4A"]+=1
					if(lyrics!=None and storeLyricsM4A(pathTmp,lyrics)): #lyrics found, store and save the hash of song (to avoid a rescan)
						dictSongs.get("alreadySearched").append(doMD5(pathTmp))

				elif(pathTmp.endswith(".mp3")):
					dictSongs["numMP3"]+=1
					if(lyrics!=None and storeLyricsMP3(pathTmp,lyrics)): #lyrics found, store and save the hash of song (to avoid a rescan)
						dictSongs.get("alreadySearched").append(doMD5(pathTmp))

	return dictSongs

#############################################################################
#start the program, let choose two option: "Flush" -> erease the previous lyrics, "search" -> scan the folder
def main():
	if(len(sys.argv)>1):
		if(sys.argv[1].upper()=="FLUSH"):
			flushLyrics(sys.argv[2])
		elif(sys.argv[1].upper()=="SEARCH"):
			dictSongs = scanFolder(sys.argv[2])
			print(dictSongs)
			serializeJSON(sys.argv[2],"glyrics.json",dictSongs)
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