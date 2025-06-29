from PySide6.QtWidgets import QApplication, QTextEdit, QWidget, QPlainTextEdit, QScrollBar
from PySide6.QtGui import QPainter, QTextCharFormat, QTextCursor, QTextFormat, QColor, QWheelEvent, QKeyEvent
from PySide6.QtCore import Qt, QRect, QSize, QPoint

import ErrorWindow

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)

class CodeArea(QPlainTextEdit):  # use QPlainTextEdit instead of QTextEdit for easier handling
    def __init__(self):
        super().__init__()
        self.file_to_errors_mapping = dict()
        self.ErrorWindow = ErrorWindow.ErrorWindow()
        self.lineNumberArea = LineNumberArea(self)

        # Connect events to the necesarry methods
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        self.affected_lines = dict()

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

        # Set horizontal scrollbar
        horizontalScrollBar = QScrollBar(Qt.Horizontal)
        self.setHorizontalScrollBar(horizontalScrollBar)

        self.zoom = 0  # Track zoom level

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn(1)
                self.zoom += 1
            else:
                self.zoomOut(1)
                self.zoom -= 1
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                self.zoomIn(1)
                self.zoom += 1
                event.accept()
                return
            elif event.key() == Qt.Key_Minus:
                self.zoomOut(1)
                self.zoom -= 1
                event.accept()
                return
            elif event.key() == Qt.Key_0:
                # Reset zoom
                self.zoomOut(self.zoom)
                self.zoom = 0
                event.accept()
                return
        super().keyPressEvent(event)

    def lineNumberAreaWidth(self):
        digits = len(str(self.blockCount())) # Takes the number of lines and counts its digits
        space = 6 + self.fontMetrics().horizontalAdvance('9') * digits # Makes space according to the maximum number of digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
        
    # Updates on scrolling or opening another file
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    # Constantly paints the Code Area
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)

                padding = 4
                painter.drawText(
                    padding,
                    top,
                    self.lineNumberArea.width() - 2 * padding,
                    self.fontMetrics().height(),
                    Qt.AlignRight | Qt.AlignVCenter,
                    number
                )

                painter.drawText(0, top, self.lineNumberArea.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    # Highlights the line the cursor is currently on and the ones with vulnerabilities
    # And updates the current error if the cursor is on an error
    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.gray).darker(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selected_line = selection.cursor.blockNumber() + 1
            selection.cursor.clearSelection()
            extraSelections.append(selection)

            if not self.file_to_errors_mapping:
                return

            # Highlight the affected lines
            affectedLineColor = QColor(160, 160, 0) # yellow
            for error in self.file_to_errors_mapping:
                if error.severity not in {"Low", "Medium", "High", "Critical"}:
                    continue
                errorStart = error.first_line
                errorEnd = error.last_line
                selection = QTextEdit.ExtraSelection()
                selection.format.setBackground(affectedLineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textCursor()
                selection.cursor.clearSelection()
                selection.cursor.movePosition(QTextCursor.Start)
                selection.cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, errorStart - 1)

                for line in range(errorStart - 1, errorEnd):
                    if line == selected_line - 1:
                        continue
                    block = self.document().findBlockByNumber(line)
                    if block.isValid():
                        selection = QTextEdit.ExtraSelection()
                        selection.format.setBackground(affectedLineColor)
                        selection.format.setProperty(QTextFormat.FullWidthSelection, True)

                        cursor = QTextCursor(block)
                        selection.cursor = cursor
                        selection.cursor.clearSelection()

                        extraSelections.append(selection)

            error_found = False

            for error in self.file_to_errors_mapping:
                if error.severity not in {"Low", "Medium", "High", "Critical"}:
                    continue
                elif selected_line >= error.first_line and selected_line <= error.last_line:
                    content = f"Current line: {selected_line}\n\n"
                    content += f"Error in lines: {error.first_line} - {error.last_line}\n\n"
                    content += "Description: " + error.description + '\n'
                    content += "Severity: " + error.severity
                    self.ErrorWindow.error_description_box.setPlainText(content)
                    error_found = True
                    break

            if not error_found:
                content = "No error in this line."
                self.ErrorWindow.error_description_box.setPlainText(content)

        self.setExtraSelections(extraSelections)