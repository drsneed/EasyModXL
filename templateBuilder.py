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
from PyQt4.QtCore import *
import os

class TemplateBuilder(QDialog):
    def __init__(self, parent=None):
        super(TemplateBuilder, self).__init__(parent)
        self.parent = parent
        info = QLabel("Browse for a base file to build a template")
        browseButton = QPushButton("Browse")
        browseButton.setMaximumWidth(110)
        self.results = QLabel()
        self.results.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.feedback = QLabel()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout()
        layout.addWidget(info)
        layout.addWidget(browseButton)
        layout.addWidget(self.results)
        layout.addWidget(self.feedback)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        self.connect(self.buttons, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(self.buttons, SIGNAL("rejected()"), self, SLOT("reject()"))
        browseButton.clicked.connect(self.makeTemplate)
        self.dataDict = { }
        self.setWindowTitle("Template Builder")
        self.resize(400,400)

    def getFiles(self, root, baseName):
        for path, subdirs, files in os.walk(root):
            for name in files:
                if baseName in name:
                    yield path + '/' + name
        
    def makeTemplate(self):
        baseFile = QFileDialog.getOpenFileName(self, 'Base File', '.', '\n'.join(self.parent.formats2))
        if not baseFile: return
        self.feedback.setText("Searching for matching files... This may take a minute.")
        QCoreApplication.processEvents()
        baseFile = str(baseFile)
        baseName = os.path.splitext(os.path.split(baseFile)[1])[0]
        dataFolder = baseFile[:baseFile.find('/data/') + 6]
        matchingFiles = list(self.getFiles(dataFolder, baseName))
        if not matchingFiles:
            self.feedback.setText('<font color=red>No matches found</font>')
            return
        results = ''
        for match in matchingFiles:
            results += os.path.split(match)[1] + '\n'
            self.results.setText(results)
            data = open(match, 'rb').read()
            name = match[match.find('/data/')+1 :]
            self.dataDict[name] = data
        self.feedback.setText("<font color = green>Found %d files. Click Ok to generate template</font>" % len(matchingFiles))
        
            
