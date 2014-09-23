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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from   packunpack2       import PatchFile, EMXLProject
import os

class WorkerThread(QThread):
    isRunning = pyqtSignal()
    isDone    = pyqtSignal(dict)
    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.parent = parent
        self.processedDict = { }
        self.parent.fileList.dropReceived.connect(self.initializeThread)

    def __del__(self):
        self.wait()

    def case(self, element, *idx):
        return bool(
            element in map(
                lambda _: self.parent.acceptedFileFormats[_], idx
            )
        )
    
    def getFiles(self, root):
        for path, subdirs, files in os.walk(root):
            for name in files:
              yield path + '/' + name
              
    def parseDataFolder(self, dataDir):
        output = { }
        for path in list(self.getFiles(str(dataDir))):
            if os.path.splitext(path)[1] in self.parent.acceptedFileFormats:
                f = open(path, 'rb').read()
                path = path.replace('\\', '/')
                if path.lower().startswith('data/') or '/data/' in path:
                    p = path[path.find('data'):]
                else:
                    p = path
                output[p] = f
        return output
    
    def initializeThread(self, dataReceived):
        self.dataReceived = dataReceived
        self.isRunning.emit()
        self.start()

    def run(self):
        fileDict = { }
        for path in self.dataReceived:
            path = str(path)
            fileType = os.path.splitext(path)
            fileType = 'data' if not fileType[1] else fileType[1]
            if self.case(fileType, 0): # data
                parsedData = self.parseDataFolder(path)
            elif self.case(fileType, 1, 2): # patch, pak
                patch = PatchFile(path)
                parsedData = patch.fileDict
            elif self.case(fileType, 3, 4, 5, 11, 12, 13, 14, 15):
                contents = open(path, 'rb').read( )
                if '/data/' in path:
                    parsedData = {path[path.find('/data/')+1:] : contents}
                else:
                    parsedData = {path: contents}
            elif self.case(fileType, 6, 7, 8, 9, 10): # localization
                contents = open(path, 'rb').read()
                #contents = contents.replace('\x00', '') # strip null terminators
                if '/data/' in path:
                    parsedData = {path[path.find('/data/')+1:] : contents}
                else:
                    parsedData = {path : contents}
            else:
                continue
            fileDict.update(parsedData)
        self.isDone.emit(fileDict)
