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

class RecentFileAction(QAction):
    actionClicked = pyqtSignal(str)
    def __init__(self, text, parent=None):
        super(RecentFileAction, self).__init__(parent)
        self.customText = text
        self.setText(text)
        self.setToolTip(text)
        self.setStatusTip(text)
        self.triggered.connect(self.connectAction)
    def connectAction(self):
        self.actionClicked.emit(self.customText[2:])
