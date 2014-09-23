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

from   PyQt4.QtCore import *
from   PyQt4.QtGui import *

class FileList(QListWidget):
    dropReceived = pyqtSignal(list)

    def __init__(self, parent=None):
        super(FileList, self).__init__(parent)
        self.parent = parent
        self.setObjectName("FileList")
        self.setMaximumSize(200,500)
        self.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.style1 = '''#FileList{background-color:#3366FF;}'''
        self.style2 = '''#FileList{background-color:#e6e6e6;}'''
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultSettings()
        
    def setDefaultSettings(self):
        self.setStyleSheet(self.style2)
        # Add more defaults here
    def dragEnterEvent(self, event):
        self.setStyleSheet(self.style1)
        event.acceptProposedAction()
    def dragMoveEvent(self, event):
        event.acceptProposedAction()
    def dragLeaveEvent(self, event):
        self.setDefaultSettings()
        #event.acceptProposedAction()
    def dropEvent(self, event):
        self.parent.activateWindow()
        self.setStyleSheet(self.style2)
        mimeData = event.mimeData()
        dataToSend = [  ]
        if mimeData.hasUrls():
            for _url_ in mimeData.urls():
                dataToSend.append(_url_.path()[1:])
            self.dropReceived.emit(dataToSend)
            event.acceptProposedAction()
