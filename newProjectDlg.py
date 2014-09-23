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

from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import QDialog, QRadioButton, QDialogButtonBox, QHBoxLayout, \
	 QVBoxLayout, QComboBox

class NewProjectDlg(QDialog):
    def __init__(self, parent=None):
        super(NewProjectDlg, self).__init__(parent)
        self.items = [ ]
        for i in range(1, 21):
            self.items.append("template %d" % i)
        self.option1 = QRadioButton("New empty project")
        self.option1.setChecked(True)
        self.option2 = QRadioButton("New project from template")
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setDefault(True)
        self.connect(self.buttons, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(self.buttons, SIGNAL("rejected()"), self, SLOT("reject()"))   
        regLayout = QVBoxLayout()
        regLayout.addWidget(self.option1)
        regLayout.addWidget(self.option2)
        regLayout.addWidget(self.buttons)
        self.setLayout(regLayout)
        self.setWindowTitle("New Project")
        self.resize(190, 100)

		 
