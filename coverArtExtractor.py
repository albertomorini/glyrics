import os
import subprocess

#ffmpeg_cmd = "ffmpeg -i t.m4a -an cover.jpg"

#process each song by searching and saving the lyrics
def scanFolder(path):
    for root, directories, files in os.walk(path, topdown=True):
        for name in files:
            pathTmp=str(os.path.join(root, name))
            if(pathTmp.endswith(".m4a") or pathTmp.endswith("mp3")):
                os.chdir(root) # go to albyh
                mycmd = "no | ffmpeg -i ./"+name.replace(" ",r'\ ')+" -an ./cover.jpg ;" # yes/no to pipe the overwrite to ffmpeg to replace the coverart whenever already present
                subprocess.run(mycmd, shell=True) # shell=True to manage whitespace and some other characters
                continue

scanFolder("/Volumes/MEDIA/MUSIC/")