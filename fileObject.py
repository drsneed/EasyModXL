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
from xmlSyntax import SyntaxHighlighter

class File(QWidget):
    unsavedAlert = pyqtSignal(QWidget)
    def __init__(self, fullPath, contents, addTab=True, parent=None):
        super(File, self).__init__(parent)
        self.parent = parent
        self.ID = fullPath
        self.Name = os.path.split(str(fullPath))[1]
        self.fileType = os.path.splitext(self.Name)[1]
        self.contents = contents
        self.isEditable = bool(self.fileType in parent.editableFileTypes)
        self.hasTabOpen = False

        if self.isEditable and addTab:
            if self.ID[-6:] == '.class':
                self.tabRep = TabRepresentative(self)
                self.hasTabOpen = True
        self.listRep = ListRepresentative(None, self)
        parent.fileList.addItem(self.listRep)
        parent.showFullPaths.toggled.connect(self.toggleDisplay)

    def toggleDisplay(self, showFullPath):
        if showFullPath:
            self.listRep.setText(self.ID)
        else:
            self.listRep.setText(self.Name)

    def die(self, indexOfFile):
        if self.hasTabOpen:
            self.parent.tabbedWindow.removeTab(self.parent.tabbedWindow.indexOf(self.tabRep))
        del self.parent.currentData[self.ID]
        self.parent.showFullPaths.toggled.disconnect(self.toggleDisplay)
        self.parent.currentFiles.remove(self)
        trash = self.parent.fileList.takeItem(indexOfFile)
        del trash
        del self.listRep
        del self

    def addToTabs(self):
        tabIndex = self.parent.tabbedWindow.count()
        self.tabRep = TabRepresentative(self)
        self.hasTabOpen = True
        self.listRep.setFont(self.listRep.openTabFont)
        self.parent.tabbedWindow.setCurrentIndex(tabIndex)
        self.parent.tabbedWindow.currentWidget().textBox.setFocus(True)

    def updateName(self, newName):
        del self.parent.currentData[self.ID]
        self.ID = newName
        self.parent.currentData[self.ID] = self.contents
        self.listRep.ID = newName
        self.Name = os.path.split(newName)[1]
        if self.parent.showFullPaths.isChecked():
            self.listRep.setText(newName)
        else:
            self.listRep.setText(self.ID)
        self.listRep.setToolTip(newName)
        self.listRep.setStatusTip(newName)
        if self.hasTabOpen:
            self.tabRep.ID = self.ID
            self.tabRep.label.setText(self.ID)
            self.parent.tabbedWindow.setTabToolTip(self.parent.tabbedWindow.indexOf(self.tabRep), self.ID)
            self.parent.tabbedWindow.setTabText(self.parent.tabbedWindow.indexOf(self.tabRep), self.Name)

class ListRepresentative(QListWidgetItem):
    def __init__(self, parent=None, realParent=None):
        QListWidgetItem.__init__(self)
        self.parent = realParent
        self.openTabFont = QFont()
        self.openTabFont.setBold(True)
        self.defaultFont = QFont()
        if self.parent.parent.showFullPaths.isChecked():
            self.setText(self.parent.ID)
        else:
            self.setText(self.parent.Name)
        if self.parent.hasTabOpen:
            self.setFont(self.openTabFont)
        if not self.parent.isEditable:
            self.setForeground(Qt.gray)
        try:
            self.setIcon(QIcon(self.parent.parent.fileListIcons[self.parent.fileType]))
        except KeyError:
            pass
        self.setToolTip(self.parent.ID)
        self.setStatusTip(self.parent.ID)
        
class TabRepresentative(QWidget):
    unsavedAlert = pyqtSignal(QWidget)
    def __init__(self, parent=None):
        super(TabRepresentative, self).__init__(parent)
        self.parent = parent
        self.ID = parent.ID
        self.label = QLabel(self.ID)
        self.textBox = QTextEdit()
        self.textBox.setLineWrapMode(QTextEdit.NoWrap)
        self.textBox.setFont(QFont("Courier", 11))
        self.textBox.setText(self.parent.contents)
        tabLayout = QVBoxLayout(self)
        tabLayout.addWidget(self.label)
        tabLayout.addWidget(self.textBox)
        self.parent.parent.editUndo.setEnabled(self.textBox.document().isUndoAvailable())
        self.parent.parent.editRedo.setEnabled(self.textBox.document().isRedoAvailable())
        self.textBox.document().modificationChanged.connect(self.setChanged)
        self.textBox.document().modificationChanged.connect(self.parent.parent.setWindowModified)
        self.textBox.document().undoAvailable.connect(self.parent.parent.editUndo.setEnabled)
        self.textBox.document().redoAvailable.connect(self.parent.parent.editRedo.setEnabled)   
        syntaxHighlighter = SyntaxHighlighter(self.textBox.document())
        self.unsavedAlert.connect(self.parent.parent.toggleSaveOn)
        self.parent.parent.tabbedWindow.addTab(self, self.parent.Name)
        self.parent.parent.tabbedWindow.setTabToolTip(self.parent.parent.tabbedWindow.indexOf(self), self.ID)
        self.parent.parent.tabbedWindow.setCurrentWidget(self)

    def setChanged(self):
        self.unsavedAlert.emit(self)
    def removeFromTabs(self):
        self.parent.parent.tabbedWindow.removeTab(self.parent.parent.tabbedWindow.indexOf(self))
        self.parent.hasTabOpen = False
        self.parent.listRep.setFont(self.parent.listRep.defaultFont)
