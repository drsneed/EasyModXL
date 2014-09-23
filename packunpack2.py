#---------------------------------------------------------------------------#
# Copyright (C) 2012 Dustin Sneeden                                         #
# EasyMod XL - Open Source Mod Editor for Cities XL                         #
#                                                                           #
# This program is part of EasyMod XL.                                       #
# EasyMod XL is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#---------------------------------------------------------------------------#


import Crypto.Cipher.ARC4
import os, hashlib, struct, zlib

class PatchFile:
    ''' Cities XL Raw Archive '''
    def __init__(self, patchFile = None, fileDict=None):
        self.locFiles = ['.en','.es','.de','.fr','.it']
        if patchFile != None:
            self.rawData = open(patchFile, 'rb').read()
            tabAddr = self.le(self.rawData[0x20:0x24])
        
            self.fileCount = self.le(self.rawData[0x24:0x28])
            self.fileDict  = self.getFileDict(self.rawData[tabAddr:])
        if fileDict != None:
            self.fileDict = fileDict

    def le(self, Bytes):
        ''' Converts from Little Endian to Integer '''
        return struct.unpack('<L', Bytes)[0]
        
    def getFileDict(self, fileTable):
        md5Hash = hashlib.md5()
        md5Hash.update('allocator')
        
        md5Hash   = md5Hash.digest()
        decryptor = Crypto.Cipher.ARC4.new(md5Hash)
        fileDict  = {              }
        ft        = decryptor.decrypt(fileTable)
        for i in range(self.fileCount):
            compressedSize, ft = self.le(ft[:4])  , ft[4:]
            uncompressSize, ft = self.le(ft[:4])  , ft[4:]
            compressedAddr, ft = self.le(ft[:4])  , ft[4:]
            sha1Hash      , ft = ft[:20]          , ft[20:]
            isArchive     , ft = self.le(ft[:4])  , ft[4:]
            nameLength    , ft = self.le(ft[:4])  , ft[4:]
            name          , ft = ft[:nameLength-1], ft[nameLength:]
            if isArchive == 0:
                fileDict[name] = self.rawData[compressedAddr:compressedSize+compressedAddr]
            else:
                if name[-3:] in self.locFiles:
                    data = zlib.decompress(self.rawData[compressedAddr:compressedSize + compressedAddr])
                    data = data.replace('\x00','')
                    fileDict[name] = data
                else:
                    fileDict[name] = zlib.decompress(self.rawData[compressedAddr:compressedSize+compressedAddr])
        return fileDict
        
    def unpackInto(self, outputDir):
        curDir = os.getcwd()
        os.chdir(outputDir)
        for filepath in self.fileDict:
            path, filename = os.path.split(str(filepath))
            paths = path.split('/')
            for p in paths:
                if os.path.exists(p):
                    os.chdir(p)
                else:
                    os.mkdir(p)
                    os.chdir(p)
            makeFile = open(filename, 'wb')
            makeFile.write(self.fileDict[filepath])
            makeFile.close()
            os.chdir('../'*len(paths))
        os.chdir(curDir)
        
class DataFolder:
    def __init__(self, rootDir):
        self.origDir = os.getcwd()
        self.locFiles = ['en','es','de','fr','it']
        self.dataDir = rootDir[:rootDir.find('/data')]
        self.fileList = self.parseDataFolder(rootDir)
    
    def sha1(self, key):
        sha1Object = hashlib.sha1()
        sha1Object.update('allocator')
        return sha1Object.digest()
        
    def getFiles(self, root):
        for path, subdirs, files in os.walk(root):
            for name in files:
                yield (path, name)
    def parseDataFolder(self, datadir):
        output = [ ]
        for path, _file in list(self.getFiles(datadir)):
            p = path[path.find('data'):].replace('\\','/')
            output.append((p, _file))
        return output
        
    def packInto(self, outputFile):
        fileContents = ''
        fileTable    = ''
        for path, _file in self.fileList:
            os.chdir(self.dataDir + '/' + path)
            
            inflatedFile = open(_file, 'rb').read()
            if _file[-3:] in self.locFiles:
                if inflatedFile[:2] == '\xff\xfe':
                    inflatedFile = str().join(map(lambda u: u + '\x00', inflatedFile))
                else:
                    inflatedFile = '\xff\xfe' + str().join(map(lambda u: u + '\x00', inflatedFile))
            deflatedFile = zlib.compress(inflatedFile)
            fileName     = path + '/' + _file + '\x00'
            fileNameLen  = struct.pack('<L', len(fileName))
            fileAddress  = struct.pack('<L', 0x30 + len(fileContents))
            inflatedSize = struct.pack('<L', len(inflatedFile))
            deflatedSize = struct.pack('<L', len(deflatedFile))
            inflatedHash = self.sha1(inflatedFile)
            if _file.endswith('.patch') or \
               _file.endswith('.pak')   or \
               _file.endswith('.lvl')   or \
               _file.endswith('.ava'):
                isArchive = struct.pack('<L', 0x000000)
                fileContents += inflatedFile
            else:
                isArchive = struct.pack('<L', 0x000100)
                fileContents += deflatedFile
                
            fileTable += deflatedSize + inflatedSize + fileAddress + inflatedHash + \
            isArchive + fileNameLen + fileName
            os.chdir(self.dataDir)
        os.chdir(self.origDir)
        md5Hash = hashlib.md5()
        md5Hash.update('allocator')
        md5Hash   = md5Hash.digest()
        encryptor = Crypto.Cipher.ARC4.new(md5Hash)
        fileTable = encryptor.encrypt(fileTable)
        
        header  = '\x4D\x43\x50\x4B\x03\x00\x00\x00\x7F\x01\x00\x00'
        header += self.sha1(fileContents + fileTable)
        header += struct.pack('<L', 0x30 + len(fileContents))
        header += struct.pack('<L', len(self.fileList))
        header += '\x00' * 8
        
        patchFile = header + fileContents + fileTable
        writePatch = open(outputFile, 'wb')
        writePatch.write(patchFile)
        writePatch.close()

class EMXLProject:
    def __init__(self, currentData):
        self.currentData = currentData
        self.locFiles = ['.en','.es','.de','.fr','.it']
    def sha1(self, key):
        sha1Object = hashlib.sha1()
        sha1Object.update('allocator')
        return sha1Object.digest()
        
    def packInto(self, outputFile):
        fileContents = ''
        fileTable    = ''
        for path, contents in self.currentData.items():
            path = str(path)
            if path[-3:] in self.locFiles:
                if contents[:2] == '\xff\xfe':
                    inflatedFile = str().join(map(lambda u: u + '\x00', contents))
                else:
                    inflatedFile = '\xff\xfe' + str().join(map(lambda u: u + '\x00', contents))
            else:
                inflatedFile = contents
            deflatedFile = zlib.compress(inflatedFile)
            fileName     = path + '\x00'
            fileNameLen  = struct.pack('<L', len(fileName))
            fileAddress  = struct.pack('<L', 0x30 + len(fileContents))
            inflatedSize = struct.pack('<L', len(inflatedFile))
            deflatedSize = struct.pack('<L', len(deflatedFile))
            inflatedHash = self.sha1(inflatedFile)
            if path.endswith('.patch') or \
               path.endswith('.pak')   or \
               path.endswith('.ava'):
                isArchive = struct.pack('<L', 0x000000)
                fileContents += inflatedFile
            else:
                isArchive = struct.pack('<L', 0x000100)
                fileContents += deflatedFile
                
            fileTable   += deflatedSize + inflatedSize + \
            fileAddress +  inflatedHash + isArchive    + \
            fileNameLen +  fileName
            
        md5Hash = hashlib.md5()
        md5Hash.update('allocator')
        md5Hash   = md5Hash.digest()
        encryptor = Crypto.Cipher.ARC4.new(md5Hash)
        fileTable = encryptor.encrypt(fileTable)
        
        header  = '\x4D\x43\x50\x4B\x03\x00\x00\x00\x7F\x01\x00\x00'
        header += self.sha1(fileContents + fileTable)
        header += struct.pack('<L', 0x30 + len(fileContents))
        header += struct.pack('<L', len(self.currentData))
        header += '\x00' * 8
        
        patchFile = header + fileContents + fileTable
        writePatch = open(outputFile, 'wb')
        writePatch.write(patchFile)
        writePatch.close()


