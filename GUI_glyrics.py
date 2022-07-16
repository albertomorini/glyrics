import PySimpleGUI as sg
import os
import platform
import darkdetect
import sys

sys.path.insert(0, '.')
import glyrics as glyrics



########################################################################


def loadingWindow(dirPath):
	menu_def = [['File', ['Open', 'Save', 'Exit',]],['Edit', ['Paste', ['Special', 'Normal',], 'Undo'],],['Help', 'About...']]

	bgColor="#202020"
	colorButton=('white',"#7f95c1")

	layout = [
		[sg.Menu(menu_def)],
		[sg.Text('Scanning your library, please wait...',font=("Helvetica 23"), background_color=bgColor,size=(30, 1))],
		#TODO: add an animation or a timer
	]
	window = sg.Window('glyrics', layout, background_color=bgColor)

	#glyrics.scanFolder(dirPath)

	while True: #keep window open
		event,values=window.read()
		if event == sg.WIN_CLOSED or event=='Cancel':
			break
			window.close()
		if event == 'Submit':
			dirPath =values[1]
			glyrics.scanFolder(dirPath)
			window.close()
			loadingWindow(dirPath[1])


def main():
	menu_def = [['File', ['Open', 'Save', 'Exit',]],['Edit', ['Paste', ['Special', 'Normal',], 'Undo'],],['Help', 'About...']]

	bgColor="#202020"
	colorButton=('white',"#7f95c1")

	layout = [
		[sg.Menu(menu_def)],
		[sg.Text('Welcome on glyrics!',font=("Helvetica 23"), background_color=bgColor)],
		[sg.Text('Pick your music libary folder', font=("Helvetica 18"), background_color=bgColor, size=(30, 1)), sg.InputText(font=("Helvetica 15")), sg.FolderBrowse(font=("Helvetica 15"))],
		[
			sg.Submit(font=("Helvetica 15"), size=(15,1), button_color=colorButton),
			sg.Button("Delete lyrics", button_color=('white', 'red'),font=("Helvetica 15"), key="delButton")
		]
	]
	window = sg.Window('glyrics', layout, background_color=bgColor)

	while True: #keep window open
		event,values=window.read()
		if event == sg.WIN_CLOSED or event=='Cancel':
			break
			window.close()
		if event == 'Submit':
			dirPath =values[1]
			window.close()
			loadingWindow(dirPath)
			


main()