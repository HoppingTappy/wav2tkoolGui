from struct import (unpack, pack, pack_into)


class WavFile:


	def __init__(self):
		self.Header = self.WavHeader()
		self.Chunk = self.WavChunk()

	def read(self, filePath):

		data = open(filePath,'rb')

		self.Header.read(data)
		self.Chunk.read(data, self.Header)

		data.close()

	def write(self, filePath):

		file = open(filePath,"wb")

		data = bytearray(self.Header.write())


		offset = len(data)
		data += self.Chunk["fmt "].write()
		pack_into("<I", data, offset+4, len(data)-(offset+8))

		offset = len(data)
		data += self.Chunk["data"].write()
		pack_into("<I", data, offset+4, len(data)-(offset+8))


		for key in self.Chunk.keys():
			if key == "fmt " or key == "data":
				continue
			offset = len(data)
			data += self.Chunk[key].write()

			pack_into("<I", data, offset+4, len(data)-(offset+8))


		pack_into("<I", data, 4, len(data) - 8 )

		file.write(data)
		file.close()

	def setFmt(self, ch=2, bit=16, sampleRate=48000):

		key = "fmt "
		self.Chunk[key].NumChannels = ch
		self.Chunk[key].Bit = bit
		self.Chunk[key].SampleRate = sampleRate
		self.Chunk[key].BlockAlign = self.Chunk[key].NumChannels * (i.Bit//8)
		self.Chunk[key].Bps = self.Chunk[key].SampleRate * self.Chunk[key].BlockAlign

		return

	def remove(self, id):
		self.Chunk.pop(id)

	def add(self, id):
		self.Chunk[id] = self.Chunk.options.get(id, self.Chunk.noMatch)()

	def addFmt(self):
		self.Chunk["fmt "] = self.WavChunk.chunkFmt()

	def addData(self):
		self.Chunk["data"] = self.WavChunk.chunkData()

	def setData(self, data):
		key = "data"
		self.Chunk[key].Data = data
		return

	def addSmpl(self):
		self.Chunk["smpl"] = self.WavChunk.chunkSmpl()

	def setSmpl(self, start, end):
		key = "smpl"
		self.Chunk[key].NumSampleLoops = self.Chunk[key].NumSampleLoops + 1
		self.Chunk[key].CuePointID.append( 0 )
		self.Chunk[key].Type.append( 0 )
		self.Chunk[key].Start.append( start )
		self.Chunk[key].End.append( end )
		self.Chunk[key].Fraction.append( 0 )
		self.Chunk[key].PlayCount.append( 0 )
		return


	def checkChunk(self, idText):

		return self.Chunk.get(idText)

	def getChunkNum(self, idText):
		for i,chunk in enumerate(self.Chunk):
			if (chunk.Id==idText):
				return i

		return -1

	class WavHeader:
		def __init__(self):
			self.Id = "RIFF"
			self.Size = 0
			self.FileType = "WAVE"
			return

		def read(self, data):
			self.Id = data.read(4).decode("ascii")
			self.Size = unpack("<I" ,data.read(4))[0]
			self.FileType = data.read(4).decode("ascii")

		def write(self):
			data = pack("4s", self.Id.encode("ascii") )
			data += pack("<I", 0)
			data += pack("4s", self.FileType.encode("ascii"))
			return data




	class WavChunk(dict):



		def __init__(self):
			dict.__init__(self)


			self.options = {
				"fmt "						:self.chunkFmt,
				"data"						:self.chunkData,
				"smpl"						:self.chunkSmpl,
			}

			return

		def read(self,data,header):


			while data.tell() < header.Size + 8:

				id = data.read(4).decode("ascii")
				size = unpack("<I" ,data.read(4))[0]
				offsetAddr = data.tell()

#				self.append( options.get(id, self.noMatch)() )
				self[id] = self.options.get(id, self.noMatch)()

				self[id].Id = id
				self[id].Size = size

				self[id].read(data)

				data.seek(offsetAddr + size,0)

			return

		def write(self, data):
			self.write

			return

		class noMatch:

			def __init__(self):
				self.Id = ""
				self.Size = 0
				return

			def read(self, data):
				self.Data = data.read(self.Size)
		#		print(self.Id,self.Size,self.Data)
				return

			def write(self):
				data = pack("4s" , self.Id.encode("ascii") )
				data += pack("<I" , 0)
		#		data += pack(str(self.Size)+"B",*self.Data)
				data += self.Data
				return data

		class chunkFmt():
			def __init__(self):

				self.Id = "fmt "
				self.Size = 0

				self.CompCode = 1
				self.NumChannels = 2
				self.Bit = 16
				self.SampleRate = 48000
				self.BlockAlign = self.NumChannels + (self.Bit//8)
				self.Bps = self.SampleRate * self.BlockAlign

				self.ExSize = 0
				self.ExData = 0

				return

			def read(self, data):

				self.CompCode = unpack("<H" ,data.read(2))[0]
				self.NumChannels = unpack("<H" ,data.read(2))[0]
				self.SampleRate = unpack("<I" ,data.read(4))[0]
				self.Bps = unpack("<I" ,data.read(4))[0]
				self.BlockAlign = unpack("<H" ,data.read(2))[0]
				self.Bit = unpack("<H" ,data.read(2))[0]
				if self.CompCode != 1:
					self.ExSize = unpack("<H" ,data.read(2))[0]
					self.ExData = data.read(self.ExSize)
		#			for i in range(self.exSize):

				return

			def write(self):
				data = pack("4s" , self.Id.encode("ascii") )
				data += pack("<I" , 0)
				data += pack("<H" , self.CompCode		)
				data += pack("<H" , self.NumChannels	)
				data += pack("<I" , self.SampleRate		)
				data += pack("<I" , self.Bps			)
				data += pack("<H" , self.BlockAlign		)
				data += pack("<H" , self.Bit			)
				if self.CompCode != 1:
					data += pack("<H" , self.ExSize			)
					data += self.ExData

				return data

		class chunkData():
			def __init__(self):

				self.Id = "data"
				self.Size = 0

				self.Data = 0
				return

			def read(self, data):
				self.Data = bytearray(data.read(self.Size))
				return

			def write(self):
				data = pack("4s" , self.Id.encode("ascii") )
				data += pack("<I" , 0)

				data += self.Data

				if WavFile.isEven( len(data) ):
					pass
				else:
		#			data += b"\x80"
					data += data[len(data)-1].to_bytes(1,"little")
				return data

		class chunkSmpl():
			def __init__(self):

				self.Id = "smpl"
				self.Size = 0

				self.Manufacturer = 0
				self.Product = 0
				self.SamplePeriod = 0
				self.MIDIUnityNote = 60
				self.MIDIPitchFraction = 0
				self.SMPTEFormat = 0
				self.SMPTEOffset = 0
				self.NumSampleLoops = 0
				self.SamplerData = 0


				self.CuePointID = []
				self.Type = []
				self.Start = []
				self.End = []
				self.Fraction = []
				self.PlayCount = []
				return

			def read(self, data):

				self.Manufacturer = unpack("<I" ,data.read(4))[0]
				self.Product = unpack("<I" ,data.read(4))[0]
				self.SamplePeriod = unpack("<I" ,data.read(4))[0]
				self.MIDIUnityNote = unpack("<I" ,data.read(4))[0]
				self.MIDIPitchFraction = unpack("<I" ,data.read(4))[0]
				self.SMPTEFormat = unpack("<I" ,data.read(4))[0]
				self.SMPTEOffset = unpack("<I" ,data.read(4))[0]
				self.NumSampleLoops = unpack("<I" ,data.read(4))[0]
				self.SamplerData = unpack("<I" ,data.read(4))[0]


				for i in range(self.NumSampleLoops):

					self.CuePointID.append( unpack("<I" ,data.read(4))[0] )
					self.Type.append( unpack("<I" ,data.read(4))[0] )
					self.Start.append( unpack("<I" ,data.read(4))[0] )
					self.End.append( unpack("<I" ,data.read(4))[0] )
					self.Fraction.append( unpack("<I" ,data.read(4))[0] )
					self.PlayCount.append( unpack("<I" ,data.read(4))[0] )


				return

			def write(self):
				data = pack("4s" , self.Id.encode("ascii") )
				data += pack("<I" , 0)

				data += pack("<I" , self.Manufacturer		)
				data += pack("<I" , self.Product			)
				data += pack("<I" , self.SamplePeriod		)
				data += pack("<I" , self.MIDIUnityNote		)
				data += pack("<I" , self.MIDIPitchFraction	)
				data += pack("<I" , self.SMPTEFormat		)
				data += pack("<I" , self.SMPTEOffset		)
				data += pack("<I" , self.NumSampleLoops		)
				data += pack("<I" , self.SamplerData		)

				for i in range(self.NumSampleLoops):
					data += pack("<I" , self.CuePointID[i]		)
					data += pack("<I" , self.Type[i]			)
					data += pack("<I" , self.Start[i]			)
					data += pack("<I" , self.End[i]				)
					data += pack("<I" , self.Fraction[i]		)
					data += pack("<I" , self.PlayCount[i]		)

				return data

	def isEven(num):
		return num % 2 == 0