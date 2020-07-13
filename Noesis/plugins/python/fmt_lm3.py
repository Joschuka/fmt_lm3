from inc_noesis import *
import os
import pickle
import zlib
import math

#Version 1.1

# =================================================================
# Plugin options
# =================================================================

globalPath = None

bLoadMaterials = True
bLoadAnimations = True

#You can use these fields if the skeleton is misplaced for some reason.
skelPosCorrection = NoeVec3([0,0,0])
skelRotCorrection = NoeAngles([0,0,0])



# =================================================================
# Misc
# =================================================================

def registerNoesisTypes():
	handle = noesis.register("Luigi's Mansion 3 dictionnary",".dict")
	noesis.setHandlerTypeCheck(handle, CheckDictType)
	noesis.setHandlerLoadModel(handle, ExtractDict)
	handle = noesis.register("Luigi's Mansion 3 texture",".lm3t")
	noesis.setHandlerTypeCheck(handle, CheckTextureType)
	noesis.setHandlerLoadRGBA(handle, LoadRGBA)
	handle = noesis.register("Luigi's Mansion 3 model",".lm3m")
	noesis.setHandlerTypeCheck(handle, CheckModelType)
	noesis.setHandlerLoadModel(handle, LoadModel)
	return 1

def getFileNum(fileNum,isGlobal=False):
	if isGlobal:
		result = globalPath + os.sep + "File_Data" + os.sep + "global_" + str(fileNum) + '.lm3'
	else:
		result = filePath + os.sep + os.path.basename(os.path.dirname(filePath)) + '_' + str(fileNum) + '.lm3'
	return result
	
def InitializeFromDict():
	
	global dataFileName
	dataFileName = rapi.getInputName()[:-5] + ".data"
	if not rapi.checkFileExists(dataFileName):
		print("Associated data file not found")
	
	#file paths
	global destPath
	global textPath
	global modelPath
	global animPath
	global animBundlePath
	global filePath
	destPath = os.path.dirname(rapi.getInputName()) + os.sep + rapi.getLocalFileName(dataFileName)[:-5]
	modelPath = destPath + os.sep + "Models"
	textPath = destPath + os.sep + "Textures"
	animPath = destPath + os.sep + "Animations"
	animBundlePath = destPath + os.sep + "AnimationPacks"
	filePath = destPath + os.sep + "File_Data"	
	
	if not os.path.exists(modelPath):
		os.makedirs(modelPath)
	if not os.path.exists(textPath):
		os.makedirs(textPath)
	if not os.path.exists(animPath):
		os.makedirs(animPath)
	if not os.path.exists(animBundlePath):
		os.makedirs(animBundlePath)	
	if not os.path.exists(filePath):
		os.makedirs(filePath)	

def InitializeFromAsset():
	global textureList
	textureList = []
	global modelList
	modelList = []
	global animationList
	animationList = []
	global textureHashToIndex
	textureHashToIndex = {}	

	global rootPath
	rootPath = os.path.dirname(rapi.getInputName())
	rootPath = os.path.dirname(rootPath)
	
	#file paths
	global textPath
	global modelPath
	global animPath
	global filePath
	modelPath = rootPath + os.sep + "Models"
	textPath = rootPath + os.sep + "Textures"
	animPath = rootPath + os.sep + "Animations"
	animBundlePath = rootPath + os.sep + "AnimationPacks"
	filePath = rootPath + os.sep + "File_Data"	
	
	if not os.path.exists(modelPath):
		os.makedirs(modelPath)
	if not os.path.exists(textPath):
		os.makedirs(textPath)
	if not os.path.exists(animPath):
		os.makedirs(animPath)
	if not os.path.exists(animBundlePath):
		os.makedirs(animBundlePath)	
	if not os.path.exists(filePath):
		os.makedirs(filePath)

def InitializeFileStream(num):
	#file streams
	if num == 0:		
		global bs0
		if rapi.checkFileExists(getFileNum(0)):
			bs0 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(0)))
			bs0.setEndian(NOE_LITTLEENDIAN)
		else:
			print("file 0 not found")
	elif num == 52:
		global bs52
		if rapi.checkFileExists(getFileNum(52)):
			bs52 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(52)))
			bs52.setEndian(NOE_LITTLEENDIAN)
		else:
			print("file 52 not found")
	elif num == 53:
		global bs53
		if rapi.checkFileExists(getFileNum(53)):
			bs53 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(53)))
			bs53.setEndian(NOE_LITTLEENDIAN)
		else:
			print("file 53 not found")
	elif num == 54:
		global bs54
		if rapi.checkFileExists(getFileNum(54)):
			bs54 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(54)))
			bs54.setEndian(NOE_LITTLEENDIAN)
		else:
			print("file 54 not found")
	elif num == 63:
		global bs63
		if rapi.checkFileExists(getFileNum(63)):
			bs63 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(63)))
			bs63.setEndian(NOE_LITTLEENDIAN)
		else:
			print("file 63 not found")
	elif num == 65:
		global bs65
		if rapi.checkFileExists(getFileNum(65)):
			bs65 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(65)))
			bs65.setEndian(NOE_LITTLEENDIAN)
		else:
			print("file 65 not found")			

# =================================================================
# Noesis check type
# =================================================================

def CheckDictType(data):
	bs = NoeBitStream(data)
	if len(data) < 16:
		print("Invalid dict file, too small")
		return 0
	return 1
	
def CheckModelType(data):
	bs = NoeBitStream(data)
	if len(data) < 16:
		print("Invalid model file, too small")
		return 0
	return 1

def CheckTextureType(data):
	return 1

# =================================================================
# Classes
# =================================================================

class ChunkType1:
	def __init__(self):
		self.id = None
		self.unk1 = None
		self.headerSize = None
		self.headerOffset = None
		self.dataType = None
		self.flags = None
		self.chunkSize = None
		self.chunkOffset = None
		
	def __str__(self):
		return '(ID: '+str(self.id)+', chunkFlag: '+str(self.chunkFlag)+\
		', chunkSize: '+str(self.chunkSize)+', chunkOffset: '+str(self.chunkOffset)+\
		', dataType: '+str(self.dataType)+ ')'
	
	def parse(self, bs):
		self.id = bs.readUShort()
		self.unk1 = bs.readUShort()
		self.headerSize = bs.readUInt()
		self.headerOffset = bs.readUInt()
		self.dataType = bs.readUShort()
		self.flags = bs.readUShort()
		self.chunkSize = bs.readUInt()
		self.chunkOffset = bs.readUInt()

class ChunkType2:
	def __init__(self):
		self.dataType = None
		self.chunkFlag = None
		self.chunkSize = None
		self.chunkOffset = None
		
	def __str__(self):
		return '(chunkFlag: '+str(self.chunkFlag)+\
		', chunkSize: '+str(self.chunkSize)+', chunkOffset: '+str(self.chunkOffset)+\
		', dataType: '+str(self.dataType)+ ')'
	
	def parse(self, bs):
		self.dataType = bs.readUShort()
		self.chunkFlag = bs.readUShort()
		self.chunkSize = bs.readUInt()
		self.chunkOffset = bs.readUInt()

class LM3TextureAsset:
	def __init__(self):
		self.hashName = None
		self.headerOffset = None
		self.headerSize = None
		self.dataOffset = None
		self.dataSize = None

class LM3ModelAsset:
	def __init__(self):
		self.hashName = None
		self.meshAssetList = []
		self.buffersOffset = -1
		self.materialOffsets = []
		self.materialMap = None
		self.pairedTextureFileIndices = []
		self.pairedGlobalTextureFileIndices = []
		self.jointList = []
		self.parentList = []
		self.animationIndices = []
		
		self.boneIDB1ToHash = {}
		self.hashToBoneIDB1 = {}
		self.boneID71ToHash = {}
		self.hashToBoneID71 = {}
		
		
		self.b001Offset = -1
		self.b001Size = -1
		self.b003Offset = -1
		self.b003Size = -1
		self.b004Offset = -1
		self.b004Size = -1
		self.b005Offset = -1
		self.b005Size = -1
		self.b006Offset = -1
		self.b006Size = -1
		self.b007Offset = -1
		self.b007Size = -1
		self.b102Offset = -1
		self.b102Size = -1
		self.b103Offset = -1
		self.b103Size = -1
		self.s7103Offset = -1
		self.s7103Size = -1
		self.s7105Offset = -1
		self.s7105Size = -1
		self.s7106Offset = -1
		self.s7106Size = -1
		
class LM3SkeletonAsset:
	def __init__(self):
		self.pairedModelHashName = None
		self.s7103Offset = -1
		self.s7103Size = -1
		self.s7105Offset = -1
		self.s7105Size = -1
		self.s7106Offset = -1
		self.s7106Size = -1
		
class LM3AnimationAsset:
	def __init__(self):
		self.hashName = None
		self.dataOffset = None
		self.dataSize = None
		
class LM3AnimationBundleAsset:
	def __init__(self):
		self.animationIndices =[]
		
class LM3BoneHeader:
	def __init__(self):
		self.hash = None
		self.index = -1
		self.magic = None
		self.type = -1
		self.opcode = -1
		self.offset = -1

class LM3MeshAsset:
	def __init__(self):
		self.vertexBufferOffset = -1
		self.skinningBufferOffset = -1
		self.indexBufferOffset = -1
		self.indexFormat = None
		
		self.indexCount = -1
		self.vertexCount = -1
		self.isSkinned = None		
	
# =================================================================
# Load texture
# =================================================================

def LoadRGBA(data, texList):
	InitializeFromAsset()
	InitializeFileStream(63)
	InitializeFileStream(65)
	textureAsset = pickle.load(open( rapi.getInputName(), "rb" ))
	processTexture([textureAsset])
	
	for tex in textureList:
		texList.append(tex)
	global bs63, bs65
	del bs63,bs65
	return 1
	
# =================================================================
# Load model
# =================================================================

def LoadModel(data, mdlList):
	ctx = rapi.rpgCreateContext()
	InitializeFromAsset()
	modelAsset = pickle.load(open( rapi.getInputName(), "rb" ))
	processModel([modelAsset])
	for mod in modelList:
		mdlList.append(mod)
	return 1
	
# =================================================================
# Data extraction 
# =================================================================

def ExtractAssets():

	chunkType1List = []
	chunkType2List = []
	
	#Texture 
	textureAssetList = []
	textureHashesToFileIndex = {}
	textureIndex = -1
	#Model
	modelAssetList = []
	modelHashesToFileIndex = {}
	modelIndex = -1
	#Skeleton
	skeletonAssetList = []
	skeletonIndex = -1
	#Animation
	animationAssetList = []
	animationHashesToFileIndex = {}
	#Animation bundle
	animationBundleAssetList = []
	#Material
	materialFlag = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00'
	
	#file streams
	global bs0,bs52,bs53,bs54,bs63,bs65
	if rapi.checkFileExists(getFileNum(0)):
		bs0 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(0)))
	else:
		print("file 0 not found")
	if rapi.checkFileExists(getFileNum(52)):
		bs52 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(52)))
	else:
		print("file 52 not found")
	if rapi.checkFileExists(getFileNum(53)):
		bs53 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(53)))
	else:
		print("file 53 not found")
	if rapi.checkFileExists(getFileNum(63)):
		bs63 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(63)))
	else:
		print("file 63 not found")
	bs0.setEndian(NOE_LITTLEENDIAN)
	bs52.setEndian(NOE_LITTLEENDIAN)
	bs53.setEndian(NOE_LITTLEENDIAN)
	bs63.setEndian(NOE_LITTLEENDIAN)	
	
	#Read chunk entries from file 0
	while(True):
		flag = bs0.readUShort()
		if flag==0x1301:
			bs0.seek(-2,1)
			chunkType1 = ChunkType1()
			chunkType1.parse(bs0)
			chunkType1List.append(chunkType1)
		else:
			bs0.seek(-2,1)
			break
	while(bs0.tell()+12 <= bs0.getSize()):
		chunkType2 = ChunkType2()
		chunkType2.parse(bs0)
		chunkType2List.append(chunkType2)		
	del bs0
	
	#Parsing chunkType1
	for chunk in chunkType1List:
		if chunk.dataType == 0xB000:
			bs52.seek(chunk.headerOffset+4)
			modelAsset = LM3ModelAsset()
			modelAsset.hashName = hex(bs52.readUInt())
			modelHashesToFileIndex[modelAsset.hashName] = len(modelAssetList)
			modelAssetList.append(modelAsset)
		elif chunk.dataType == 0x7000:
			bs52.seek(chunk.headerOffset+4)
			animationAsset = LM3AnimationAsset()
			animationAsset.hashName = hex(bs52.readUInt())
			animationAsset.dataOffset = chunk.chunkOffset
			animationAsset.dataSize = chunk.chunkSize
			animationHashesToFileIndex[animationAsset.hashName] = len(animationAssetList)
			animationAssetList.append(animationAsset)
		elif chunk.dataType == 0x7100:
			bs52.seek(chunk.headerOffset+4)
			skeletonAsset = LM3SkeletonAsset()
			skeletonAsset.pairedModelHashName = hex(bs52.readUInt())
			skeletonAssetList.append(skeletonAsset)
		elif chunk.dataType == 0x1302:
			bs53.seek(chunk.chunkOffset)
			animationBundleAsset = LM3AnimationBundleAsset()
			count = bs53.readUInt()
			bs53.readUInt()
			for j in range(count):
				bs53.readUInt()
				hash = hex(bs53.readUInt())
				if hash in animationHashesToFileIndex:
					animationBundleAsset.animationIndices.append(animationHashesToFileIndex[hash])
				else:
					continue #anim file in global
			animationBundleAsset.animationIndices = list(sorted(set(animationBundleAsset.animationIndices)))
			animationBundleAssetList.append(animationBundleAsset)				
			
	#Processing chunkType2
	for chunk in chunkType2List:
		#Texture
		#Texture Info
		if chunk.dataType == 0xB501:
			textureIndex += 1
			textureAsset = LM3TextureAsset()
			bs63.seek(chunk.chunkOffset)
			textureAsset.hashName = hex(bs63.readUInt())
			textureAsset.headerOffset = chunk.chunkOffset
			textureAsset.headerSize = chunk.chunkSize
			textureAssetList.append(textureAsset)
			#necessary because for some reason some textures may have broken duplicates (see maid and Hellen in Shiny)
			if textureAsset.hashName not in textureHashesToFileIndex:
				textureHashesToFileIndex[textureAsset.hashName] = textureIndex
		# Texture Data
		elif chunk.dataType == 0xB502:
			textureAssetList[textureIndex].dataOffset = chunk.chunkOffset
			textureAssetList[textureIndex].dataSize = chunk.chunkSize			
			
		#Model
		#Model matrix, used by some models to align to the skeleton
		elif chunk.dataType == 0xB001:
			modelAssetList[modelIndex].b001Size = chunk.chunkSize
			modelAssetList[modelIndex].b001Offset = chunk.chunkOffset
		#Submesh info
		elif chunk.dataType == 0xB003:
			modelAssetList[modelIndex].b003Size = chunk.chunkSize
			modelAssetList[modelIndex].b003Offset = chunk.chunkOffset
		#Vertex data
		elif chunk.dataType == 0xB004:
			modelAssetList[modelIndex].b004Size = chunk.chunkSize
			modelAssetList[modelIndex].b004Offset = chunk.chunkOffset
		#Index buffers
		elif chunk.dataType == 0xB005:
			modelAssetList[modelIndex].b005Size = chunk.chunkSize
			modelAssetList[modelIndex].b005Offset = chunk.chunkOffset
		#Material data 
		elif chunk.dataType == 0xB006:
			modelIndex+=1
			modelAssetList[modelIndex].b006Size = chunk.chunkSize
			modelAssetList[modelIndex].b006Offset = chunk.chunkOffset
		#Material additionnal data
		elif chunk.dataType == 0xB007:
			modelAssetList[modelIndex].b007Size = chunk.chunkSize
			modelAssetList[modelIndex].b007Offset = chunk.chunkOffset
		#Incomplete boneset coords
		elif chunk.dataType == 0xB102:
			modelAssetList[modelIndex].b102Size = chunk.chunkSize
			modelAssetList[modelIndex].b102Offset = chunk.chunkOffset
		#Incomplete boneset hashes
		elif chunk.dataType == 0xB103:
			modelAssetList[modelIndex].b103Size = chunk.chunkSize
			modelAssetList[modelIndex].b103Offset = chunk.chunkOffset
			
		#Skeleton
		#Skeleton header
		elif chunk.dataType == 0x7101:
			skeletonIndex += 1
		#Complete boneset coords
		elif chunk.dataType == 0x7103:
			skeletonAssetList[skeletonIndex].s7103Size = chunk.chunkSize
			skeletonAssetList[skeletonIndex].s7103Offset = chunk.chunkOffset
		#Hashes to complete boneset ID
		elif chunk.dataType == 0x7105:
			skeletonAssetList[skeletonIndex].s7105Size = chunk.chunkSize
			skeletonAssetList[skeletonIndex].s7105Offset = chunk.chunkOffset
		#Parenting info
		elif chunk.dataType == 0x7106:
			skeletonAssetList[skeletonIndex].s7106Size = chunk.chunkSize
			skeletonAssetList[skeletonIndex].s7106Offset = chunk.chunkOffset		
			
	for i,textAsset in enumerate(textureAssetList):
		pickle.dump( textAsset, open( textPath + os.sep + "texture_" + str(i) +".lm3t", "wb" ))
	pickle.dump( textureHashesToFileIndex, open( textPath + os.sep + "textureMap.lm3tMap", "wb" ))
	
	for i,modelAsset in enumerate(modelAssetList):
		#B005
		modelAsset.buffersOffset = modelAsset.b005Offset
		#B003 and B004
		meshCount = modelAsset.b003Size//0x40
		checkPoint = modelAsset.b004Offset
		b004Size = modelAsset.b004Offset + modelAsset.b004Size
		for j in range(meshCount):
			bs52.seek(modelAsset.b003Offset+j*0x40)
			meshAsset = LM3MeshAsset()
			#parse section
			bs52.readUInt() #hashName
			meshAsset.indexBufferOffset = bs52.readUInt()
			indexFlags = bs52.readUInt()
			meshAsset.indexCount = (indexFlags & 0xFFFFFF)
			type = (indexFlags >> 24)
			if (type == 0x80):
				meshAsset.indexFormat = 1
			else:
				meshAsset.indexFormat = 0
			meshAsset.vertexCount = bs52.readUInt()
			bs52.readUInt()
			bs52.readUShort()
			bs52.readUShort()
			bs52.readUInt64()
			bs52.readUInt()
			meshAsset.isSkinned = True if bs52.readUInt() != 0xFFFFFFFF else False
	
			bs52.seek(checkPoint)
			if(meshAsset.isSkinned and bs52.tell()+4<=b004Size):
				meshAsset.skinningBufferOffset = bs52.readUInt()
			if(bs52.tell()+4<=b004Size):
				meshAsset.vertexBufferOffset = bs52.readUInt()
			if(bs52.tell()+4<=b004Size):
				bs52.readUInt()
			if(bs52.tell()+4<=b004Size):
				bs52.readUInt()
			checkPoint = bs52.tell()			
			modelAsset.meshAssetList.append(meshAsset)
		
		#B006
		#load global textureMap if relevant
		if globalPath is not None:
			globalTextureHashesToFileIndex = pickle.load(open( globalPath + os.sep + "Textures" + os.sep + "textureMap.lm3tMap", "rb" ))
			
		#process section
		bs52.seek(modelAsset.b006Offset)
		while(bs52.tell() < modelAsset.b006Offset+modelAsset.b006Size):
			temp = hex(bs52.readUInt())
			if temp in textureHashesToFileIndex:
				modelAsset.pairedTextureFileIndices.append(textureHashesToFileIndex[temp])
			elif globalPath is not None:
				if temp in globalTextureHashesToFileIndex:
					modelAsset.pairedGlobalTextureFileIndices.append(globalTextureHashesToFileIndex[temp])
		modelAsset.pairedTextureFileIndices = list(sorted(set(modelAsset.pairedTextureFileIndices)))
		modelAsset.pairedGlobalTextureFileIndices = list(sorted(set(modelAsset.pairedGlobalTextureFileIndices)))
		#B007
		bs52.seek(modelAsset.b007Offset)
		while(len(modelAsset.materialOffsets)<len(modelAsset.meshAssetList)):
			checkPoint = bs52.tell()
			temp = bs52.readBytes(0x1C)
			if temp == materialFlag:
				bs52.seek(checkPoint-4)
				modelAsset.materialOffsets.append(bs52.readUInt())
			bs52.seek(checkPoint+4)
		modelAsset.materialOffsets.append(modelAsset.b006Size+4)
		
	#Skeleton scan + match	
	for i,skeletonAsset in enumerate(skeletonAssetList):
		if skeletonAsset.pairedModelHashName in modelHashesToFileIndex:
			modelAssetList[modelHashesToFileIndex[skeletonAsset.pairedModelHashName]].s7103Size = skeletonAsset.s7103Size
			modelAssetList[modelHashesToFileIndex[skeletonAsset.pairedModelHashName]].s7103Offset = skeletonAsset.s7103Offset
			modelAssetList[modelHashesToFileIndex[skeletonAsset.pairedModelHashName]].s7105Size = skeletonAsset.s7105Size
			modelAssetList[modelHashesToFileIndex[skeletonAsset.pairedModelHashName]].s7105Offset = skeletonAsset.s7105Offset
			modelAssetList[modelHashesToFileIndex[skeletonAsset.pairedModelHashName]].s7106Size = skeletonAsset.s7106Size
			modelAssetList[modelHashesToFileIndex[skeletonAsset.pairedModelHashName]].s7106Offset = skeletonAsset.s7106Offset
			if i < len(animationBundleAssetList):
				modelAssetList[modelHashesToFileIndex[skeletonAsset.pairedModelHashName]].animationIndices = animationBundleAssetList[i].animationIndices
			
	for i,modelAsset in enumerate(modelAssetList):
		if modelAsset.s7105Offset > 0:
			#B103
			bs52.seek(modelAsset.b103Offset)
			for j in range(modelAsset.b103Size//0x4):
				hash = hex(bs52.readUInt())
				modelAsset.boneIDB1ToHash[j] = hash
				modelAsset.hashToBoneIDB1[hash] = j
			#7105
			bs53.seek(modelAsset.s7105Offset)
			for j in range(modelAsset.s7105Size//0x8):
				hash = hex(bs53.readUInt())
				id = bs53.readUInt()
				modelAsset.boneID71ToHash[id] = hash
				modelAsset.hashToBoneID71[hash] = id
		
	for i,modelAsset in enumerate(modelAssetList):
		pickle.dump( modelAsset, open( modelPath + os.sep + "model_" + str(i) +".lm3m", "wb" ))	
	pickle.dump( modelHashesToFileIndex, open( modelPath + os.sep + "modelMap.lm3mMap", "wb" ))
	
	for i,animationAsset in enumerate(animationAssetList):
		pickle.dump( animationAsset, open( animPath + os.sep + "anim_" + str(i) +".lm3a", "wb" ))
	
	for i,animationBundleAsset in enumerate(animationBundleAssetList):
		pickle.dump( animationBundleAsset, open( animBundlePath + os.sep + "animPack_" + str(i) +".lm3ap", "wb" ))
	print("Files and assets extracted")
	
def ExtractDict(data, mdlList):
	
	ctx = rapi.rpgCreateContext()
	bs = NoeBitStream(data)
	InitializeFromDict()
	
	#Dict parsing, simplified since we don't need everything
	bs.readBytes(0xc)
	fileCount = bs.readUByte()
	chunkCount = bs.readUByte()
	bs.seek(0x2 + chunkCount*0x18,1)
	
	offsets = {}
	sizes = {}
	
	#verify if global dir is a valid one before proceeding
	if globalPath is not None:
		if os.path.isdir(globalPath) is not True:
			print("invalid directory")
			return 0		
	
	for i in range(fileCount):
		offset = bs.readUInt()		
		size = bs.readUInt()
		zSize = bs.readUInt()
		bs.readBytes(0x2)
		source = bs.readUByte()
		bs.readUByte()
		#Only keep the .data related files, we don't have .debug and .nxpc 
		if source == 0:
			offsets[i] = offset
			sizes[i] = size			
	indices = list(offsets.keys())
	
	#Decompress the zlib compressed files and put them in the File_Data folder
	for i, key in enumerate(indices):
		if sizes[key] > 0:
			if i +1 < len(indices):
				fileData = rapi.loadIntoByteArray(dataFileName)[offsets[indices[i]]:offsets[indices[i+1]]]
			else:
				continue
			decompressedData = rapi.decompInflate(fileData,sizes[key])			
			destinationFileName = filePath + os.sep + rapi.getLocalFileName(dataFileName)[:-5] + '_' + str(key) + '.lm3'
			with open(destinationFileName,"wb") as destFile:
				destFile.write(decompressedData)
	
	#Extraction completed, next we'll parse the chunk table and prepare the assets	
	ExtractAssets()	
	try:
		mdl = rapi.rpgConstructModel()
	except:
		mdl = NoeModel()
	mdlList.append(mdl)
	
	return 1

# =================================================================
# Data processing
# =================================================================

def processTexture(textureAssets):	
	for i,textureAsset in enumerate(textureAssets):
		bs63.seek(textureAsset.headerOffset+4) #skip the hash, not needed
		width = bs63.readUShort()
		height = bs63.readUShort()
		bs63.readBytes(4)
		format = bs63.readUByte()
		bs63.readBytes(3)
		maxBlockHeight = 16
		# print(i)
		# print(hex(format))
		if format == 0x0 or format == 0x1:
			format = "r8g8b8a8"
		elif format == 0x11:
			format = noesis.NOESISTEX_DXT1
		elif format == 0x15:
			format = noesis.FOURCC_ATI2
		elif format == 0x16:
			format = noesis.FOURCC_BC5
		elif format == 0x19:
			format = "ASTC_4_4"			
		elif format == 0x1A:
			format = "ASTC_5_4"
		elif format == 0x1B:
			format = "ASTC_5_5"
		elif format == 0x1C:
			format = "ASTC_6_5"
		elif format == 0x1D:
			format = "ASTC_6_6"
		elif format == 0x1E:
			format = "ASTC_8_5"			
		elif format == 0x1F:
			format = "ASTC_8_6"
		elif format == 0x20:
			format = "ASTC_8_8"
		else:
			print("UNKNOWN TEXTURE FORMAT !" + str(hex(format)))
			format = noesis.NOESISTEX_UNKNOWN
		textureName = str(i) + '.dds'
		bs65.seek(textureAsset.dataOffset)
		textureData = bs65.readBytes(textureAsset.dataSize)
		bRaw = type(format) == str
		if bRaw and format.startswith("ASTC"):
			blockWidth,	blockHeight = list(map(lambda x: int(x), format.split('_')[1:]))
			widthInBlocks = (width + (blockWidth - 1)) // blockWidth
			heightInBlocks = (height + (blockHeight - 1)) // blockHeight			
			blockSize = 16
			maxBlockHeight = 8 if width <= 256 or height <= 256 else 16
			maxBlockHeight = 4 if width <= 128 or height <= 128 else maxBlockHeight
			maxBlockHeight = 2 if width <= 64 or height <= 64 else maxBlockHeight
			if format == "ASTC_6_6":
				maxBlockHeight = 4 if width <= 64 or height <= 64 else maxBlockHeight
				maxBlockHeight = 2 if width <= 32 or height <= 32 else maxBlockHeight
				maxBlockHeight = 1 if width <= 32 and height <= 32 else maxBlockHeight
			#check kboo text9 
			textureData = rapi.callExtensionMethod("untile_blocklineargob", textureData, widthInBlocks, heightInBlocks, blockSize, maxBlockHeight)		
			textureData = rapi.callExtensionMethod("astc_decoderaw32", textureData, blockWidth, blockHeight, 1, width, height, 1)
			format = noesis.NOESISTEX_RGBA32
		elif bRaw:
			blockWidth = blockHeight = 1
			widthInBlocks = (width + (blockWidth - 1)) // blockWidth
			heightInBlocks = (height + (blockHeight - 1)) // blockHeight
			maxBlockHeight = 8 if width <= 256 or height <= 256 else 16
			maxBlockHeight = 4 if width <= 128 or height <= 128 else maxBlockHeight
			maxBlockHeight = 2 if width <= 32 or height <= 32 else maxBlockHeight
			textureData = rapi.callExtensionMethod("untile_blocklineargob", textureData, widthInBlocks, heightInBlocks, 16, maxBlockHeight)
			textureData = rapi.imageDecodeRaw(textureData, width, height, format,2)
			format = noesis.NOESISTEX_RGBA32
		else:
			blockWidth = blockHeight = 4
			blockSize = 8 if format == noesis.NOESISTEX_DXT1 else 16
			widthInBlocks = (width + (blockWidth - 1)) // blockWidth
			heightInBlocks = (height + (blockHeight - 1)) // blockHeight
			maxBlockHeight = 8 if width <= 256 or height <= 256 else 16
			maxBlockHeight = 4 if width <= 128 or height <= 128 else maxBlockHeight
			maxBlockHeight = 2 if width <= 32 or height <= 32 else maxBlockHeight
			textureData = rapi.callExtensionMethod("untile_blocklineargob", textureData, widthInBlocks, heightInBlocks, blockSize, maxBlockHeight)
			textureData = rapi.imageDecodeDXT(textureData, width, height, format,0.0,2)
			format = noesis.NOESISTEX_RGBA32
		tex = NoeTexture(textureAsset.hashName, width, height, textureData, format)
		textureHashToIndex[textureAsset.hashName]=len(textureList)
		textureList.append(tex)
		
		
def processModel(modelAssets):
	for a,modelAsset in enumerate(modelAssets):
		
		if bLoadMaterials:
			#Local textures
			InitializeFileStream(63)
			InitializeFileStream(65)
			tempTextureList = []
			for tex in modelAsset.pairedTextureFileIndices:
				tempTextureList.append(pickle.load(open( textPath+os.sep+"texture_" + str(tex)+".lm3t", "rb" )))
			processTexture(tempTextureList)
			global bs63,bs65
			del bs63,bs65

			#Global textures, if relevant
			if globalPath is not None:
				tempTextureList = []
				global bs63,bs65
				bs63 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(63,True)))
				bs65 = NoeBitStream(rapi.loadIntoByteArray(getFileNum(65,True)))
				bs63.setEndian(NOE_LITTLEENDIAN)
				bs65.setEndian(NOE_LITTLEENDIAN)
				for tex in modelAsset.pairedGlobalTextureFileIndices:
					tempTextureList.append(pickle.load(open( globalPath + os.sep + "Textures"+os.sep+"texture_" + str(tex)+".lm3t", "rb" )))
				processTexture(tempTextureList)
				del bs63,bs65
			
			#Materials (kinda...)
			InitializeFileStream(52)
			materialList = []
			for index in range(len(modelAsset.materialOffsets)):
				modelAsset.materialOffsets[index]+=modelAsset.b006Offset-8
			for i,offset in enumerate(modelAsset.materialOffsets[:-1]):
				material = NoeMaterial('submesh_' + str(i), "")
				# "Good" material
				if offset + 448 in modelAsset.materialOffsets:
					bs52.seek(offset)
					bs52.readBytes(0x14)
					hash = hex(bs52.readUInt())
					#added for Hellen in Shiny.data, fixed some building stuff
					if hash == hex(0x81800000):
						bs52.seek(-8,1)
						hash = hex(bs52.readUInt())					
						if hash in textureHashToIndex:
							material.setTexture(textureList[textureHashToIndex[hash]].name)
						bs52.readBytes(4)
						hash = hex(bs52.readUInt())
						if hash in textureHashToIndex:
							material.setNormalTexture(textureList[textureHashToIndex[hash]].name)
							material.setNormalTexture(textureList[2].name)
						materialList.append(material)
					else:
						if hash in textureHashToIndex:
							material.setNormalTexture(textureList[textureHashToIndex[hash]].name)
						bs52.readBytes(8)
						bs52.readBytes(0xC)
						hash = hex(bs52.readUInt())
						if hash in textureHashToIndex:
							material.setTexture(textureList[textureHashToIndex[hash]].name)
						# bs52.readBytes(0x38)
						# hash = bs52.readUInt()
						# print(bs52.tell())
						# if hash in model.textureHashesToIndex:
							# print("spec found !")
							# material.setSpecularTexture(textureList[model.textureHashesToIndex[hash]].name)
						materialList.append(material)
				#just for egadd glasses...
				elif offset == 330752 and offset+196 == modelAsset.materialOffsets[-1]:
					bs52.seek(offset)
					bs52.readBytes(0x10)
					hash = hex(bs52.readUInt())
					if hash in textureHashToIndex:
						material.setTexture(textureList[textureHashToIndex[hash]].name)
					bs52.readBytes(8)
					bs52.readBytes(0xC)
					hash = hex(bs52.readUInt())
					if hash in textureHashToIndex:
						material.setNormalTexture(textureList[textureHashToIndex[hash]].name)
					# bs52.readBytes(0x38)
					# hash = bs52.readUInt()
					# print(bs52.tell())
					# if hash in model.textureHashesToIndex:
						# print("spec found !")
						# material.setSpecularTexture(textureList[model.textureHashesToIndex[hash]].name)
					materialList.append(material)		
				elif offset + 192 in modelAsset.materialOffsets:
					bs52.seek(offset)
					bs52.readBytes(0x10)
					hash = hex(bs52.readUInt())
					a = bs52.readUInt()
					if a != 0x81800000:
						if hash in textureHashToIndex:
							material.setNormalTexture(textureList[textureHashToIndex[hash]].name)
						bs52.readBytes(0x4)
						bs52.readBytes(0xC)
						hash = hex(bs52.readUInt())
						if hash in textureHashToIndex:
							material.setTexture(textureList[textureHashToIndex[hash]].name)
						materialList.append(material)
					else:
						if hash in textureHashToIndex:
							material.setTexture(textureList[textureHashToIndex[hash]].name)
						bs52.readBytes(4)
						hash = hex(bs52.readUInt())
						if hash in textureHashToIndex:
							material.setNormalTexture(textureList[textureHashToIndex[hash]].name)
							material.setNormalTexture(textureList[2].name)
						materialList.append(material)
				else:
					bs52.seek(offset)
					a = 0
					while a != 0x81800000 and a!= 0x01800000 and bs52.tell() < modelAsset.materialOffsets[-1]:
						a= bs52.readUInt()
					if a == 0x81800000:
						bs52.seek(-8,1)
						hash = hex(bs52.readUInt())
						# print(hash)
						if hash in textureHashToIndex:
							material.setTexture(textureList[textureHashToIndex[hash]].name)
						bs52.readBytes(8)
						hash = hex(bs52.readUInt())
						if hash in textureHashToIndex:
							material.setNormalTexture(textureList[textureHashToIndex[hash]].name)
						# bs52.readBytes(8)
						# hash = bs52.readUInt()
						# if hash in model.textureHashesToIndex:
							# print("spec found !")
							# material.setSpecularTexture(textureList[model.textureHashesToIndex[hash]].name)
						materialList.append(material)
					elif a == 0x01800000: #added because of Hellen concert Hall sm 0
						bs52.seek(-8,1)
						bs52.readBytes(0x18)
						hash = hex(bs52.readUInt())
						# print(hash)
						if hash in textureHashToIndex:
							material.setTexture(textureList[textureHashToIndex[hash]].name)
						bs52.readBytes(8)
						hash = hex(bs52.readUInt())
						if hash in textureHashToIndex:
							material.setNormalTexture(textureList[textureHashToIndex[hash]].name)
						# bs52.readBytes(8)
						# hash = bs52.readUInt()
						# if hash in model.textureHashesToIndex:
							# print("spec found !")
							# material.setSpecularTexture(textureList[model.textureHashesToIndex[hash]].name)
						materialList.append(material)
		else:
			InitializeFileStream(52)
			materialList = []
		#Skeleton
		#Parenting info
		InitializeFileStream(53)
		global bs53
		if modelAsset.s7106Offset > 0:
			bs53.seek(modelAsset.s7106Offset)
			for i in range(modelAsset.s7106Size//0x2):
				modelAsset.parentList.append(bs53.readUShort())
		#Transform info
		if modelAsset.s7103Offset > 0:
			bs53.seek(modelAsset.s7103Offset)
			for i in range(modelAsset.s7103Size//0x1C):
				quaternion = [bs53.readFloat() for j in range(4)]
				position = [bs53.readFloat() for j in range(3)]
				boneMatrixTransform = NoeQuat(quaternion).toMat43().inverse()
				boneMatrixTransform[3] = NoeVec3(position)
				# bone = NoeBone(i, 'bone_' + str(i), boneMatrixTransform, None, modelAsset.parentList[i])
				bone = NoeBone(i, 'bone_' + str(i), boneMatrixTransform, None, modelAsset.parentList[i])
				modelAsset.jointList.append(bone)
		for bone in modelAsset.jointList:
			parentId = bone.parentIndex
			if parentId != 65535:
				bone.setMatrix(bone.getMatrix() * modelAsset.jointList[parentId].getMatrix())
			else:
				bone.setMatrix(bone.getMatrix()*NoeAngles([90,0,-90]).toMat43())
				
		#Animation
		if bLoadAnimations:
			animBPath = rapi.loadPairedFileGetPath("animPack file", ".lm3ap")
			if animBPath is not None:
				animationBundleAsset = pickle.load(open( animBPath[1], "rb" ))
				# animList = modelAsset.animationIndices if bLoadAnimations else []
				animList = animationBundleAsset.animationIndices
				for n,animationindex in enumerate(animList):
					animationAsset = pickle.load(open( animPath+os.sep+"anim_" + str(animationindex)+".lm3a", "rb" ))
					keyframedJointList = []
					# print(animationAsset.dataOffset)
					# print(animationAsset.dataSize)
					bs53.seek(animationAsset.dataOffset)
					bs53.readUInt() # 0, always ?
					boneHeaderCount = bs53.readUShort()
					frameCount = bs53.readUShort()
					duration = bs53.readFloat()
					bs53.readUInt() # 0, always ?
					bs53.seek(0x18,1) # Not sure what the two first chunks mean
					rotNoeKeyFramedValues = {}
					posNoeKeyFramedValues = {}
					scaleNoeKeyFramedValues = {}
					unknownRotOpcode = {}
					unknownPosOpcode = {}
					unknownScaleOpcode = {}
					for i in range(boneHeaderCount-2): #Sometimes additionnal chunks starting with 0x00000505, don't really care since we have offsets
						boneHeader = LM3BoneHeader()
						boneHeader.hash = hex(bs53.readUInt())
						boneHeader.index = bs53.readUByte()
						boneHeader.magic = bs53.readUByte()
						boneHeader.type = bs53.readUByte()
						boneHeader.opcode = bs53.readUByte()
						boneHeader.offset = bs53.readUInt()
						checkpoint = bs53.tell()
						if boneHeader.hash in modelAsset.hashToBoneID71:
							# if boneHeader.magic != 0xC0 and boneHeader.magic != 0xC1 and boneHeader.magic != 0xC2:
								# print("New magic found")
								# print(boneHeader.magic)
							#rotation
							if boneHeader.type == 1:
								rotNoeKeyFramedValues[boneHeader.hash] = []
								if boneHeader.opcode == 0x0F: #confirmed
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									for j in range(frameCount):
										quaternion = NoeQuat([bs53.readFloat() for a in range(4)]).transpose()
										rotationKeyframedValue = NoeKeyFramedValue(duration/frameCount*j,quaternion)
										rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								elif boneHeader.opcode == 0x13: #not sure but makes sense
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									count = bs53.readUInt()
									for j in range(count):
										quaternion = NoeQuat([bs53.readFloat() for a in range(4)]).transpose()
										rotationKeyframedValue = NoeKeyFramedValue(duration/count*j,quaternion)
										rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								elif boneHeader.opcode == 0x15: #confirmed
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									quaternion = NoeQuat([bs53.readFloat() for a in range(4)]).transpose()
									rotationKeyframedValue = NoeKeyFramedValue(0,quaternion)
									rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								# elif boneHeader.opcode == 0x16: #not sure at all
									# flag to say nothing do be done ?
									# bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									# quaternion = NoeQuat([bs53.readShort()/0x7FFF for a in range(4)]).transpose()
									# rotationKeyframedValue = NoeKeyFramedValue(0,quaternion)
									# rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								elif boneHeader.opcode == 0x17: #not sure at all
									# Some weird thing is going on. Normalization or something needed ?							
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									quaternion = NoeAngles([bs53.readShort()/180,0,0]).toQuat()
									rotationKeyframedValue = NoeKeyFramedValue(0,quaternion)
									rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								elif boneHeader.opcode == 0x18: #somewhat confirmed (priestess cloth)
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									for j in range(frameCount):
										quaternion = NoeAngles([0,0,bs53.readShort()/180]).toQuat()
										rotationKeyframedValue = NoeKeyFramedValue(duration/frameCount*j,quaternion)
										rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								elif boneHeader.opcode == 0x19: #somewhat confirmed (priestess arms)
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									for j in range(frameCount):
										quaternion = NoeAngles([0,bs53.readShort()/180,0]).toQuat()
										rotationKeyframedValue = NoeKeyFramedValue(duration/frameCount*j,quaternion)
										rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								# elif boneHeader.opcode == 0x1A: #need confirm, king boo
									# bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									# bs53.readShort()
									# quaternion = NoeAngles([bs53.readShort()/180,0,0]).toQuat()
									# rotationKeyframedValue = NoeKeyFramedValue(0,quaternion)
									# rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								# elif boneHeader.opcode == 0x1B: #seen on maid
									# bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									# bs53.readShort()
									# quaternion = NoeAngles([bs53.readShort()/180,0,0]).toQuat()
									# rotationKeyframedValue = NoeKeyFramedValue(0,quaternion)
									# rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								# elif boneHeader.opcode == 0x1C: #need confirm (pianist tail)
									# bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									# bs53.readShort()
									# quaternion = NoeAngles([0,bs53.readShort()/180,0]).toQuat()
									# rotationKeyframedValue = NoeKeyFramedValue(0,quaternion)
									# rotNoeKeyFramedValues[boneHeader.hash].append(rotationKeyframedValue)
								else:
									if hex(boneHeader.opcode) in unknownRotOpcode:
										unknownRotOpcode[hex(boneHeader.opcode)] += 1
									else:
										unknownRotOpcode[hex(boneHeader.opcode)] = 1
							#location
							elif boneHeader.type == 3:
								posNoeKeyFramedValues[boneHeader.hash] = []
								if boneHeader.opcode == 0x6: #confirmed, somewhat (priestess movement)
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									for j in range(frameCount):
										position = NoeVec3([bs53.readFloat() for a in range(3)])
										positionKeyFramedValue = NoeKeyFramedValue(duration/frameCount*j, position)
										posNoeKeyFramedValues[boneHeader.hash].append(positionKeyFramedValue)
								elif boneHeader.opcode == 0x8: #guess
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									for j in range(frameCount):
										position = NoeVec3([bs53.readHalfFloat() for a in range(3)])
										positionKeyFramedValue = NoeKeyFramedValue(duration/frameCount*j, position)
										posNoeKeyFramedValues[boneHeader.hash].append(positionKeyFramedValue)
								elif boneHeader.opcode == 0x9: #to be confirmed but makes sense
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									count = bs53.readUInt()
									for j in range(count):
										position = NoeVec3([bs53.readFloat() for a in range(3)])
										positionKeyFramedValue = NoeKeyFramedValue(duration/count*j, position)
										posNoeKeyFramedValues[boneHeader.hash].append(positionKeyFramedValue)
								elif boneHeader.opcode == 0xA: #to be confirmed but makes sense
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									count = bs53.readUShort()
									for j in range(count):
										position = NoeVec3([bs53.readHalfFloat() for a in range(3)])
										positionKeyFramedValue = NoeKeyFramedValue(duration/count*j, position)
										posNoeKeyFramedValues[boneHeader.hash].append(positionKeyFramedValue)
								elif boneHeader.opcode == 0xB: #to be confirmed but makes sense
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									position = NoeVec3([bs53.readFloat() for a in range(3)])
									positionKeyFramedValue = NoeKeyFramedValue(0, position)
									posNoeKeyFramedValues[boneHeader.hash].append(positionKeyFramedValue)
								elif boneHeader.opcode == 0xC: #confirmed (maid stuff)
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									position = NoeVec3([bs53.readHalfFloat() for a in range(3)])
									positionKeyFramedValue = NoeKeyFramedValue(0, position)
									posNoeKeyFramedValues[boneHeader.hash].append(positionKeyFramedValue)
								elif boneHeader.opcode == 0xD: #confirmed (pianist movement)
									bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									axis = bs53.readUInt()
									bs53.readBytes(0x8)
									count = bs53.readUInt()
									for j in range(count):
										data = bs53.readFloat()
										if axis == 0:
											position = NoeVec3([data,0,0])
										elif axis == 1:
											position = NoeVec3([0,data,0])
										elif axis == 2:
											position = NoeVec3([0,0,data])
										positionKeyFramedValue = NoeKeyFramedValue(duration/count*j, position)
										posNoeKeyFramedValues[boneHeader.hash].append(positionKeyFramedValue)
								elif boneHeader.opcode == 0xE: #confirmed somewhat (Hellen outfit)
									bs53.seek(animationAsset.dataOffset+ boneHeader.offset)
									a = bs53.readUInt()
									bs53.readUShort()
									count = bs53.readUShort()
									for j in range(count):
										position = NoeVec3([bs53.readHalfFloat(),0,0])
										positionKeyFramedValue = NoeKeyFramedValue(duration/count*j, position)
										posNoeKeyFramedValues[boneHeader.hash].append(positionKeyFramedValue)
								else:
									if hex(boneHeader.opcode) in unknownPosOpcode:
										unknownPosOpcode[hex(boneHeader.opcode)] += 1
									else:
										unknownPosOpcode[hex(boneHeader.opcode)] = 1
							#Not confirmed at all, no clue yet. Probably something other than scale
							# elif boneHeader.type == 2:
								# scaleNoeKeyFramedValues[boneHeader.hash] = []
								# posNoeKeyFramedValues[boneHeader.hash] = []
								# if boneHeader.opcode == 0x2A: #always of length 12 so either 6 HF or 3 F, don't have any clear example
									# bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									# scale = NoeVec3([bs53.readHalfFloat() for a in range(3)])
									# scaleKeyFramedValue = NoeKeyFramedValue(0, scale)
									# scaleNoeKeyFramedValues[boneHeader.hash].append(scaleKeyFramedValue)
									# bs53.seek(animationAsset.dataOffset + boneHeader.offset)
									# position = NoeVec3([bs53.readFloat() for a in range(3)])
									# positionKeyFramedValue = NoeKeyFramedValue(0, position)
									# posNoeKeyFramedValues[boneHeader.hash].append(positionKeyFramedValue)
								# else:
									# if hex(boneHeader.opcode) in unknownScaleOpcode:
										# unknownScaleOpcode[hex(boneHeader.opcode)] += 1
									# else:
										# unknownScaleOpcode[hex(boneHeader.opcode)] = 1
						bs53.seek(checkpoint)
					# print("anim " + str(animationindex))
					# print(unknownRotOpcode)
					# print(unknownPosOpcode)
					for hash in modelAsset.hashToBoneID71:
						if hash in posNoeKeyFramedValues or hash in rotNoeKeyFramedValues or hash in scaleNoeKeyFramedValues:
							actionBone = NoeKeyFramedBone(modelAsset.hashToBoneID71[hash])
							#root bone rotation ignored as it seem to screw up some stuff
							if hash in rotNoeKeyFramedValues and hash != "0x2e51a3":
								actionBone.setRotation(rotNoeKeyFramedValues[hash], noesis.NOEKF_ROTATION_QUATERNION_4)
							if hash in posNoeKeyFramedValues:
								actionBone.setTranslation(posNoeKeyFramedValues[hash], noesis.NOEKF_TRANSLATION_VECTOR_3)
							if hash in scaleNoeKeyFramedValues:
								actionBone.setScale(scaleNoeKeyFramedValues[hash], noesis.NOEKF_SCALE_VECTOR_3)
							keyframedJointList.append(actionBone)
					anim = NoeKeyFramedAnim("anim_"+str(animationindex), modelAsset.jointList, keyframedJointList, 30)
					animationList.append(anim)
		del bs53
		
		
		#Geometry
		InitializeFileStream(54)
		bs52.seek(modelAsset.b001Offset)
		modelMatrix = NoeMat44.fromBytes(bs52.readBytes(0x40))
		for i,mesh in enumerate(modelAsset.meshAssetList):
			#vertices
			bs54.seek(modelAsset.buffersOffset + mesh.vertexBufferOffset)
			finalVertexBuffer = bs54.readBytes(0x30*mesh.vertexCount)
			#since UVs are split between normal coords we need to construct a new buffer
			uv1 = noesis.deinterleaveBytes(finalVertexBuffer,0xC,0x4,0x30)
			uv2 = noesis.deinterleaveBytes(finalVertexBuffer,0x1C,0x4,0x30)
			finalUVBuffer = noesis.interleaveUniformBytes(uv1+uv2,4,mesh.vertexCount)
			#indices
			bs54.seek(modelAsset.buffersOffset + mesh.indexBufferOffset)
			multiplier = 1 if mesh.indexFormat else 2
			finalIndicesBuffer = bs54.readBytes(mesh.indexCount * multiplier)
			#skinning, don't care about non animated stuff for now so we ignore objects with only B1 info
			if mesh.isSkinned and modelAsset.s7103Offset > 0:
				bs54.seek(modelAsset.buffersOffset)
				bs54.seek(mesh.skinningBufferOffset,1)				
				checkpoint = bs54.tell()
				#Indices, need to be taken from B1 to 71
				finalBlendIndicesBuffer = bytes()
				for j in range(mesh.vertexCount):
					bs54.seek(checkpoint+j*0x14)
					temp = [bs54.readUByte() for j in range(4)]
					a = []
					for t in temp:
						h = modelAsset.boneIDB1ToHash[t]
						f = modelAsset.hashToBoneID71[h]
						finalBlendIndicesBuffer+=struct.pack('<B', f)
				bs54.seek(checkpoint)
				finalBlendWeightsBuffer = noesis.deinterleaveBytes(bs54.readBytes(0x14*mesh.vertexCount),0x4,0x10,0x14)
			
			meshName = 'submesh_' + str(i)
			rapi.rpgSetMaterial(meshName)
			rapi.rpgSetName(meshName)		
			rapi.rpgClearBufferBinds()
			rapi.rpgBindPositionBufferOfs(finalVertexBuffer, noesis.RPGEODATA_FLOAT, 0x30,0x0)
			rapi.rpgBindNormalBufferOfs(finalVertexBuffer, noesis.RPGEODATA_FLOAT, 0x30,0x10)
			rapi.rpgBindUV1Buffer(finalUVBuffer, noesis.RPGEODATA_FLOAT, 0x8)
			if mesh.isSkinned and modelAsset.s7103Offset > 0:
				rapi.rpgBindBoneIndexBuffer(finalBlendIndicesBuffer, noesis.RPGEODATA_UBYTE, 0x4, 0x4)
				rapi.rpgBindBoneWeightBuffer(finalBlendWeightsBuffer, noesis.RPGEODATA_FLOAT,0x10, 0x4)
			correctionMatrix = skelRotCorrection.toMat43()
			correctionMatrix[3] = skelPosCorrection
			transfMatrix = modelMatrix.toMat43() * NoeAngles([90,0,0]).toMat43() * correctionMatrix
			rapi.rpgSetTransform(transfMatrix)
			rapi.rpgCommitTriangles(finalIndicesBuffer,noesis.RPGEODATA_UBYTE if mesh.indexFormat else noesis.RPGEODATA_USHORT, mesh.indexCount,noesis.RPGEO_TRIANGLE, 1)		
		try:
			mdl = rapi.rpgConstructModel()
		except:
			mdl = NoeModel()
		mdl.setModelMaterials(NoeModelMaterials(textureList, []))
		if len(modelAsset.jointList) > 0:
			mdl.setBones(modelAsset.jointList)
		if len(animationList) > 0:
			mdl.setAnims(animationList)
		mdl.setModelMaterials(NoeModelMaterials(textureList, materialList))
		modelList.append(mdl)
			
	
	