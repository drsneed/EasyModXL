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
import re

class SyntaxDebugger(QDialog):
    def __init__(self, parent=None):
        super(SyntaxDebugger, self).__init__(parent)
        self.parent  = parent
        self.label   = QLabel("Select a file to check: ")
        self.listBox = QListWidget()
        self.logBox  = QTextBrowser()
        self.result  = QLabel("Click debug to continue")
        self.debug   = QPushButton("Debug")
        self.done    = QPushButton("Done")
        buttonBox    = QHBoxLayout()
        vertical     = QVBoxLayout()
        
        buttonBox.addWidget(self.debug)
        buttonBox.addWidget(self.done)
        vertical.addWidget(self.label)
        vertical.addWidget(self.listBox)
        vertical.addWidget(self.logBox)
        vertical.addWidget(self.result)
        vertical.addLayout(buttonBox)
        
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Syntax Debugger")
        self.setLayout(vertical)
        self.resize(600,600)

        for files in self.parent.currentFiles:
            if files.hasTabOpen:
                self.listBox.addItem(files.ID)

        # Connect buttons to functions
        self.debug.clicked.connect(self.debugData)
        self.done.clicked.connect(self.Done)
        self.resize(500,300)
    def Done(self):
        self.close()
    def debugData(self):
        self.logBox.setText("")
        text = str(self.parent.currentData[str(self.listBox.currentItem().text())])
        copyOfText = text
        frontTag = re.compile('<([a-zA-Z0-9_]*)>')
        backTag  = '</(%s)>'
        errorCount = 0
        while True:
            tagFound = frontTag.search(text)
            if tagFound:
                ft = tagFound.group(1)
                loc = tagFound.span()
                match = re.search(backTag % ft, text)
                if match:
                    bt = match.group(1)
                    textB4firstTag  = text[ : text.find('<'+ft+'>')]
                    text = textB4firstTag  + text[len(textB4firstTag)  + len(ft) + 2 : ]
                    textB4secondTag = text[ : text.find('</'+bt+'>')]
                    text = textB4secondTag + text[len(textB4secondTag) + len(bt) + 2 : ]
                else:
                    errorCount = errorCount + 1
                    text = text[text.find(ft) + len(ft) :]
                    self.logBox.append("<font color=blue>(%s, %s)</font> <font color=red>"
                                       "No closing tag for &lt;%s&gt;</font>" % (loc[0],loc[1], ft))      
            else:
                break
        hangingBrackets = re.findall('[>\n\t]([a-zA-Z0-9_]*)>(?<!<)|<([a-zA-Z0-9_]*)[<\n\t](?!>)', copyOfText)
        for leftBracket, rightBracket in hangingBrackets:
            if leftBracket:
                errorCount = errorCount + 1
                self.logBox.append('<font color = red>Missing left bracket: %s&gt;</font>' % leftBracket)
            if rightBracket:
                errorCount = errorCount + 1
                self.logBox.append('<font color = red>Missing right bracket: %s&gt;</font>' % rightBracket)
        if not errorCount:
            self.result.setText("<font color = green>No errors were found.</font>")
        else:
            self.result.setText("<font color = red>%d error%s found.</font>" % (errorCount, 's' if errorCount != 1 else ''))

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent = None):
        super(SyntaxHighlighter, self).__init__(parent)
        xmlFormat = QTextCharFormat()
        xmlFormat.setForeground(Qt.darkCyan)
        self.highlightingRules = [(QRegExp("<[?\" \.=\-a-zA-Z0-9/_]*>"), xmlFormat)]

        self.commentStartExpression = QRegExp("<!--")
        self.commentEndExpression   = QRegExp("-->")

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(Qt.red)

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState(0)
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)
        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text, startIndex + commentLength)
            
        
                                   
                
                    










        
        
        
        
