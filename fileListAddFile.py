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

class FileListAddFile(QDialog):
    def __init__(self, parent=None):
        super(FileListAddFile, self).__init__(parent)
        self.parent = parent
        # First Option
        self.option1 = QRadioButton("New File: ")
        self.option1.setChecked(True)
        self.newFileBox = QLineEdit()
        self.newFileBox.setFocus(True)
        label = QLabel("Example: data/design/buildings/residence/r1/h_low01_t1.class")
        

        # Second Option
        self.option2 = QRadioButton("Existing File: ")
        self.exiFileBox = QLineEdit()
        self.exiFileBox.setEnabled(False)
        self.browser = QPushButton ("Browse")
        self.browser.setEnabled(False)

        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)        
        self.buttons.button(QDialogButtonBox.Ok).setDefault(True)

        # Layouts
        lay1 = QHBoxLayout()
        lay2 = QHBoxLayout()
        lay1.addWidget(self.option1)
        lay1.addWidget(self.newFileBox)
        lay2.addWidget(self.option2)
        lay2.addWidget(self.exiFileBox)
        lay2.addWidget(self.browser)
        layout = QVBoxLayout()
        layout.addLayout(lay1)
        layout.addWidget(label)
        layout.addLayout(lay2)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        # Connections
        self.browser.clicked.connect(self.getFileName)
        self.option1.toggled.connect(self.newFileBox.setEnabled)
        self.option2.toggled.connect(self.browser.setEnabled)
        self.option2.toggled.connect(self.exiFileBox.setEnabled)
        self.connect(self.newFileBox, SIGNAL("returnPressed()"), self, SLOT("accept()"))
        self.connect(self.exiFileBox, SIGNAL("returnPressed()"), self, SLOT("accept()"))
        self.connect(self.buttons, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(self.buttons, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.newFileBox.textChanged.connect(self.isValid)
        self.exiFileBox.textChanged.connect(self.isValid2)

        # Window configuration
        self.setWindowTitle('Add new file')
        self.resize(500,100)

    def isValid2(self):
        if self.exiFileBox.text() != "":
            self.buttons.button(QDialogButtonBox.Ok).setEnabled(True)
    def isValid(self):
        button = self.buttons.button(QDialogButtonBox.Ok)
        text = str(self.newFileBox.text())
        if '.' not in text:
            button.setEnabled(False)
        elif text[:5].lower() != 'data/':
            button.estEnabled(False)
        elif text[text.find('.'):].lower() not in self.parent.acceptedFileFormats:
            button.setEnabled(False)
        elif text in self.parent.currentData:
            button.setEnabled(False)
        else:
            button.setEnabled(True)

    def getFileName(self):
        fileName = QFileDialog.getOpenFileName(self, "Add Existing File", ".", '\n'.join(self.parent.formats2))
        if fileName:
            self.exiFileBox.setText(fileName)
