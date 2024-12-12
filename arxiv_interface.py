from qfluentwidgets import (ScrollArea, BodyLabel, LineEdit, PushButton,
                            TextBrowser, CheckBox, FlowLayout)
from PySide6 import QtCore
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QFileDialog)
import re
from asyncslot import asyncSlot
from pathlib import Path

from fetch import fetch_html, abs_html, get_abs_url


class ArxivInterface(ScrollArea):
    # tags = ['abcde', 'askjlafjkd', 'askdjla', 'asdada', 'jhon']

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ArxivInterface")
        self.setWidgetResizable(True)

        self.tagWidgets = []

        self.initWidgets()
        self.initLayout()

    def initWidgets(self):
        self.mainWidget = QWidget()
        self.setWidget(self.mainWidget)

        self.urlLabel = BodyLabel("URL:")
        self.urlLineEdit = LineEdit()
        self.urlSearchButton = PushButton("Search")

        self.tagLabel = BodyLabel("Tags:")
        self.tagsearchLineEdit = LineEdit()
        self.tagsearchButton = PushButton("Search")
        self.tagAllSelectButton = PushButton("Select All")
        self.downloadButton = PushButton("Download")
        self.downloadButton.setEnabled(False)

        self.detailLabel = BodyLabel("Details:")
        self.detailTextEdit = TextBrowser()

        self.urlSearchButton.clicked.connect(asyncSlot(self.onclickedSearchButton))
        self.tagAllSelectButton.clicked.connect(self.onclickedTagAllSelectButton)
        self.tagsearchButton.clicked.connect(self.onclickedTagsearchButton)
        self.downloadButton.clicked.connect(asyncSlot(self.onclickedDownloadButton))

    def initLayout(self):
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)

        self.urlHLayout = QHBoxLayout()
        self.urlHLayout.addWidget(self.urlLabel)
        self.urlHLayout.addWidget(self.urlLineEdit)
        self.urlHLayout.addWidget(self.urlSearchButton)

        self.tagVLayout = QVBoxLayout()
        self.tagVHLayout = QHBoxLayout()
        self.tagFLayout = FlowLayout()
        self.tagVHLayout.addWidget(self.tagLabel)
        self.tagVHLayout.addWidget(self.tagsearchLineEdit)
        self.tagVHLayout.addWidget(self.tagsearchButton)
        self.tagVHLayout.addWidget(self.tagAllSelectButton)
        self.tagVLayout.addLayout(self.tagVHLayout)
        self.tagVLayout.addLayout(self.tagFLayout)

        self.detailVLayout = QVBoxLayout()
        self.detailVLayout.addWidget(self.detailLabel)
        self.detailVLayout.addWidget(self.detailTextEdit)

        self.mainLayout.addLayout(self.urlHLayout)
        self.mainLayout.addLayout(self.tagVLayout)
        self.mainLayout.addStretch(1)
        self.mainLayout.addWidget(self.downloadButton)
        self.mainLayout.addLayout(self.detailVLayout)

    async def onclickedSearchButton(self):
        self.downloadButton.setEnabled(False)
        self.urlSearchButton.setEnabled(False)
        url = self.urlLineEdit.text()
        self.datas = []
        tags = []
        if "arxiv.org" in url:
            abs_urls = await get_abs_url(url)
            total = len(abs_urls)
            for idx, abs_url in enumerate(abs_urls):
                self.detailTextEdit.append(f"Processing {abs_url} ({(idx + 1) / total * 100:.2f}%)")
                data = await abs_html(abs_url)
                self.datas.append(data)
        for data in self.datas:
            if not data['subjects'] in tags:
                tags.append(data['subjects'])
        for tag in tags:
            checkBox = CheckBox(tag)
            self.tagWidgets.append(checkBox)
            self.tagFLayout.addWidget(checkBox)
        self.downloadButton.setEnabled(True)
        self.urlSearchButton.setEnabled(True)

    @QtCore.Slot()
    def onclickedTagsearchButton(self):
        for widget in self.tagWidgets:
            widget.setChecked(False)
            widget.setVisible(False)

        if self.tagsearchLineEdit.text() == "":
            for widget in self.tagWidgets:
                widget.setVisible(True)
        else:
            searchTags = re.split(r'[,\s，]+', self.tagsearchLineEdit.text())
            for widget in self.tagWidgets:
                for tag in searchTags:
                    if tag in widget.text():
                        widget.setVisible(True)
            
    @QtCore.Slot()
    def onclickedTagAllSelectButton(self):
        for widget in self.tagWidgets:
            if widget.isVisible():
                widget.setChecked(True)

    async def onclickedDownloadButton(self):
        self.downloadButton.setEnabled(False)
        directory = self.selectDirectoryDialog()
        if directory == "":
            self.detailTextEdit.append("No directory selected.")
            return
        else:
            directory = Path(directory)
            self.detailTextEdit.append(f"Directory selected: {directory}")
            selectedTags = []
            for widget in self.tagWidgets:
                if widget.isChecked():
                    selectedTags.append(widget.text())
            
            self.detailTextEdit.append("Selected tags:")
            for tag in selectedTags:
                for data in self.datas:
                    if data['subjects'] == tag:
                        download_url = data['download_url'].get('View PDF')
                        if download_url:
                            self.detailTextEdit.append(f"Download: {data['title']}")
                            with open(directory / f"{data["title"]}.pdf", "wb") as f:
                                f.write(await fetch_html(download_url))
            self.detailTextEdit.append("Download completed.")
        self.downloadButton.setEnabled(True)
    
    def selectDirectoryDialog(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        return directory
