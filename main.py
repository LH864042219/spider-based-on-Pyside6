from PySide6.QtWidgets import (QApplication)
from qfluentwidgets import (FluentWindow, Theme, setTheme, FluentIcon, NavigationItemPosition)
import sys
from asyncslot import AsyncSlotRunner

from arxiv_interface import ArxivInterface

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spider")
        self.setGeometry(100, 100, 800, 600)

        self.initWidgets()
        self.initNavigation()

    def initWidgets(self):
        self.arxivInterface = ArxivInterface(self)

    def initNavigation(self):
        self.addSubInterface(
            interface=self.arxivInterface,
            icon=FluentIcon.HOME,
            text="Arxiv",
            position=NavigationItemPosition.TOP
        )

    def closeEvent(self, event):
        # 能用就行
        QApplication.shutdown(app)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    setTheme(Theme.AUTO)
    window.show()

    with AsyncSlotRunner():
        app.exec()