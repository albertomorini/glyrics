import os
import sys
import lyricsgenius as genius
from tinytag import TinyTag
from mutagen.mp4 import MP4

APIkey_genius= "Fbn65vLE84Ji1Le4hZaZmjXbsUHrvV64ZgLdml3qEcwIMr8z0cPj6dBL8fDy_TJE"
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
def lyricsExists(pathSong):
	try:
		song = MP4(pathSong)
		if(song["©lyr"] != None): #if the tag exists we suppose that's already a lyrics
			return True
		else:
			return False #has the tag but empty value
	except Exception as e:
		#the lyrics tag doesn't exists
		return False

#store the lyrics to the M4A song
def storeLyricsM4A(pathSong, lyrics):
	song = MP4(pathSong)
	song["©lyr"] = lyrics
	song.save()


########################################################################

#DANGER: erase the lyrics of the songs
def flushLyrics(path):
	x = str(input("Insert 'suRe' if you're really sure"))
	if (x=='suRe'):
		for root, directories, files in os.walk(path, topdown=True):
			for name in files:
				pathTmp=str(os.path.join(root, name))
				if(pathTmp.endswith(".m4a")):
					song = MP4(pathTmp)
					song.pop("©lyr")
					song.save()


#return the paths of the songs that doesn't have a lyrics
def processFolder(path):

	dictSongs = {
		"numSongs":0,
		"lyricsAlreadyExists":0
	}

	for root, directories, files in os.walk(path, topdown=True):
		for name in files:
			pathTmp=str(os.path.join(root, name))						
			dictSongs["numSongs"]+=1
			if(pathTmp.endswith(".m4a")): #TODO: and not in json already searched?

				if (lyricsExists(pathTmp)):
					dictSongs["lyricsAlreadyExists"]+=1
				else:
					lyrics = searchLyrics(pathTmp)
					if(lyrics!=None):
						storeLyricsM4A(pathTmp,lyrics)

			#TODO: print(dictSongs["numSongs"]) -> for gui?? like "I'm on the n-th song of i dunno haven't scanned all yet ahah"
	return dictSongs


########################################################################

if(len(sys.argv)>1):
	if(sys.argv[1]=="Flush"):
		flushLyrics(sys.argv[2])
	if(sys.argv[1]=="search"):
		dictSongs = processFolder(sys.argv[2])
		print(dictSongs)
		print("Done!")
else:
	"function directory"

