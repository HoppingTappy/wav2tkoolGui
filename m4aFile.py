from struct import (unpack, pack, pack_into)

import pprint
class M4aFile:


	def __init__(self):
		self.Chunks = self.M4aChunk()

	def read(self, filePath):

		data = open(filePath,'rb')

		self.Chunks.read(data)

		data.close()

	def write(self, filePath):

		file = open(filePath,"wb")

		data = bytearray()

		for key in self.Chunks:
			data+=self.Chunks[key].write()

		file.write(data)
		file.close()

	def remove(self, name):
		pprint.pprint(self.Chunks)
		self.Chunks.pop(name)

	def add(self, name):
		self.Chunks[name] = M4aFile.options.get(name, M4aFile.noMatch)()



	def checkChunk(self, idText):

		return self.Chunks.get(idText)

	def getChunkNum(self, idText):
		for i,chunk in enumerate(self.Chunks):
			if (chunk.Id==idText):
				return i

		return -1



	class M4aChunk(dict):



		def __init__(self):
			dict.__init__(self)

			return

		def read(self,data):
			fileSize = len(data.read())
			data.seek(0)
			while data.tell() < fileSize:
				offsetAddr = data.tell()
				expandFlag = False
				seekByte = 8
				size = unpack(">I" ,data.read(4))[0]
				if size==1:
					expandFlag = True
					seekByte = 16

				name = data.read(4).decode("shift-jis")
				if expandFlag:
					size = unpack(">Q" ,data.read(8))[0]

				data.seek(-seekByte,1)

				self[name] = M4aFile.options.get(name, M4aFile.noMatch)()
				self[name].parent = self
#				self[name].size = size
#				self[name].name = name
				self[name].read(data)

				data.seek(offsetAddr + size,0)

			return


	class noMatch:

		def __init__(self):
			self.name = ""
#			self.size = 0
			self.data = bytearray()
			return

		def read(self, data):
			expandFlag = False
			seekByte = 8
			size = unpack(">I" ,data.read(4))[0]
			if size==1:
				expandFlag = True
				seekByte = 16

			self.name = data.read(4).decode("shift-jis")
			if expandFlag:
				size = unpack(">Q" ,data.read(8))[0]

			self.data = data.read(size-seekByte)
			return

		def write(self):
			data = bytearray()
			if self.name=="hdlr" and self.parent.name=="meta":
				data += pack(">Q" , len(self.data)+8)
			else:
				data += pack(">I" , len(self.data)+8)
			data += pack("4s" , self.name.encode("shift-jis") )
			data += self.data
			return data

		def remove(self):
#			self.parent.size -= self.size
			self.parent.pop(self.name)

		def add(self,name):
			self[name] = M4aFile.options.get(name, M4aFile.noMatch)()
			self[name].parent = self
			self[name].name = name

		def setData(self,data):
			self.data = bytearray()
			if self.name=="data":
				self.data += pack(">I",1)
			self.data += pack(">I",0)
			self.data += pack(str(len(data))+"s" , data.encode("shift-jis") )


		def clear(self):
			self.data = bytearray()

	class subChunk(dict):
		def __init__(self):
			dict.__init__(self)
			self.name = ""
			return

		def read(self, data):
			size = unpack(">I" ,data.read(4))[0]
			self.name = data.read(4).decode("shift-jis")
			endAddr = data.tell()+size-8

			while data.tell() < endAddr:
				offsetAddr = data.tell()
				expandFlag = False
				seekByte = 8
				size = unpack(">I" ,data.read(4))[0]
				if size==0:
					size = unpack(">I" ,data.read(4))[0]
					offsetAddr+=4


				if size==1:
					expandFlag = True
					seekByte = 16

				name = data.read(4).decode("shift-jis")
				if expandFlag:
					size = unpack(">Q" ,data.read(8))[0]

				data.seek(-seekByte,1)
				self[name] = M4aFile.options.get(name, M4aFile.noMatch)()
				self[name].parent = self
				self[name].read(data)

				data.seek(offsetAddr + size,0)
			return

		def write(self):
			data = bytearray()
			data += pack(">I" , 0)
			data += pack("4s" , self.name.encode("shift-jis") )
			for key in self:
				data+=self[key].write()
			data[:4] = pack(">I" , len(data))
			return data

		def remove(self):
			self.parent.pop(self.name)


		def add(self,name):
			self[name] = M4aFile.options.get(name, M4aFile.noMatch)()
			self[name].parent = self
			self[name].name = name

	class ilstChunk(list):
		def __init__(self):
			list.__init__(self)
			self.name = ""
			return

		def read(self, data):
			size = unpack(">I" ,data.read(4))[0]
			self.name = data.read(4).decode("shift-jis")
			endAddr = data.tell()+size-8
			while data.tell() < endAddr:
				offsetAddr = data.tell()
				expandFlag = False
				seekByte = 8
				size = unpack(">I" ,data.read(4))[0]
				if size==0:
					size = unpack(">I" ,data.read(4))[0]


				if size==1:
					expandFlag = True
					seekByte = 16

				name = data.read(4).decode("shift-jis")
				if expandFlag:
					size = unpack(">Q" ,data.read(8))[0]

				data.seek(-seekByte,1)
				self.append( M4aFile.options.get(name, M4aFile.noMatch)() )
				self[-1].parent = self
				self[-1].read(data)

				data.seek(offsetAddr + size,0)
			return

		def write(self):
			data = bytearray()
			data += pack(">I" , 0)
			data += pack("4s" , self.name.encode("shift-jis") )
			for l in self:
				data+=l.write()
			data[:4] = pack(">I" , len(data))
			return data

		def remove(self):
			self.parent.pop(self.name)


		def add(self,name):
			self.append(M4aFile.options.get(name, M4aFile.noMatch)())
			self[-1].parent = self
			self[-1].name = name

	options = {
		"moov"						:subChunk,
		"udta"						:subChunk,
		"trak"						:subChunk,
		"mdia"						:subChunk,
		"minf"						:subChunk,
		"edts"						:subChunk,
		"stbl"						:subChunk,
		"meta"						:subChunk,
		"ilst"						:ilstChunk,
#		"data"						:subChunk,
#		"ｳtoo"						:subChunk,
		"----"						:subChunk,
#		"name"						:nameChunk,
	}

	def isEven(num):
		return num % 2 == 0