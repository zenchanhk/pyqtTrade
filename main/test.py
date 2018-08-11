#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QFrame,
        QLabel, QMainWindow, QMenu, QMessageBox, QSizePolicy, QVBoxLayout,
        QWidget, QLineEdit, QHBoxLayout, QWidgetAction, QPushButton)
import qtawesome as qta

STYLE = '''
SymbolSearch[state='false'] {
    background: lightgray;
}
'''

class MyLineEdit(QLineEdit):
    focusIn = pyqtSignal()
    focusOut = pyqtSignal()
    enterPressed = pyqtSignal(str)

    def __init__(self, parent):
       super().__init__(parent)

    def focusInEvent(self, event):
        self.focusIn.emit()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.focusOut.emit()
        super().focusOutEvent(event)

    def keyPressEvent(self, e):
        if e.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.enterPressed.emit(self.text())
        super().keyPressEvent(e)

class MyLabel(QLabel):
    clicked=pyqtSignal()
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, ev):
        self.clicked.emit()

class Item:
    _id = ''
    _delegate = None

    def __init__(self, id=None, delegate=None, parent=None):
        if id != None:
            self._id = id
            self._delegate = delegate

    @QtCore.pyqtProperty(str)
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._id = value

    @QtCore.pyqtProperty(QWidget)
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, value):
        if value != self._delegate:
            self._delegate = value

class Section:
    _id = ''
    _delegate = None

    def __init__(self, id=None, delegate=None, item_id):
        if id != None:
            self._id = id
            self._delegate = delegate
    
    @QtCore.pyqtProperty(str)
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._id = value

    @QtCore.pyqtProperty(QWidget)
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, value):
        if value != self._delegate:
            self._delegate = value

class Group:
    _id = ''
    _delegate = None

    def __init__(self, id=None, delegate=None, parent=None):
        if id != None:
            self._id = id
            if delegate == None:
                self._delegate = QMenu(parent)
            else:
                self._delegate = delegate

    @QtCore.pyqtProperty(str)
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._id = value

    @QtCore.pyqtProperty(QWidget)
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, value):
        if value != self._delegate:
            self._delegate = value

class GroupItem(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.l1 = QWidget(self)
        self.l1.setFixedHeight(2)
        self.l1.setFixedWidth(5)
        self.l1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.l1.setStyleSheet("background-color: #c0c0c0;")
        self.l2 = QWidget(self)
        self.l2.setFixedHeight(2)
        self.l2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.l2.setStyleSheet("background-color: #c0c0c0;")
        self.label = QLabel(self)
        self.label.setText(text)
        lay.addWidget(self.l1)
        lay.addWidget(self.label)
        lay.addWidget(self.l2)

class SymbolSearch(QWidget):
    enterPressed = pyqtSignal(str)
    selected = pyqtSignal(object)

    _placeholder = 'placeholder'
    _loading = False
    _data = []
    _setting = [Section, Group]

    def __init__(self, parent):
        super().__init__(parent)
        #self.setFocusPolicy(Qt.StrongFocus)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.input = MyLineEdit(self)
        self.input.setPlaceholderText(self.placeholder)
        self.input.focusIn.connect(self.focusInHandler)
        self.input.focusOut.connect(self.focusOutHandler)
        self.input.enterPressed.connect(self.keyPressHandler)
        lay.addWidget(self.input)

        self.label = MyLabel(self)
        self.label.setText(self.placeholder)
        self.label.clicked.connect(self.focusInHandler)
        self.label.setGeometry(self.input.geometry().x(), self.input.geometry().y(),
            self.input.geometry().width(), self.input.geometry().height())
        
        s = self.styleSheet()
        #calculate the space of top and bottom
        self.winHeight = 0 
        self.topHeight = 0
        self.bottomHeight = 10
        #print(s)
        self.setStyleSheet('QLabel{background: red}')

    @QtCore.pyqtProperty(str)
    def placeholder(self):
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        if value != self._placeholder:
            self.input.setPlaceholderText(value)
            self.label.setText(value)
            self._placeholder = value

    @QtCore.pyqtProperty(bool)
    def loading(self):
        return self._loading

    @loading.setter
    def loading(self, value):
        if value != self._loading:
            self._loading = value

    @QtCore.pyqtProperty(list)
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if value != self._data:
            self._data = value
            for item in value:
                print(item)

    def moveEvent(self, event):
        for w in QApplication.topLevelWidgets():
            if isinstance(w, QMainWindow):
                wg = w.geometry()
                self.winHeight = wg.height()
                g = self.geometry()
                self.topHeight = g.y()
                self.bottomHeight = self.winHeight - g.y() - g.height() 
                break
        super().moveEvent(event)

    def resizeEvent(self, event): 
        self.label.resize(event.size().width(), event.size().height())
        super().resizeEvent(event)

    def keyPressHandler(self, e):
        self.enterPressed.emit(e)
        self._showDropDown()

    def focusInHandler(self):
        self.label.hide()
        self.input.setFocus()

    def focusOutHandler(self):
        if not self.menu.isVisible:
            self.label.show()

    def _createActions(self):
        test = QWidgetAction(self.menu)
        l = QLabel(self)
        l.setText('test')
        test.setDefaultWidget(ItemAction('Group'))
        self.menu.addAction(test)
        settingsAction = QAction('settings', self.menu)
        self.menu.addAction(settingsAction)

    def _createMenu(self):
        self.menu = QMenu()
    
    def _showDropDown(self):
        self._createMenu()
        self._createActions()
        self.menu.popup(QPoint(0, 0))
        gm = self.menu.geometry()
        gs = self.mapToGlobal(self.pos()) - self.pos()
        if self.bottomHeight < gm.height() and self.topHeight > self.bottomHeight:
            y = gs.y() - gm.height()
        else:
            y = gs.y() + self.geometry().height()
        x = gs.x()
        
        self.menu.move(QPoint(x, y))
        self.geometry()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        widget = QWidget()
        self.setCentralWidget(widget)

        topFiller = QWidget()
        topFiller.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.infoLabel = QLabel(
                "<i>Choose a menu option, or right-click to invoke a context menu</i>",
                alignment=Qt.AlignCenter)
        self.infoLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        bottomFiller = QWidget()
        bottomFiller.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(5, 5, 5, 5)
        vbox.addWidget(topFiller)
        vbox.addWidget(self.infoLabel)
        vbox.addWidget(bottomFiller)

        ss = SymbolSearch(self)
        i = MyLineEdit(self)
        i.placeholderText = 'test'
        vbox.addWidget(ss)
        vbox.addWidget(i)
        b = QPushButton(self)
        b.setText("Test")
        b.clicked.connect(self.showmenu)
        vbox.addWidget(b)
        widget.setLayout(vbox)

        self.createActions()
        self.createMenus()

        message = "A context menu is available by right-clicking"
        self.statusBar().showMessage(message)

        self.setWindowTitle("Menus")
        self.setMinimumSize(160,160)
        self.resize(480,320)
        self.setStyleSheet('QMenu::item:disabled{background-color:red; color:black}')
        #self.setStyleSheet('QMenu::item:enabled{margin-left: 10px}')

    def showmenu(self):
        menu = QMenu(self)
        menu.addAction(self.cutAct)
        menu.addAction(self.copyAct)
        menu.addAction(self.pasteAct)
        self.pasteAct.setEnabled(False)
        menu.exec_()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction(self.cutAct)
        menu.addAction(self.copyAct)
        menu.addAction(self.pasteAct)
        self.pasteAct.setEnabled(False)
        menu.exec_(event.globalPos())

    def newFile(self):
        self.infoLabel.setText("Invoked <b>File|New</b>")

    def open(self):
        self.infoLabel.setText("Invoked <b>File|Open</b>")
        	
    def save(self):
        self.infoLabel.setText("Invoked <b>File|Save</b>")

    def print_(self):
        self.infoLabel.setText("Invoked <b>File|Print</b>")

    def undo(self):
        self.infoLabel.setText("Invoked <b>Edit|Undo</b>")

    def redo(self):
        self.infoLabel.setText("Invoked <b>Edit|Redo</b>")

    def cut(self):
        self.infoLabel.setText("Invoked <b>Edit|Cut</b>")

    def copy(self):
        self.infoLabel.setText("Invoked <b>Edit|Copy</b>")

    def paste(self):
        self.infoLabel.setText("Invoked <b>Edit|Paste</b>")

    def bold(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Bold</b>")

    def italic(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Italic</b>")

    def leftAlign(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Left Align</b>")

    def rightAlign(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Right Align</b>")

    def justify(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Justify</b>")

    def center(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Center</b>")

    def setLineSpacing(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Set Line Spacing</b>")

    def setParagraphSpacing(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Set Paragraph Spacing</b>")

    def about(self):
        self.infoLabel.setText("Invoked <b>Help|About</b>")
        QMessageBox.about(self, "About Menu",
                "The <b>Menu</b> example shows how to create menu-bar menus "
                "and context menus.")

    def aboutQt(self):
        self.infoLabel.setText("Invoked <b>Help|About Qt</b>")

    def createActions(self):
        self.newAct = QAction("&New", self, shortcut=QKeySequence.New,
                statusTip="Create a new file", triggered=self.newFile)

        self.openAct = QAction("&Open...", self, shortcut=QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.open)

        self.saveAct = QAction("&Save", self, shortcut=QKeySequence.Save,
                statusTip="Save the document to disk", triggered=self.save)

        self.printAct = QAction("&Print...", self, shortcut=QKeySequence.Print,
                statusTip="Print the document", triggered=self.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)

        self.undoAct = QAction("&Undo", self, shortcut=QKeySequence.Undo,
                statusTip="Undo the last operation", triggered=self.undo)

        self.redoAct = QAction("&Redo", self, shortcut=QKeySequence.Redo,
                statusTip="Redo the last operation", triggered=self.redo)

        self.cutAct = QAction("Cu&t", self, shortcut=QKeySequence.Cut,
                statusTip="Cut the current selection's contents to the clipboard",
                triggered=self.cut)

        self.copyAct = QAction("&Copy", self, shortcut=QKeySequence.Copy,
                statusTip="Copy the current selection's contents to the clipboard",
                triggered=self.copy)

        self.pasteAct = QAction("— Paste —————", self, shortcut=QKeySequence.Paste,
                statusTip="Paste the clipboard's contents into the current selection",
                triggered=self.paste)

        self.boldAct = QAction("&Bold", self, checkable=True,
                shortcut="Ctrl+B", statusTip="Make the text bold",
                triggered=self.bold)

        boldFont = self.boldAct.font()
        boldFont.setBold(True)
        self.boldAct.setFont(boldFont)

        self.italicAct = QAction("&Italic", self, checkable=True,
                shortcut="Ctrl+I", statusTip="Make the text italic",
                triggered=self.italic)

        italicFont = self.italicAct.font()
        italicFont.setItalic(True)
        self.italicAct.setFont(italicFont)

        self.setLineSpacingAct = QAction("Set &Line Spacing...", self,
                statusTip="Change the gap between the lines of a paragraph",
                triggered=self.setLineSpacing)

        self.setParagraphSpacingAct = QAction("Set &Paragraph Spacing...",
                self, statusTip="Change the gap between paragraphs",
                triggered=self.setParagraphSpacing)

        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=self.aboutQt)
        self.aboutQtAct.triggered.connect(QApplication.instance().aboutQt)

        self.leftAlignAct = QAction("&Left Align", self, checkable=True,
                shortcut="Ctrl+L", statusTip="Left align the selected text",
                triggered=self.leftAlign)

        self.rightAlignAct = QAction("&Right Align", self, checkable=True,
                shortcut="Ctrl+R", statusTip="Right align the selected text",
                triggered=self.rightAlign)

        self.justifyAct = QAction("&Justify", self, checkable=True,
                shortcut="Ctrl+J", statusTip="Justify the selected text",
                triggered=self.justify)

        self.centerAct = QAction("&Center", self, checkable=True,
                shortcut="Ctrl+C", statusTip="Center the selected text",
                triggered=self.center)

        self.alignmentGroup = QActionGroup(self)
        self.alignmentGroup.addAction(self.leftAlignAct)
        self.alignmentGroup.addAction(self.rightAlignAct)
        self.alignmentGroup.addAction(self.justifyAct)
        self.alignmentGroup.addAction(self.centerAct)
        self.leftAlignAct.setChecked(True)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)
        self.editMenu.addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.formatMenu = self.editMenu.addMenu("&Format")
        self.formatMenu.addAction(self.boldAct)
        self.formatMenu.addAction(self.italicAct)
        self.formatMenu.addSeparator().setText("Alignment")
        self.formatMenu.addAction(self.leftAlignAct)
        self.formatMenu.addAction(self.rightAlignAct)
        self.formatMenu.addAction(self.justifyAct)
        self.formatMenu.addAction(self.centerAct)
        self.formatMenu.addSeparator()
        self.formatMenu.addAction(self.setLineSpacingAct)
        self.formatMenu.addAction(self.setParagraphSpacingAct)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())