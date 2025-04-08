import os
import sys
import lyricsgenius as genius
from tinytag import TinyTag
from mutagen.mp4 import MP4

APIkey_genius= "Fbn65vLE84Ji1Le4hZaZmjXbsUHrvV64ZgLdml3qEcwIMr8z0cPj6dBL8fDy_TJE"
genius = genius.Genius(APIkey_genius)


#song = MP4("/Volumes/Media/Music/Music/Kendrick Lamar/DAMN_/10 LOVE, (FEAT. ZACARI.).m4a")
#print(song["title"])


metaData = TinyTag.get("/Volumes/Media/Music/Music/Kendrick Lamar/DAMN_/10 LOVE. (FEAT. ZACARI.).m4a")
print(metaData.title)
print(metaData.genre)
print(metaData.extra)
print(metaData.year)
print(metaData.albumartist)


'''


IDEA:

2 grafi: uno libreria locale, l'altro dato un artista scarico 50 artisti associati (featuring)

	grafo con della libreria musicale (networkX + pyvis).
		-> nodi = artisti, grandi quanto il numero di canzoni (pyvis)
		-> archi= featuring. (quindi cerco i "feat"), metto le canzoni come attributi

	secondo grafo, sottoinsieme degli stessi generi musicali
	terzo grafo, linea temporale con album dello stesso anno
		-> nodi = gli anni e gli album
		-> archi= associazione anno-album

'''