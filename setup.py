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

from distutils.core import setup
import py2exe
import os
import re
import sys
import pickle
import sip
sip.setapi('QVariant', 2)
import resources
from   templateWizard    import *
from   PyQt4.QtCore      import *
from   PyQt4.QtGui       import *
from   packunpack2       import PatchFile, EMXLProject, DataFolder
from   recentFileAction  import RecentFileAction
from   fileList          import FileList
from   fileObject        import File, TabRepresentative
from   xmlSyntax         import SyntaxDebugger, SyntaxHighlighter
from   fileListAddFile   import FileListAddFile
from   fileListCloneFile import FileListCloneFile
from   newFileName       import PromptForNewFileName
from   editFindReplace   import FindReplaceDialog
from   newProjectDlg     import NewProjectDlg
from   simplePackUnpack  import SimplePackUnpack
from   workerThread      import WorkerThread
from   templateBuilder   import TemplateBuilder

setup(windows=[{"script" : "EasyModXL.pyw",
                "icon_resources": [(1, "emxl.ico")]}])
