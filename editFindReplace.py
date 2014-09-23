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
import re

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super(FindReplaceDialog, self).__init__(parent)
        self.parent = parent
        self.text = unicode(self.parent.tabbedWindow.currentWidget().textBox.toPlainText())

        findLabel = QLabel('     Find What:')
        self.findBox = QLineEdit()
        findButton = QPushButton('Find Next')
        replaceLabel = QLabel('Replace With:')
        self.replaceBox = QLineEdit()
        self.replaceButton = QPushButton('Replace')
        replaceAllButton = QPushButton('Replace All')
        resetCursor = QPushButton('Reset Cursor')
        doneButton = QPushButton('Done')
        self.matchCase = QCheckBox('Match Case')
        self.regexp  = QCheckBox('Regular Expression')

        self.matchCase.setChecked(True)
        self.findBox.setFocus(True)
        self.replaceButton.setEnabled(False)

        layout1 = QHBoxLayout()
        layout1.addWidget(findLabel)
        layout1.addWidget(self.findBox)
        layout2 = QHBoxLayout()
        layout2.addWidget(replaceLabel)
        layout2.addWidget(self.replaceBox)
        mainLayout = QGridLayout()
        mainLayout.addLayout(layout1, 0, 0)
        mainLayout.addWidget(findButton, 0, 1)
        mainLayout.addLayout(layout2, 1, 0)
        mainLayout.addWidget(self.replaceButton, 1, 1)
        mainLayout.addWidget(self.matchCase, 2, 0)
        mainLayout.addWidget(replaceAllButton, 2, 1)
        mainLayout.addWidget(self.regexp, 3, 0)
        mainLayout.addWidget(resetCursor, 3, 1)
        mainLayout.addWidget(doneButton, 4, 1)
        mainLayout.setColumnMinimumWidth(0, 300)
        self.setLayout(mainLayout)
        self.setWindowTitle('Find/Replace')

        findButton.clicked.connect(self.findText)
        doneButton.clicked.connect(self.close)
        resetCursor.clicked.connect(self.resetCursorPosition)
        self.regexp.toggled.connect(self.matchCase.setDisabled)
        self.regexp.toggled.connect(replaceAllButton.setDisabled)
        self.matchCase.toggled.connect(replaceAllButton.setEnabled)
        self.replaceButton.clicked.connect(self.replaceText)
        replaceAllButton.clicked.connect(self.replaceAllText)

    def replaceAllText(self):
        term = str(self.findBox.text())
        repl = str(self.replaceBox.text())
        self.text = self.text.replace(term, repl)
        self.parent.tabbedWindow.currentWidget().textBox.setText(self.text)

    def replaceText(self):
        replacementText = self.replaceBox.text()
        cursor = self.parent.tabbedWindow.currentWidget().textBox.textCursor()
        cursor.removeSelectedText()
        cursor.insertText(replacementText)
        self.parent.tabbedWindow.currentWidget().textBox.setTextCursor(cursor)
        self.replaceButton.setEnabled(False)
        self.text = unicode(self.parent.tabbedWindow.currentWidget().textBox.toPlainText())

    def resetCursorPosition(self):
        cursor = self.parent.tabbedWindow.currentWidget().textBox.textCursor()
        cursor.setPosition(0)
        self.parent.tabbedWindow.currentWidget().textBox.setTextCursor(cursor)

    def findText(self):
        regex = False
        cursor = self.parent.tabbedWindow.currentWidget().textBox.textCursor()
        cursorPos = cursor.position()
        term = str(self.findBox.text())
    
        if self.regexp.isChecked():
            match = re.search(term, self.text)
            if match:
                regex = True
                textIndex = match.start()
                textEnd = match.end()
            else:
                textIndex = -1
        elif self.matchCase.isChecked():
            textIndex = self.text[cursorPos:].find(term)
        else:
            textIndex = self.text.lower()[cursorPos:].find(term.lower())
        
        if regex:
            self.replaceButton.setEnabled(True)
            cursor.setPosition(textIndex)
            cursor.setPosition(textEnd, QTextCursor.KeepAnchor)
            self.parent.tabbedWindow.currentWidget().textBox.setTextCursor(cursor)
        elif textIndex != -1:
            self.replaceButton.setEnabled(True)
            cursor.setPosition(cursorPos + textIndex)
            cursor.setPosition(cursor.position() + len(term), QTextCursor.KeepAnchor)
            self.parent.tabbedWindow.currentWidget().textBox.setTextCursor(cursor)
        else:
            message = QMessageBox.information(self, 'No match', 'No matches were found.', QMessageBox.Ok)

    

