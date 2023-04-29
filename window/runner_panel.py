from logger_tt import logger
from platform import system
from re import compile

from PySide6.QtCore import QProcess
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QPlainTextEdit,
    QWidget,
    QVBoxLayout,
)


class RunnerPanel(QWidget):
    """
    A generic, read-only panel that can be used to display output from something.
    It also has a built-in QProcess functionality.
    """

    def __init__(self):
        super().__init__()
        logger.info("Initializing RunnerPanel")
        self.ansi_escape = compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        self.system = system()
        self.text = QPlainTextEdit(readOnly=True)
        self.text.verticalScrollBar().setValue(self.text.verticalScrollBar().maximum())
        if self.system == "Darwin":
            self.text.setFont(QFont("Monaco"))
        elif self.system == "Linux":
            self.text.setFont(QFont("DejaVu Sans Mono"))
        elif self.system == "Windows":
            self.text.setFont(QFont("Cascadia Code"))

        self.process = QProcess = None

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.setLayout(self.layout)
        self.resize(800, 600)

        self.message("ヽ༼ ຈل͜ຈ༼ ▀̿̿Ĺ̯̿̿▀̿ ̿༽Ɵ͆ل͜Ɵ͆ ༽ﾉ")

    def closeEvent(self, event):
        if self.process is not None:
            self.process.kill()
        event.accept()

    def execute(self, command: str, args: list):
        logger.info("RunnerPanel subprocess initiating...")
        self.process = QProcess(self)
        self.process.setProgram(command)
        self.process.setArguments(args)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardError.connect(self.handle_output)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.finished)
        self.message(f"\nExecuting command:\n{command} {args}")
        self.process.start()

    def handle_output(self):
        data = self.process.readAllStandardOutput()
        stdout = self.ansi_escape.sub("", bytes(data).decode("utf8"))
        self.message(stdout)

    def message(self, line: str):
        logger.debug(line)
        # Hardcoded todds progress output support
        if self.process and "todds" in self.process.program() and "Progress: " in line:
            cursor = self.text.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(line.strip())
        else:
            self.text.appendPlainText(line)

    def finished(self):
        self.message("Subprocess completed.")
