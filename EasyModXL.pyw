#---------------------------------------------------------------------------#
# Copyright (C) 2012 Dustin Sneeden                                         #
# EasyMod XL - Open Source Mod Editor for Cities XL                         #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
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

import sip
sip.setapi('QVariant', 2)

import os
import re
import sys
import pickle
import resources
from   templateWizard    import *
from   PyQt4.QtCore      import *
from   PyQt4.QtGui       import *
from   packunpack2       import PatchFile, EMXLProject
from   recentFileAction  import RecentFileAction
from   fileList          import FileList
from   fileObject        import File, TabRepresentative
from   xmlSyntax         import SyntaxDebugger
from   fileListAddFile   import FileListAddFile
from   fileListCloneFile import FileListCloneFile
from   newFileName       import PromptForNewFileName
from   editFindReplace   import FindReplaceDialog
from   newProjectDlg     import NewProjectDlg
from   simplePackUnpack  import SimplePackUnpack
from   workerThread      import WorkerThread
from   templateBuilder   import TemplateBuilder

class EasyModXL(QMainWindow):
    def __init__(self, configuration):
        super(EasyModXL, self).__init__()
        self.editableFileTypes = (
            '.en', '.es', '.de', '.fr','.fx',
            '.it', '.lua', '.class', '.layout',
            '.cfg', '.xml', '.actor','.saynete'
            )
        self.acceptedFileFormats = (
            'data', '.patch', '.pak', '.lua',
            '.class', '.layout', '.en', '.es',
            '.de', '.fr', '.it', '.sgbin','.actor',
            '.fnt','.planet', '.tga','.fx','.wav',
            '.dds', '.ava', '.lvl', '.gfx', '.png',
            '.motion', '.cfg', '.xml','.saynete', '.body',
            )
        self.fileListIcons = {
            '.class':':/img/editable.png', '.layout':':/img/editable.png',
            '.sgbin':':/img/model.png', '.dds' :':/img/thumb.png',
            '.png':':/img/thumb.png','.actor':':/img/editable.png',
            '.cfg': ':img/editable.png', '.xml':':/img/editable.png',
            '.en':':/img/editable.png', '.de'  :':/img/editable.png',
            '.es':':/img/editable.png', '.fr'  :':/img/editable.png',
            '.it':':/img/editable.png', '.lua' :':/img/editable.png',
            '.saynete': ':/img/editable.png', '.tga':'/img/thumb.png'
            }
        self.formats2 = [f[1:] + ' file (*%s)' % f for f in self.acceptedFileFormats[2:]]
        self.currentProject = None
        self.unsavedChanges = False
        self.currentData    = { }
        self.unsavedTabs    = [ ]
        self.currentFiles   = [ ]
        self.recentFileList = [ ]

        self.setupMenuActions( )
        self.tabbedWindow = QTabWidget( )
        self.tabbedWindow.setTabsClosable(True)
        self.tabbedWindow.currentChanged.connect(self.tabChanged)
        self.tabbedWindow.tabCloseRequested.connect(self.closeTab)

        self.fileListOptions = QWidget()
        self.fileListOptions.setMaximumSize(215, 75)
        self.openTabsForNewFiles = QCheckBox("Auto-open tabs for class files")
        self.clearFilesForNewDrops = QCheckBox("Clear files for new drops")
        self.clearFilesForNewDrops.setChecked(True)
        self.showFullPaths = QCheckBox("Show full paths")
        self.fileListOptionsLayout = QVBoxLayout(self.fileListOptions)
        self.fileListOptionsLayout.addWidget(self.openTabsForNewFiles)
        self.fileListOptionsLayout.addWidget(self.clearFilesForNewDrops)
        self.fileListOptionsLayout.addWidget(self.showFullPaths)
                
        self.fileListContainer = QWidget()
        self.fileList = FileList(self)
        self.fileList.itemDoubleClicked.connect(self.itemSelectedListener)
        self.fileList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fileList.customContextMenuRequested.connect(self.updateFileListContextMenu)
        self.setupFileListContextMenu()
        self.setupFileListHeader()

        self.worker = WorkerThread(self)
        self.worker.isRunning.connect(self.showLoadingGif)
        self.worker.isDone.connect(self.dataReceivedFromWorkerThread)
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setVisible(False)
        self.fileListLayout = QVBoxLayout(self.fileListContainer)
        self.fileListLayout.addLayout(self.fileListHeader)
        self.fileListLayout.addWidget(self.fileList)
        self.fileListLayout.addWidget(self.progressBar)

        self.listOptions = QDockWidget("File list options", self)
        self.listOptions.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.listOptions.setWidget(self.fileListOptions)

        self.sidebar = QDockWidget("File list", self)
        self.sidebar.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.sidebar.setWidget(self.fileListContainer)

        self.status = QLabel()
        self.status.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().addPermanentWidget(self.status)
        self.statusBar().showMessage("Ready", 5000)

        self.setCentralWidget(self.tabbedWindow)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.listOptions)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)
        self.setWindowTitle("EasyMod XL")
        self.setWindowIcon(QIcon(':/img/EasyModXL.png'))



        self.config = configuration
        if self.config is not None:
            self.resize(self.config['windowSize'])
            self.move(self.config['windowPosition'])
            if 'recentFiles' in self.config.keys():
                self.recentFileList = self.config['recentFiles']
            if 'currentProject' in self.config.keys():
                QTimer.singleShot(0, self.loadInitialFile)
        else:
            self.resize(1000, 600)

    #---------------------------Begin Functions---------------------------#
    # All functions are in alphabetical order.                            #
    #---------------------------------------------------------------------#

    def activateProgressBar(self, uselessString):
        self.progressBar.setVisible(True)

    def deactivateProgressBar(self, uselessString):
        self.progressBar.setValue(100)
        self.progressBar.setVisible(False)
        self.progressBar.setValue(0)
        
    def autoComplete(self):
        startIndex = -1
        cursor = self.tabbedWindow.currentWidget().textBox.textCursor()
        text = unicode(self.tabbedWindow.currentWidget().textBox.toPlainText())
        if text[cursor.position()-1] == '>':
            for i in range(len(text[:cursor.position()-1]), 0, -1):
                if text[i] == '<':
                    startIndex = i + 1
                    break
            if startIndex == -1:
                if text[0] == '<':
                    startIndex = 1
                else:
                    return
            tag = '</' + text[startIndex:cursor.position()]
            cursor.insertText(tag)
            cursor.setPosition(cursor.position() - len(tag))
            self.tabbedWindow.currentWidget().textBox.setTextCursor(cursor)
            
    def addActions_(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
                
    
    def clearAll(self):
        self.fileList.clear()
        self.tabbedWindow.clear()
        self.unsavedTabs = [ ]
        for fileObj in self.currentFiles:
            self.showFullPaths.toggled.disconnect(fileObj.toggleDisplay)
            del fileObj.listRep
            del fileObj
        self.currentFiles = [ ]
        self.currentData = { }
        self.unsavedChanges = False

    def closeEvent(self, event):
        if not self.proceed(): event.ignore()
        if self.config == None:
            self.config = {}
        self.config['windowSize'] = self.size()
        self.config['windowPosition'] = self.pos()
        self.config['currentProject'] = self.currentProject
        self.config['recentFileList'] = self.recentFileList[-10:]
        customPath = os.environ.get("LOCALAPPDATA") + "\\EasyModXL"
        if not os.path.exists(customPath):
            os.mkdir(customPath)
        fname = customPath + '\\' + "settings.cfg"
        output = open(fname, 'wb')
        pickle.dump(self.config, output)
        output.close()

    def closeTab(self, tabIdx):
        if self.tabbedWindow.widget(tabIdx) in self.unsavedTabs:
            if self.proceed():
                self.tabbedWindow.widget(tabIdx).removeFromTabs()
        else:
            self.tabbedWindow.widget(tabIdx).removeFromTabs()
        
    def dataReceivedFromWorkerThread(self, fileDict):
        self.gifHolder.setVisible(False)
        self.gif.stop()
        if not fileDict: return
        self.statusBar().showMessage("Updating UI", 1000)
        self.progressBar.setVisible(True)
        self.progressBar.setValue(10)
        toRemove = []
        toAdd    = {}
        for item in fileDict:
            self.progressBar.setValue(self.progressBar.value()+2)
            if item.lower()[:5] != 'data/':
                newFileName = self.promptForNewFileName(item)
                if newFileName:
                    toAdd[str(newFileName)] = fileDict[item]
                toRemove.append(item)
        for things in toRemove:
            del fileDict[things]
        fileDict.update(toAdd)
        if self.clearFilesForNewDrops.isChecked():
            self.clearAll()
            for item in sorted(fileDict.iterkeys()):
                self.progressBar.setValue(self.progressBar.value()+2)
                self.currentData[item] = fileDict[item]
                fileObject = File(item, fileDict[item], self.openTabsForNewFiles.isChecked(), self)
                QCoreApplication.processEvents()
                self.currentFiles.append(fileObject)
        else:
            for item in self.currentFiles:
                self.progressBar.setValue(self.progressBar.value()+2)
                if item.ID in fileDict:
                    overwrite = QMessageBox.warning(self, "Overwrite File", "Overwrite %s?"% \
                                item.ID, QMessageBox.Yes | QMessageBox.No)
                    if overwrite == QMessageBox.No:
                        del fileDict[item.ID]
                    elif overwrite == QMessageBox.Yes:
                        if item.hasTabOpen:
                            item.tabRep.textBox.setText(fileDict[item.ID])
                        self.currentData[item.ID] = fileDict[item.ID]
                        del fileDict[item.ID]
                    else:
                        del fileDict[item.ID]
            for item in sorted(fileDict.iterkeys()):
                self.progressBar.setValue(self.progressBar.value()+2)
                fileObj = File(item, fileDict[item], self.openTabsForNewFiles.isChecked(), self)
                QCoreApplication.processEvents()
                self.currentFiles.append(fileObj)
                self.currentData[item] = fileDict[item]
        self.progressBar.setValue(100)
        self.progressBar.setVisible(False)

            
    def editUndo_(self):
        self.tabbedWindow.currentWidget().textBox.undo
    def editRedo_(self):
        self.tabbedWindow.currentWidget().textBox.redo
    def editFindReplace(self):
        if self.tabbedWindow.count() == 0:
            QMessageBox.information(self, "No files open", "A file needs to be opened to use this feature.", QMessageBox.Ok)
            return
        findReplace = FindReplaceDialog(self)
        findReplace.show()
    def editCopy(self):
        self.tabbedWindow.currentWidget().textBox.copy
    def editCut(self):
        self.tabbedWindow.currentWidget().textBox.cut
    def editPaste(self):
        self.tabbedWindow.currentWidget().textBox.paste
    def fileExport(self):
        outputDir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if outputDir:
            File__ = PatchFile(None, self.currentData)
            File__.unpackInto(outputDir)
            
            
    def fileConvert(self):
        if not self.proceed(): return
        patchFile = QFileDialog.getSaveFileName(self, "Save Project",
                   ".", "Patch File (*.patch)")
        try:
            datafolder = EMXLProject(self.currentData)
            datafolder.packInto(patchFile)
            msg = QMessageBox.information(self, "Success", "%s successfully created." % patchFile, QMessageBox.Ok)
            self.statusBar().showMessage("%s successfully created." % patchFile, 5000)
        except:
            msg = QMessageBox.warning(self, "Failure", "Creation of patch file failed.", QMessageBox.Ok)
    def fileQuit(self):
        self.close()
    def fileListAddFile(self):
        newFile = FileListAddFile(self)
        if newFile.exec_():
            if newFile.option1.isChecked():
                fileName = str(newFile.newFileBox.text())
                contents = ''
            elif newFile.option2.isChecked():
                fileName = str(newFile.exiFileBox.text())
                newFileName = self.promptForNewFileName(fileName)
                if newFileName == None: return
                contents = open(fileName, 'rb').read()
                fileName = newFileName
            self.currentData[fileName] = contents
            fileObj = File(fileName, contents, self.openTabsForNewFiles.isChecked(), self)
            self.currentFiles.append(fileObj)
            
    def fileListDeleteAll(self):
        answer = QMessageBox.question(self, "Are you sure?",
                 "Are you sure you want to remove all files from this project?",
                 QMessageBox.Yes|QMessageBox.Cancel)
        if answer == QMessageBox.Yes:
            self.clearAll()
    def fileListCloneFile(self):
        newFileName = FileListCloneFile(self)
        if newFileName.exec_():
            contents = self.currentData[self.fileList.currentItem().parent.ID]
            fileName = str(newFileName.newNameBox.text())
            self.currentData[fileName] = contents
            fileObj = File(fileName, contents, self.openTabsForNewFiles.isChecked(), self)
            self.currentFiles.append(fileObj)
    def fileListCopyPath(self):
            QApplication.clipboard().setText(self.fileList.currentItem().parent.ID)
    def fileListDeleteFile(self):
        answer = QMessageBox.question(self, "Are you sure?",
                 "Are you sure you want to delete %s?" % \
                 self.fileList.currentItem().parent.ID,
                 QMessageBox.Yes|QMessageBox.Cancel)
        if answer == QMessageBox.Yes:
            fileListIndex = self.fileList.currentRow()
            self.fileList.currentItem().parent.die(fileListIndex)

    def fileListRemoveTab(self):
        if self.fileList.currentItem().parent.tabRep in self.unsavedTabs:
            if self.proceed():
                self.fileList.currentItem().parent.tabRep.removeFromTabs()
        else:
            self.fileList.currentItem().parent.tabRep.removeFromTabs()
    def fileListRemoveAllTabs(self):
        if self.unsavedTabs:
            if not self.proceed(): return
        for fileObj in self.currentFiles:
            if fileObj.hasTabOpen:
                fileObj.tabRep.removeFromTabs()
    def fileListRenameFile(self):
        newFileName = self.promptForNewFileName(self.fileList.currentItem().parent.ID)
        if newFileName is not None:
            self.fileList.currentItem().parent.updateName(newFileName)

    def fileListSortFiles(self):
        self.fileList.sortItems(Qt.AscendingOrder)
        
    def fileNew(self):
        if not self.proceed():
            return
        newProject = NewProjectDlg(self)
        newProject.show()
        if newProject.exec_():
            if newProject.option1.isChecked():
                self.clearAll()
            else:
                self.statusBar().showMessage('Loading template wizard...', 250)
                QCoreApplication.processEvents()
                templateWiz = TemplateWizard(self)
                templateWiz.show()
                if templateWiz.exec_():
                    self.clearAll()
                    self.currentData = self.tempCurrentData
                    for item in self.currentData:
                        fileObj = File(item, self.currentData[item], self.openTabsForNewFiles.isChecked(), self)
                        self.currentFiles.append(fileObj)
            self.setWindowTitle("EasyMod XL")
            self.currentProject = None
                    
    def fileOpen(self):
        if not self.proceed(): return
        fname = self.currentProject if self.currentProject is not None else '.'
        openFile = QFileDialog.getOpenFileName(self, "Open Project", fname, "EasyMod Project (*.emp)")
        if openFile:
            projectFile = open(openFile, 'rb')
            self.currentData = pickle.load(projectFile)
            projectFile.close()
            self.currentProject = openFile
            if self.currentProject not in self.recentFileList:
                self.recentFileList.append(self.currentProject)
            self.toggleSaveOff()
            self.toggleSaveAllOff()
            self.clearAll()
            for item in self.currentData:
                fileObj = File(item, self.currentData[item], self.openTabsForNewFiles.isChecked(), self)
                self.currentFiles.append(fileObj)
            self.setWindowTitle("EasyMod XL - " + os.path.split(str(self.currentProject))[1])

    def fileSave_(self):
        if self.currentProject is None:
            self.fileSaveAs()
        else:
            name = self.tabbedWindow.currentWidget().ID
            data = unicode(self.tabbedWindow.currentWidget().textBox.toPlainText())
            self.tabbedWindow.currentWidget().parent.contents = data
            self.currentData[name] = data
            outputBuffer = open(self.currentProject, 'wb')
            pickle.dump(self.currentData, outputBuffer)
            outputBuffer.close()
            self.tabbedWindow.currentWidget().textBox.document().setModified(False)
            self.unsavedTabs.remove(self.tabbedWindow.currentWidget())
            if len(self.unsavedTabs) == 0:
                self.unsavedChanges = False
            self.toggleSaveOff()
    def fileSaveAll_(self):
        if self.currentProject is None:
            self.fileSaveAs()
        else:
            for index in range(self.tabbedWindow.count()):
                name = self.tabbedWindow.widget(index).ID
                data = unicode(self.tabbedWindow.widget(index).textBox.toPlainText())
                self.tabbedWindow.widget(index).parent.contents = data
                self.tabbedWindow.widget(index).textBox.document().setModified(False)
                self.currentData[name] = data
            outputBuffer = open(self.currentProject, 'wb')
            pickle.dump(self.currentData, outputBuffer)
            outputBuffer.close()
            self.toggleSaveOff()
            self.toggleSaveAllOff()
            self.unsavedTabs = [ ]
            self.unsavedChanges = False

    def fileSaveAs(self):
        fname = self.currentProject if self.currentProject is not None else "."
        saveFile = QFileDialog.getSaveFileName(self, "Save Project",
                   fname, "EasyMod Project (*.emp)")
        if not saveFile: return
        for index in range(self.tabbedWindow.count()):
            name = self.tabbedWindow.widget(index).ID
            data = unicode(self.tabbedWindow.widget(index).textBox.toPlainText())
            self.tabbedWindow.widget(index).parent.contents = data
            self.tabbedWindow.widget(index).textBox.document().setModified(False)
            self.currentData[name] = data
        
        projectFile = open(saveFile, 'wb')
        pickle.dump(self.currentData, projectFile)
        projectFile.close()
        self.currentProject = str(saveFile)
        self.statusBar().showMessage("%s saved." % self.currentProject, 5000)
        self.setWindowTitle('EasyMod XL - %s' % os.path.split(self.currentProject)[1])
        if self.currentProject not in self.recentFileList:
            self.recentFileList.append(self.currentProject)
        self.toggleSaveAllOff()
        self.unsavedChanges = False
        self.unsavedTabs = [ ]
        self.toggleSaveOff()
              
    def helpHelp(self):
        msg = QMessageBox.information(self, "Not Available", "Not available in Beta release", QMessageBox.Ok)

    def helpAbout(self):
        QMessageBox.about(self, "About EasyModXL",
            '''<b>EasyMod XL Beta</b><br/>
            EasyMod XL is a modding tool designed to make modding Cities XL
            easy and fun. It was written and is maintained by Hyperwolf, founder
            of XL Nation http://xlnation.net''')

    def itemSelectedListener(self):
        itemSelected = self.fileList.currentItem().parent
        tabFound = False
        for index in range(self.tabbedWindow.count()):
            if self.tabbedWindow.widget(index).parent == itemSelected:
                tabFound = True
                self.tabbedWindow.setCurrentIndex(index)
                break
        if not tabFound:
            if itemSelected.isEditable:
                itemSelected.addToTabs()

    def loadFile(self, openFile):
        try:
            inputBuffer = open(openFile, 'rb')
            self.currentData = pickle.load(inputBuffer)
            inputBuffer.close()
        except:
            return
        self.currentProject = openFile
        if self.currentProject not in self.recentFileList:
            self.recentFileList.append(self.currentProject)
        self.toggleSaveOff()
        self.toggleSaveAllOff()
        self.clearAll()
        for item, contents in self.currentData.items():
            fileObj = File(item, contents, self.openTabsForNewFiles.isChecked(), self)
            self.currentFiles.append(fileObj)
        self.setWindowTitle("EasyMod XL - " + os.path.split(str(self.currentProject))[1])

    def loadInitialFile(self):
        fname = self.config['currentProject']
        if fname and QFile.exists(fname):
            self.loadFile(fname)

    def makeAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False,signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/img/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action     
        
    def proceed(self):
        if self.unsavedChanges:
            reply = QMessageBox.question(self, "Unsaved Changes", "Save changes? ",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if   reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                self.fileSave_()
            elif reply == QMessageBox.No:
                return True
        return True
    
    def promptForNewFileName(self, oldName):
        newFileName = PromptForNewFileName(oldName, self)
        if newFileName.exec_():
            fileName = newFileName.newNameBox.text()
        else:
            fileName = None
        return fileName
    
    def settPreferences(self):
        msg = QMessageBox.information(self, "Not Available", "Not available in Beta release", QMessageBox.Ok)
        
    def setupFileListContextMenu(self):
        self.fileListMenu = QMenu()
        fileListCloneFile = self.makeAction("&Clone", self.fileListCloneFile, None, "editCopy", "Clone selected file")
        fileListRenameFile = self.makeAction("&Rename", self.fileListRenameFile, None, None, "Rename selected file")        
        fileListAddFile = self.makeAction("&Add File", self.fileListAddFile, None, "add", "Add new file")
        fileListCopyPath = self.makeAction("&Copy path", self.fileListCopyPath, None, "editCopy", "Copy selected file's path to clipboard")
        fileListDeleteFile = self.makeAction("&Delete", self.fileListDeleteFile, None, None, "Delete selected file")
        fileListDeleteAll = self.makeAction("D&elete all", self.fileListDeleteAll, None, "delete", "Delete all files")
        fileListRemoveTab = self.makeAction("Cl&ose tab", self.fileListRemoveTab, None,None, "Close tab that contains this file")
        fileListRemoveAllTabs = self.makeAction("Clo&se all tabs", self.fileListRemoveAllTabs,None,None, "Close all tabs")
        separator1 = QAction(self); separator1.setSeparator(True);
        separator2 = QAction(self); separator2.setSeparator(True);
        
        self.fileListActions = (fileListAddFile, fileListRenameFile, fileListCloneFile, separator1,
                                fileListDeleteFile, fileListDeleteAll, separator2, fileListRemoveTab,
                                fileListRemoveAllTabs)
        
    def setupFileListHeader(self):
        addButton = QPushButton()
        addButton.setToolTip("Add File")
        addButton.setStatusTip("Add File")
        addButton.setIcon(QIcon(":/img/add.png"))
        addButton.setFixedSize(25, 25)
        addButton.clicked.connect(self.fileListAddFile)

        sortButton = QPushButton()
        sortButton.setToolTip("Sort List")
        sortButton.setStatusTip("Sort List")
        sortButton.setIcon(QIcon(":/img/sort.png"))
        sortButton.setFixedSize(25,25)
        sortButton.clicked.connect(self.fileListSortFiles)
        
        clearAllButton = QPushButton()
        clearAllButton.setToolTip("Clear file list")
        clearAllButton.setStatusTip("Clear file list")
        clearAllButton.setIcon(QIcon(":/img/delete.png"))
        clearAllButton.setFixedSize(25, 25)
        clearAllButton.clicked.connect(self.fileListDeleteAll)

        closeTabsButton = QPushButton()
        closeTabsButton.setToolTip("Close all tabs")
        closeTabsButton.setStatusTip("Close all tabs")
        closeTabsButton.setIcon(QIcon(":/img/closeAllTabs.png"))
        closeTabsButton.setFixedSize(25, 25)
        closeTabsButton.clicked.connect(self.fileListRemoveAllTabs)

        self.gif = QMovie()
        self.gif.setFileName(':/img/progress.gif')
        self.gifHolder = QLabel()
        self.gifHolder.setMovie(self.gif)
        self.gifHolder.setAlignment(Qt.AlignRight)
        self.gifHolder.setVisible(False)
        
        self.fileListHeader = QHBoxLayout()
        self.fileListHeader.addWidget(addButton)
        self.fileListHeader.addWidget(sortButton)
        self.fileListHeader.addWidget(clearAllButton)
        self.fileListHeader.addWidget(closeTabsButton)
        self.fileListHeader.setAlignment(Qt.AlignLeft)
        self.fileListHeader.addWidget(self.gifHolder)
        
    def setupMenuActions(self):
        # Create Actions for the menubar
        fileNew          = self.makeAction("&New Project", self.fileNew, QKeySequence.New, "fileNew", "Create a new project")
        fileOpen         = self.makeAction("&Open Project", self.fileOpen, QKeySequence.Open, "fileOpen", "Open an existing project")
        self.fileSave    = self.makeAction("&Save Current", self.fileSave_, QKeySequence.Save, "fileSave", "Save the current file")
        self.fileSaveAll = self.makeAction("&Save All", self.fileSaveAll_, "Ctrl+Shift+A", "fileSaveAll", "Save all files")
        self.fileSave.setEnabled(False)
        self.fileSaveAll.setEnabled(False)
        fileSaveAs       = self.makeAction("Save Project &As", self.fileSaveAs, "Ctrl+Shift+s", "fileSaveAs", "Save the current project as...")       
        fileExport       = self.makeAction("&Export to folder", self.fileExport, "Ctrl+D", "fileExport", "Export project into a data folder")
        fileConvert      = self.makeAction("&Convert to patch", self.fileConvert, "Ctrl+M", "fileConvert", "Convert current files to a patch file")
        fileQuit         = self.makeAction("&Quit", self.fileQuit, "Ctrl+Q", "fileQuit", "Quit EasyMod")

        self.editUndo  = self.makeAction("&Undo", self.editUndo_, QKeySequence.Undo, "editUndo", "Undo previous action")
        self.editRedo  = self.makeAction("&Redo", self.editRedo_, QKeySequence.Redo, "editRedo", "Redo previous undo")
        editFind  = self.makeAction("&Find/Replace", self.editFindReplace, QKeySequence.Find, "editFind", "Find/Replace Dialog")
        editCopy  = self.makeAction("&Copy", self.editCopy, QKeySequence.Copy, "editCopy", "Copy to clipboard")
        editCut   = self.makeAction("Cu&t", self.editCut, QKeySequence.Cut, "editCut", "Cut to clipboard")
        editPaste = self.makeAction("&Paste", self.editPaste, QKeySequence.Paste, "editPaste", "Paste clipboard contents")
        editCloseBracket = self.makeAction("Cl&ose bracket", self.autoComplete, "Ctrl+J", None, "Close bracket")
        
        toolsSyntaxDebugger   = self.makeAction("&Debug", self.toolsSyntaxDeb, "Ctrl+H", "debug", "Attempt to debug XML syntax")
        toolsSimplePackUnpack = self.makeAction("&Simple Pack/Unpack", self.toolsSPUP, "Ctrl+Shift+M", "toolsSPUP", "Simple Pack/Unpack Interface")
        toolsBuildTemplate  = self.makeAction("&Build template", self.toolsBuildTemplate, None, None, "Build a template from a base file")
        
        settPreferences   = self.makeAction("&Preferences", self.settPreferences, "Ctrl+I", "settPreferences", "Interface Preferences")
        
        helpHelp  = self.makeAction("&Help", self.helpHelp, "Ctrl+H", "helpHelp", "Browse Help topics")
        helpAbout = self.makeAction("&About", self.helpAbout, None, "EasyModXL", "About EasyMod")



        # Create menus
        self.fileMenu  = self.menuBar().addMenu('&File')
        self.editMenu  = self.menuBar().addMenu('&Edit')
        self.toolsMenu = self.menuBar().addMenu('&Tools')
        self.settMenu  = self.menuBar().addMenu('&Settings')
        self.helpMenu  = self.menuBar().addMenu('&Help')

        # Add actions to main menus
        self.addActions_(self.fileMenu, (fileNew, fileOpen))
        self.recentFiles = self.fileMenu.addMenu('&Recent files')
        self.addActions_(self.fileMenu, (None, self.fileSave, self.fileSaveAll, fileSaveAs, None, fileExport, fileConvert, None, fileQuit))
        self.connect(self.recentFiles, SIGNAL("aboutToShow()"), self.updateRecentFiles) 
        self.addActions_(self.editMenu, (self.editUndo, self.editRedo, None, editCopy, editCut, editPaste,None, editFind, None, editCloseBracket))
        self.addActions_(self.toolsMenu, (toolsSyntaxDebugger, None, toolsSimplePackUnpack, toolsBuildTemplate))
        self.addActions_(self.settMenu, (settPreferences,))
        self.addActions_(self.helpMenu, (helpHelp, None, helpAbout))
        

        
        # Create Toolbars
        fileToolbar = self.addToolBar('File')
        fileToolbar.setObjectName('fileToolbar')
        editToolbar = self.addToolBar('Edit')
        editToolbar.setObjectName('editToolbar')

        # Add actions to toolbars
        self.addActions_(fileToolbar, (fileNew, fileOpen, self.fileSave, self.fileSaveAll, fileExport, fileConvert))
        self.addActions_(editToolbar, (editCopy, editCut, editPaste))
        
    def showLoadingGif(self):
        self.statusBar().showMessage("Processing data", 1000)
        self.gifHolder.setVisible(True)
        self.gif.start()

    def tabChanged(self):
        if self.tabbedWindow.count() > 0:
            self.fileSave.setEnabled(self.tabbedWindow.currentWidget().textBox.document().isModified())
            self.editUndo.setEnabled(self.tabbedWindow.currentWidget().textBox.document().isUndoAvailable())
            self.editRedo.setEnabled(self.tabbedWindow.currentWidget().textBox.document().isRedoAvailable())
        else:
            self.fileSave.setEnabled(False)
            self.editUndo.setEnabled(False)
            self.editRedo.setEnabled(False)
    def toggleSaveOff(self):
        self.fileSave.setEnabled(False)
    def toggleSaveAllOff(self):
        self.fileSaveAll.setEnabled(False)
    def toggleSaveAllOn(self):
        self.fileSave.setEnabled(False)
    def toggleSaveOn(self, sender=None):
        self.toggleSaveAllOn()
        if sender is not None and sender not in self.unsavedTabs:
            self.unsavedTabs.append(sender)
        self.unsavedChanges = True
        self.fileSave.setEnabled(True)
    def toolsSyntaxDeb(self):
        dialog = SyntaxDebugger(self)
        dialog.show()
    def toolsSPUP(self):
        spupWindow = SimplePackUnpack(self)
        spupWindow.show()
    def toolsBuildTemplate(self):
        template = TemplateBuilder(self)
        if template.exec_():
            self.dataReceivedFromWorkerThread(template.dataDict)

    
    def updateFileListContextMenu(self, position):
        if self.fileList.selectedItems():
            self.fileListActions[1].setEnabled(True) # rename
            self.fileListActions[2].setEnabled(True) # clone                                     
            self.fileListActions[4].setEnabled(True) # delete
            # remove tab
            self.fileListActions[7].setEnabled(self.fileList.currentItem().parent.hasTabOpen)
        else:
            self.fileListActions[1].setEnabled(False)
            self.fileListActions[2].setEnabled(False)
            self.fileListActions[4].setEnabled(False)
            self.fileListActions[7].setEnabled(False)
        if self.fileList.count() == 0:
            self.fileListActions[5].setEnabled(False) # delete all
        else:
            self.fileListActions[5].setEnabled(True)
        if self.tabbedWindow.count() == 0:
            self.fileListActions[-1].setEnabled(False)
        else:
            self.fileListActions[-1].setEnabled(True)
        self.addActions_(self.fileListMenu, self.fileListActions)
        self.fileListMenu.exec_(self.fileList.mapToGlobal(position))

    def updateRecentFiles(self):
        self.recentFiles.clear()
        if self.recentFileList:
            for i, fname in enumerate(self.recentFileList):
                action = RecentFileAction('%d %s' % (i+1, fname), self)
                action.actionClicked.connect(self.loadFile)
                self.recentFiles.addAction(action)

if __name__ == '__main__':
    configuration = None
    customPath = os.environ.get("LOCALAPPDATA") + "\\EasyModXL"
    if not os.path.exists(customPath):
        os.mkdir(customPath)
    fname = customPath + '\\' + "settings.cfg"
    if os.path.exists(fname):
        openSettingsFile = open(fname, 'rb')
        configuration = pickle.load(openSettingsFile)
        openSettingsFile.close()

    EasyModXLApp = QApplication(sys.argv)
    EasyModXLApp.setOrganizationName("EasyMod XL")
    EasyModXLApp.setOrganizationDomain('http://xlnation.net')
    EasyModXLApp.setApplicationName("EasyMod XL")
    MainInterface = EasyModXL(configuration)
    MainInterface.show()
    EasyModXLApp.exec_()


        
        
        
