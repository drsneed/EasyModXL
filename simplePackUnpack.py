from PyQt4.QtCore import *
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

from PyQt4.QtGui import *
from packunpack2 import PatchFile, DataFolder
class SimplePackUnpack(QDialog):
    def __init__(self, parent=None):
        super(SimplePackUnpack, self).__init__(parent)
        unpackGroup = QGroupBox("Unpack a patch file")
        patchFile = QPushButton("Patch file")
        self.patchLine = QLineEdit()
        outputDir = QPushButton("Output directory")
        self.outputLine = QLineEdit()
        unpackButton = QPushButton("Unpack")
        unpackButton.setMaximumWidth(100)
        self.feedback = QLabel()
        
        unpackLay = QGridLayout(unpackGroup)
        unpackLay.addWidget(patchFile, 0, 0)
        unpackLay.addWidget(self.patchLine, 0, 1)
        unpackLay.addWidget(outputDir, 1, 0)
        unpackLay.addWidget(self.outputLine, 1, 1)
        unpackLay.addWidget(self.feedback, 2, 0)
        unpackLay.addWidget(unpackButton, 2, 1, Qt.AlignRight)
        
        packGroup = QGroupBox('Pack a data folder')
        dataFolder = QPushButton('Data folder')
        self.dataLine = QLineEdit()
        outputFile = QPushButton("Output file")
        self.outputLine2 = QLineEdit()
        packButton = QPushButton("Pack")
        packButton.setMaximumWidth(100)
        self.feedback2 = QLabel()
        packLay = QGridLayout(packGroup)
        packLay.addWidget(dataFolder, 0, 0)
        packLay.addWidget(self.dataLine, 0, 1)
        packLay.addWidget(outputFile, 1, 0)
        packLay.addWidget(self.outputLine2, 1, 1)
        packLay.addWidget(self.feedback2, 2, 0)
        packLay.addWidget(packButton, 2, 1, Qt.AlignRight)
        
        doneButton = QPushButton("Done")
        doneButton.setMaximumWidth(100)
        quickFix = QHBoxLayout()
        quickFix.addWidget(doneButton)
        
        patchFile.clicked.connect(self.findPatchFile)
        outputDir.clicked.connect(self.findOutputDir)
        dataFolder.clicked.connect(self.findDataFolder)
        outputFile.clicked.connect(self.findOutputFile)
        doneButton.clicked.connect(self.close)
        packButton.clicked.connect(self.makePatch)
        unpackButton.clicked.connect(self.makeData)
        mainLay = QVBoxLayout()
        mainLay.addWidget(unpackGroup)
        mainLay.addWidget(packGroup)
        mainLay.addLayout(quickFix)
        self.setLayout(mainLay)
        self.setWindowTitle("Simple Pack/Unpack")
        self.resize(600, 200)
        
    def findPatchFile(self):
        formats = [
            "Patch file (*.patch)",
            "Pak file (*.pak)"
            ]
        filename = QFileDialog.getOpenFileName(self, "Get patch file",
                    ".", '\n'.join(formats))
        if filename:
            self.patchLine.setText(filename)
    
    def findOutputDir(self):
        dir_ = QFileDialog.getExistingDirectory(self, "Data folder", ".")
        if dir_:
            self.outputLine.setText(str(dir_).replace('\\','/'))
    
    def findDataFolder(self):
        dir_ = QFileDialog.getExistingDirectory(self, "Data folder", ".")
        if dir_:
            self.dataLine.setText(str(dir_).replace('\\', '/'))
    
    def findOutputFile(self):
        formats = [
            "Patch file (*.patch)",
            "Pak file (*.pak)"
            ]
        filename = QFileDialog.getSaveFileName(self, "Save patch file",
                    ".", '\n'.join(formats))
        if filename:
            self.outputLine2.setText(filename)

    def makePatch(self):
        try:
            self.feedback2.setText("Processing, please wait...")
            QCoreApplication.processEvents()
            data = DataFolder(str(self.dataLine.text()))
            data.packInto(str(self.outputLine2.text()))
            msg = QMessageBox.information(self, "Success", "%s successfully created." % \
                                          str(self.dataLine.text()), QMessageBox.Ok)
            self.feedback2.setText("")
        except:
            msg = QMessageBox.warning(self, "Failure", "Operation failed", QMessageBox.Ok)
            
    def makeData(self):
        try:
            self.feedback.setText("Processing, please wait...")
            QCoreApplication.processEvents()
            patch = PatchFile(str(self.patchLine.text()))
            patch.unpackInto(str(self.outputLine.text()))
            msg = QMessageBox.information(self, "Success", "%s successfully created." % \
                                          str(self.patchLine.text()), QMessageBox.Ok)
            self.feedback.setText("")
        except:
            msg = QMessageBox.warning(self, "Failure", "Operation failed", QMessageBox.Ok)
