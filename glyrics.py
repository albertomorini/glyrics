import os
import sys
import lyricsgenius as genius
from tinytag import TinyTag
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC


APIkey_genius= "Fbn65vLE84Ji1Le4hZaZmjXbsUHrvV64ZgLdml3qEcwIMr8z0cPj6dBL8fDy_TJE"
genius = genius.Genius(APIkey_genius)
genius.skip_non_songs = False #we search also the songs without lyrics (eg soundtrack) in the way to mark them as founded (already searched).

import python_utility as pyut


########################################################################
#
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
	song = MP4(pathSong)
	song["©lyr"] = lyrics
	song.save()

#store the lyrics to the MP3 song
def storeLyricsMP3(pathSong, lyrics):
	song = ID3(pathSong)
	song["USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
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
				elif(pathTmp.endswith(".mp3")):
					song = ID3(i)
					song.pop("USLT::'eng'")
					song.save()

#search a previous configuration, if there isn't will create a new one
def checkJson(path):
	pref = pyut.read_JSON(path)
	if(pref!=None):
		return pref
	else:
		dictSongs = {
			"alreadySearched": [],
			"numMP3":0,
			"numM4A":0
		}
		return dictSongs


#process each song by searching and saving the lyrics
def scanFolder(path):

	dictSongs = checkJson(path+"/glyrics.json") #configuration file, stored on @param path

	for root, directories, files in os.walk(path, topdown=True):
		for name in files:

			pathTmp=str(os.path.join(root, name))

			if(pyut.doHashMD5(pathTmp) not in dictSongs.get("alreadySearched")):
			#song is never been searched or it's never found the lyrics

				if(pathTmp.endswith(".m4a")):
					dictSongs["numM4A"]+=1
					lyrics = searchLyrics(pathTmp)
					if(lyrics!=None):
						storeLyricsM4A(pathTmp,lyrics)
						dictSongs.get("alreadySearched").append(pyut.doHashMD5(pathTmp))

				elif(pathTmp.endswith(".mp3")):
					dictSongs["numMP3"]+=1
					lyrics = searchLyrics(pathTmp)
					if(lyrics!=None):
						storeLyricsMP3(pathTmp,lyrics)
						dictSongs.get("alreadySearched").append(pyut.doHashMD5(pathTmp))

	return dictSongs

#start the program, let choose two option: "Flush" -> erease the previous lyrics, "search" -> scan the folder
def main():
	if(len(sys.argv)>1):
		if(sys.argv[1]=="Flush"):
			flushLyrics(sys.argv[2])
		if(sys.argv[1]=="search"):
			dictSongs = scanFolder(sys.argv[2])
			print(dictSongs)

			pyut.serialize_JSON(sys.argv[2],"glyrics.json",dictSongs)
			print("Done!")
	else:
		"function directory"


main()
