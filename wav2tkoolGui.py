#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
import wavFile
import m4aFile
import subprocess
import platform
import tkinter as tk
import tkinter.filedialog

def main():


	if platform.system() == "Windows":
		isWindows = True
	else:
		isWindows = False

	if isWindows:
		ext = ".exe"
	else:
		ext = ""

#	soxPath = Path(Path(__file__).resolve().parent.parent / "sox/sox.exe").resolve()

	ffmpegFileName = "ffmpeg" + ext
	ffmpegPath = Path(Path(__file__).resolve().parent / ffmpegFileName).resolve()

	if not ffmpegPath.exists():
		print(ffmpegFileName +" が見つかりません")
		tkinter.messagebox.showwarning("", ffmpegFileName +" が見つかりません")
		return

	root = tk.Tk()
	root.withdraw()

	fileType = [("", "*.wav")]
	dirPath = Path(Path(__file__))
	files = tk.filedialog.askopenfilenames(filetypes=fileType, initialdir=dirPath)
	print(files)

	for f in files:
		wav2tkool(Path(f),ffmpegPath)


#	targetFreq = args.freq

#	targetPath = inPath.with_stem(inPath.stem + "_"+str(targetFreq))

def wav2tkool(inPath,ffmpegPath):

	srcWav = wavFile.WavFile()
	srcWav.read(inPath)


	if srcWav.checkChunk("smpl"):
		loopEnable = True
		loopStartPoint = srcWav.Chunk["smpl"].Start[0]
		loopEndPoint = srcWav.Chunk["smpl"].End[0]
		loopLength = loopEndPoint - loopStartPoint

#		srcSampleRate = srcWav.Chunk["fmt "].SampleRate
#		loopStartPoint = int(loopStartPoint * targetFreq / srcSampleRate)
#		loopEndPoint = int(loopEndPoint * targetFreq / srcSampleRate)
	else:
		loopEnable = False

#	cp = subprocess.run([soxPath, str(inPath), "-r 48000", str(targetPath)])

#	targetWav = wavFile.WavFile()
#	targetWav.read(targetPath)
#
#	if loopEnable:
#		targetWav.add("smpl")
#		targetWav.setSmpl(loopStartPoint,loopEndPoint)
#
#		byteLength = targetWav.Chunk["fmt "].BlockAlign
#		targetWav.Chunk["data"].Data = targetWav.Chunk["data"].Data[:(loopEndPoint+1)*byteLength]

#	targetWav.write(inPath)
#	targetPath.unlink()




	if loopEnable:
		cp = subprocess.run([ffmpegPath, "-y","-i",str(inPath),"-vn",'-metadata','LOOPSTART=' + str(loopStartPoint),'-metadata','LOOPEND=' + str(loopEndPoint),'-metadata','LOOPLENGTH=' + str(loopLength),"-acodec","libvorbis", "-f", "ogg",inPath.with_suffix(".ogg")])
		cp = subprocess.run([ffmpegPath, "-y","-i",str(inPath),"-vn",'-metadata','LOOPSTART=' + str(loopStartPoint),'-metadata','LOOPEND=' + str(loopEndPoint),'-metadata','LOOPLENGTH=' + str(loopLength),"-acodec","aac"      , "-f", "mp4",inPath.with_suffix(".m4a")])

		m4a = m4aFile.M4aFile()
		m4a.read(inPath.with_suffix(".m4a"))
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"].add("----")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("name")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["name"].setData("LOOPSTART")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("data")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["data"].setData(str(loopStartPoint))


		m4a.Chunks["moov"]["udta"]["meta"]["ilst"].add("----")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("name")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["name"].setData("LOOPLENGTH")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("data")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["data"].setData(str(loopLength))

		m4a.Chunks["moov"]["udta"]["meta"]["ilst"].add("----")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("name")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["name"].setData("LOOPEND")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("data")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["data"].setData(str(loopEndPoint))

		m4a.write(inPath.with_suffix(".m4a"))

	else:
		cp = subprocess.run([ffmpegPath, "-y","-i",str(inPath),"-vn","-acodec","libvorbis", "-f", "ogg",inPath.with_suffix(".ogg")])
		cp = subprocess.run([ffmpegPath, "-y","-i",str(inPath),"-vn","-acodec","aac"      , "-f", "mp4",inPath.with_suffix(".m4a")])



if __name__ == "__main__":
	main()
