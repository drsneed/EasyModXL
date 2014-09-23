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


class FileListCloneFile(QDialog):
    def __init__(self, parent=None):
        super(FileListCloneFile, self).__init__(parent)
        self.parent = parent
        self.oldName    = str(parent.fileList.currentItem().parent.ID)
        self.label      = QLabel("New file name:")
        if self.oldName.endswith('.sgbin'):
            self.label.setText("Warning! Changing the name of a "
                               "sgbin will corrupt the file. Only change the path"
                               " leading up the file name in this case. Enter new"
                               " file name: "
                                )
        
        self.newNameBox = QLineEdit(self.oldName)
        self.newNameBox.setFocus(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setDefault(True)
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        
        self.newNameBox.textChanged.connect(self.verifyName)
        self.connect(self.buttons, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(self.buttons, SIGNAL("rejected()"), self, SLOT("reject()"))

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.newNameBox)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        self.setWindowTitle("Clone File")
        self.resize(400,200)

    def verifyName(self):
        text = str(self.newNameBox.text())
        button = self.buttons.button(QDialogButtonBox.Ok)
        if text == self.oldName:
            button.setEnabled(False)
        elif '.' not in text:
            button.setEnabled(False)
        elif text[:5].lower() != 'data/':
            button.setEnabled(False)
        elif text[text.find('.'):] not in self.parent.acceptedFileFormats:
            button.setEnabled(False)
        else:
            button.setEnabled(True)





        
        
