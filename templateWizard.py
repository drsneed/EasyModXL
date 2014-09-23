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

import sip
sip.setapi('QVariant', 2)
from operator import itemgetter
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import pickle
import zlib
import re

class TemplateWizard(QWizard):
    def __init__(self, parent=None):
        super(TemplateWizard, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle("Template Wizard")
        Templates = open('rsc/alltemplates.emtpl', 'rb')
        self.templates = pickle.load(Templates)
        Templates.close()
        self.enLoc = open('rsc/buildingnames.en', 'rb').read()
        self.esLoc = open('rsc/buildingnames.es', 'rb').read()
        self.deLoc = open('rsc/buildingnames.de', 'rb').read()
        self.frLoc = open('rsc/buildingnames.fr', 'rb').read()
        self.itLoc = open('rsc/buildingnames.it', 'rb').read()
        self.enLoc = self.enLoc.replace('\x00', '').split('\n')
        self.esLoc = self.esLoc.replace('\x00', '').split('\n')
        self.deLoc = self.deLoc.replace('\x00', '').split('\n')
        self.frLoc = self.frLoc.replace('\x00', '').split('\n')
        self.itLoc = self.itLoc.replace('\x00', '').split('\n')
        self.templates = sorted(self.templates, key=itemgetter(1))
        self.customThumbData = {}
        self.customModelData = {}
        self.selectedTag = None
        self.thumbFile = None
        self.sgbinFile = None
        self.classFile = None
        self.layoutFile = None
        
        self.addPage(IntroPage(self))
        self.addPage(ConfigPage(self))
        self.addPage(FinishedPage())
        
        
    def accept(self):
        self.chosenTemplate = self.templates[self.field('templateListSelection')]
        useDefaultLocs = self.field('useDefaultLocs')
        locFiles = {}
        if self.customModelData:
            sgbinFile = self.customModelData.keys()[0]
        else:
            sgbinFile = None
        if self.customThumbData:
            thumbFile = self.customThumbData.keys()[0]
        else:
            thumbFile = None
        for File in self.chosenTemplate[2]:
            if File.endswith('.class'):
                classContents = zlib.decompress(self.chosenTemplate[2][File])
                break
        if not classContents:
            print "something went wrong, class not found."
            return
        if not useDefaultLocs:
            nameKeyMatch = re.search('<NameKey>&(.*)</NameKey>', classContents)
            nameKey = nameKeyMatch.group(1)
            enLocData = self.getOriginalLoc(self.enLoc, nameKey)
            esLocData = self.getOriginalLoc(self.esLoc, nameKey)
            frLocData = self.getOriginalLoc(self.frLoc, nameKey)
            deLocData = self.getOriginalLoc(self.deLoc, nameKey)
            itLocData = self.getOriginalLoc(self.itLoc, nameKey)
            classContents = classContents.replace(nameKey, str(self.field('baseName')).upper())
            
        if self.selectedTag and self.field('useCustomTag'):
            classContents = re.sub('(<[tT][aA][gG]>.*</[tT][aA][gG]>)',
                                   lambda a: self.selectedTag, classContents)
        if sgbinFile:
            classContents = re.sub('(<Display>\s*<Model>)(.*)(</Model>)',
                               lambda a: a.group(1) + sgbinFile + a.group(3), classContents)
        if thumbFile:
            classContents = re.sub('(<Fundament>\s*<Use>\d</Use>\s*<Model>)(.*)(</Model>)',
                               lambda a: a.group(1) + thumbFile + a.group(3), classContents)
        classContents = re.sub('(<LayoutFile1>)(.*)(</LayoutFile1>)',
                               lambda a: a.group(1) + self.layoutFile + a.group(3), classContents)
        dataDict = {self.classFile:classContents}
        for item in self.chosenTemplate[2]:
            if item.endswith('.layout'):
                dataDict[self.layoutFile] = zlib.decompress(self.chosenTemplate[2][item])
            if not self.customModelData:
                if item.endswith('.sgbin'):
                    dataDict[item] = zlib.decompress(self.chosenTemplate[2][item])
            if not self.customThumbData:
                if item.endswith('.dds'):
                    dataDict[item] = zlib.decompress(self.chosenTemplate[2][item])
        if self.customModelData:
            dataDict[sgbinFile] = self.customModelData[sgbinFile]
        if self.customThumbData:
            key = self.customThumbData.keys()[0]
            dataDict[thumbFile] = self.customThumbData[thumbFile]
                
        if not useDefaultLocs:
            dataDict['data/localization/en/'+self.field('baseName')+'.en'] = enLocData
            dataDict['data/localization/es/'+self.field('baseName')+'.es'] = esLocData
            dataDict['data/localization/fr/'+self.field('baseName')+'.fr'] = frLocData
            dataDict['data/localization/de/'+self.field('baseName')+'.de'] = deLocData
            dataDict['data/localization/it/'+self.field('baseName')+'.it'] = itLocData
        self.parent.tempCurrentData = dataDict
        super(TemplateWizard, self).accept()
        
    def getOriginalLoc(self, locFile, nameKey):
        nameKey = '#FIELD_ID ' + nameKey
        locData = '#FILE_VERSION 3\n\n'
        for index, line in enumerate(locFile):
            if nameKey in line:
                locData += line.replace(nameKey, "#FIELD_ID " + str(self.field('baseName')).upper()) + \
                '\n' + locFile[index+1] + '\n\n'

        return locData
        
        
        
class IntroPage(QWizardPage):
    def __init__(self, parent = None):
        super(IntroPage, self).__init__(parent)
        self.setTitle("Introduction")
        introStatement = QLabel (
            "This wizard will generates templates to help get you"
            " started on a project. They are geared towards modders"
            " that have created a model and want to import it into"
            " the game."
        )
        introStatement.setWordWrap(True)
        templateList = QListWidget ( )
        templateList.setFont(QFont("Courier", 10))
        for template in parent.templates:
            templateList.addItem(template[0])
        layout = QVBoxLayout()
        layout.addWidget(introStatement)
        layout.addWidget(templateList)
        self.setLayout(layout)

        self.registerField('templateListSelection*', templateList)
 
class ConfigPage(QWizardPage):
    def __init__(self, parent=None):
        super(ConfigPage, self).__init__(parent)
        self.parent = parent
        self.foundThumb = None
        self.foundSgbin = None
        
        self.setTitle("Project Files Configuration")
        self.setSubTitle("Choose the files to include in this project."
                         "Additional files can be added later if needed."
                         )
        mainFilesGroup = QGroupBox("Core files:")
        baseNameLabel = QLabel("Edit base name:")
        self.baseNameEntry = QLineEdit()
        self.baseNameEntry.setMaxLength(150)
        classFileLabel = QLabel("Class file:")
        self.classFile = QLabel('default text')
        layoutFileLabel = QLabel("Layout file:")
        self.layoutFile = QLabel("default text")
        modelBrowse   = QPushButton("Sgbin File")
        self.sgbinFile = QLabel("default text")
        thumbBrowse   = QPushButton("Thumbnail File")
        self.thumbFile = QLabel("default text")

        #spacer = QFrame()
        #spacer.setMaximumWidth(400)
        #spacer.setMaximumWidth(3)
        #spacer.setFrameShape(QFrame.HLine)
        #spacer.setFrameShadow(QFrame.Sunken)
        
        mainFilesLayout = QGridLayout(mainFilesGroup)
        mainFilesLayout.addWidget(baseNameLabel, 0, 0)
        mainFilesLayout.addWidget(self.baseNameEntry, 0, 1)
        mainFilesLayout.addWidget(classFileLabel,1, 0)
        mainFilesLayout.addWidget(self.classFile, 1,1)
        mainFilesLayout.addWidget(layoutFileLabel,2,0)
        mainFilesLayout.addWidget(self.layoutFile,2,1)
        mainFilesLayout.addWidget(modelBrowse, 3,0)
        mainFilesLayout.addWidget(self.sgbinFile, 3, 1)
        mainFilesLayout.addWidget(thumbBrowse, 4, 0)
        mainFilesLayout.addWidget(self.thumbFile, 4, 1)
                         
        localizationGroup = QGroupBox("Localization Options")
        self.useDefaultLocs = QRadioButton("Use default building descriptions")
        self.useCustomLocs  = QRadioButton("Use custom  building descriptions")
        localizationLayout = QVBoxLayout(localizationGroup)
        localizationLayout.addWidget(self.useDefaultLocs)
        localizationLayout.addWidget(self.useCustomLocs)
        self.useDefaultLocs.setChecked(True)

        buildingMenuGroup = QGroupBox("Building Menu Location")

        self.useDefaultTag = QRadioButton("Use default tag for this template")
        self.useDefaultTag.setChecked(True)
        self.useCustomTag  = QRadioButton("Select an alternate tag")
        self.tagDropDown   = QComboBox()
        self.tagDropDown.setMaximumWidth(500)
        self.tagDropDown.setEnabled(False)
        Tags = open('rsc/tags.txt').read()
        Tags = Tags.split('\n')
        self.tags = []
        for tag in Tags:
            if 'deprecated' not in tag.lower():
                self.tags.append(tag)
                self.tagDropDown.addItem(tag)
        buildingMenuLay = QGridLayout(buildingMenuGroup)
        buildingMenuLay.addWidget(self.useDefaultTag, 0, 0)
        buildingMenuLay.addWidget(self.useCustomTag, 1, 0)
        buildingMenuLay.addWidget(self.tagDropDown, 2,0, 4, 0)
    
        # connections    
        self.baseNameEntry.textChanged.connect(self.changeBaseName)
        modelBrowse.clicked.connect(self.browseForModel)
        thumbBrowse.clicked.connect(self.browseForThumb)
        self.useCustomTag.toggled.connect(self.tagDropDown.setEnabled)
        self.tagDropDown.currentIndexChanged.connect(self.changeSelectedTag)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(mainFilesGroup)
        mainLayout.addWidget(localizationGroup)
        mainLayout.addWidget(buildingMenuGroup)
        self.setLayout(mainLayout)

        self.registerField('baseName', self.baseNameEntry)
        self.registerField('useDefaultLocs', self.useDefaultLocs)
        self.registerField('useCustomTag', self.useCustomTag)

    def changeSelectedTag(self):
        self.parent.selectedTag = str(self.tagDropDown.currentText())
    def getTagFromClass(self):
        current_template = self.parent.templates[self.field('templateListSelection')]
        for item in current_template[2]:
            if item.endswith('.class'):
                data = zlib.decompress(current_template[2][item])
                tag = re.search('(<[tT][aA][gG]>.*</[tT][aA][gG]>)', data)
                if tag:
                    return tag.group(1)
        return None

    def changeBaseName(self):
        old_base = self.parent.templates[self.field('templateListSelection')][1]
        new_base = self.baseNameEntry.text()
        for file_ in  self.parent.templates[self.field('templateListSelection')][2]:
            if str(file_).endswith(".class"):
                new_text = str(file_).replace(old_base, new_base)
                self.classFile.setText(new_text)
                self.parent.classFile = new_text
            if str(file_).endswith(".layout"):
                new_text = str(file_).replace(old_base, new_base)
                self.layoutFile.setText(new_text)
                self.parent.layoutFile = new_text
    def initializePage(self):
        self.baseNameEntry.setText(self.parent.templates[self.field('templateListSelection')][1])
        for file_ in  self.parent.templates[self.field('templateListSelection')][2]:
            if str(file_).endswith(".class"):
                self.classFile.setText(file_)
                self.parent.classFile = file_
            if str(file_).endswith(".layout"):
                self.layoutFile.setText(file_)
                self.parent.layoutFile = file_
            if str(file_).endswith(".sgbin"):
                self.sgbinFile.setText(file_)
                self.parent.sgbinFile = file_
            if str(file_).endswith(".dds"):
                self.thumbFile.setText(file_)
                self.parent.thumbFile = file_
        tag = self.getTagFromClass()
        if tag is not None:
            self.tagDropDown.insertItem(0, tag)
            self.tagDropDown.setCurrentIndex(0)
            self.parent.selectedTag = str(self.tagDropDown.currentText())

        

    def browseForModel(self):
       sgbin = QFileDialog.getOpenFileName(self, "Include Model", ".", "Sgbin File (*.sgbin)")
       if not sgbin: return
       sgbin = str(sgbin)
       fileContents = open(sgbin, 'rb').read()
       self.foundSgbin = 'data/gfx/building/' + os.path.split(sgbin)[1]
       self.sgbinFile.setText(self.foundSgbin)
       self.parent.customModelData = {self.foundSgbin:fileContents}
       
    def browseForThumb(self):
       thumb = QFileDialog.getOpenFileName(self, "Include Thumbnail", ".", "DDS File (*.dds)")
       if not thumb: return
       thumb = str(thumb)
       fileContents = open(thumb, 'rb').read()
       self.foundThumb = 'data/interface/ddstexture/buildings/' + os.path.split(thumb)[1]
       self.thumbFile.setText(self.foundThumb)
       self.parent.customThumbData = {self.foundThumb:fileContents}

class FinishedPage(QWizardPage):
    def __init__(self, parent=None):
        super(FinishedPage, self).__init__(parent)
        self.setTitle("Conclusion")
        self.label = QLabel()
        self.label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def initializePage(self):
        finishText = self.wizard().buttonText(QWizard.FinishButton)
        finishText = finishText.replace('&','')
        self.label.setText('Click %s to generate the project files' % finishText)
