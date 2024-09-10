import sys
import os
import datetime
import regex as re
import tinify
from pathlib import Path
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox, QMenu
from PyQt6.QtGui import QContextMenuEvent
from concurrent.futures import ThreadPoolExecutor

# 標題
TitelName = 'TinyPNG Compress GUI'

# 轉為exe 使用絕對路徑 解析img位置
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ApiKeyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TinyPNG API Key")
        self.setFixedSize(300, 120)  # 設定對話框的固定大小
        
        # 設定樣式
        self.setStyleSheet("""
            QDialog {
                background-color: #2e3440; 
                color: #eceff4; 
                font-family: 'Microsoft JhengHei UI'; 
                font-size: 12pt;
            }
            QLabel {
                font-size: 12pt;
                color: #eceff4;
                margin: 0px;
                padding: 0px;
            }
            QLineEdit {
                font-size: 14px;
                font-weight: bold;
                background-color: #3b4252;
                border: 1px solid #4c566a;
                color: #eceff4;
                padding: 5px;
                border-radius: 5px;
            }
            QDialogButtonBox {
                background-color: transparent;
            }
            QPushButton {
                width: 70px;
                height: 25px;
                font-size: 12pt;
                background-color: #3b4252;
                color: #eceff4;
                padding: 5px 10px;
                border-radius: 2px;
            }
            QPushButton:hover { 
                background-color: #5e81ac; 
            }
            QPushButton:pressed {
                background-color: #4c566a;
            }
        """)

        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("請輸入 API Key:")
        layout.addWidget(self.label)

        self.line_edit = QtWidgets.QLineEdit()
        layout.addWidget(self.line_edit)

        # 設定 QDialogButtonBox
        self.button_box = QtWidgets.QDialogButtonBox(QtCore.Qt.Orientation.Horizontal)
        self.ok_button = QtWidgets.QPushButton("確定")
        self.cancel_button = QtWidgets.QPushButton("取消")

        # 添加按鈕到 QDialogButtonBox
        self.button_box.addButton(self.ok_button, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.addButton(self.cancel_button, QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)

        layout.addWidget(self.button_box)

        # 將按鈕的信號與 accept/reject 行為連接
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.setLayout(layout)

    def get_key(self):
        return self.line_edit.text()

# 取得 tinify API Key
def get_tinify_key():
    key_file_path = "TinyPNG.Key"
    if not os.path.exists(key_file_path):
        # 如果 TinyPNG.Key 不存在，顯示自定義對話框要求用戶輸入 API Key
        dialog = ApiKeyDialog()
        
        # 彈出對話框
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            key = dialog.get_key()
            if key:
                with open(key_file_path, 'w') as f:
                    f.write(key)
                tinify.key = key
            else:
                # 顯示錯誤訊息，使用 dialog 作為父窗口
                show_custom_critical_message(dialog, "未提供 API Key。程序無法繼續。")
                sys.exit()
        else:
            # 顯示錯誤訊息，使用 dialog 作為父窗口
            show_custom_critical_message(dialog, "未提供 API Key。程序無法繼續。")
            sys.exit()
    else:
        with open(key_file_path, 'r') as f:
            tinify.key = f.read().strip()

# 顯示提示視窗 並定義按鈕名稱
def show_custom_critical_message(parent, message):
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("錯誤")
    msg_box.setText(message)

    # 自定義按鈕
    ok_button = QtWidgets.QPushButton("確認")
    msg_box.addButton(ok_button, QtWidgets.QMessageBox.ButtonRole.AcceptRole)

    # 使原有的 OK 按鈕不可見
    default_button = msg_box.button(QtWidgets.QMessageBox.StandardButton.Ok)
    if default_button:
        default_button.setVisible(False)

    ok_button.clicked.connect(msg_box.accept)

    msg_box.exec()


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(520, 320)
        Form.setMinimumSize(QtCore.QSize(520, 320))
        Form.setMaximumSize(QtCore.QSize(520, 320))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('img/LOGO.ico')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        Form.setWindowIcon(icon)
        Form.setStyleSheet("background-color: #2e3440; color: #eceff4; font-family: 'Microsoft JhengHei UI'; font-size: 12pt;")

        # 列表選單樣式
        self.listWidget = QtWidgets.QListWidget(parent=Form)
        self.listWidget.setGeometry(QtCore.QRect(10, 20, 500, 200))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setStyleSheet("QScrollBar:vertical { border: none; background-color: #4c566a; width: 12px; margin: 0; } QScrollBar::handle:vertical { background-color: #88c0d0; min-height: 20px; border-radius: 5px; } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0; } QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; } QScrollBar:horizontal { border: none; background-color: #4c566a; height: 12px; margin: 0; } QScrollBar::handle:horizontal { background-color: #88c0d0; min-width: 20px; border-radius: 5px; } QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; width: 0; } QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }")

        # 進度條樣式
        self.progressBar = QtWidgets.QProgressBar(parent=Form)
        self.progressBar.setGeometry(QtCore.QRect(10, 230, 500, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.Direction.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet(
            "QProgressBar { border: 2px solid #4c566a; border-radius: 5px; text-align: center; }"
            "QProgressBar::chunk { background-color: #88c0d0; width: 20px; }")

        # 按鈕樣式
        button_style = ("QPushButton { background-color: #3b4252; border-radius: 8px; color: #eceff4; font-size: 16pt; }"
                        "QPushButton:hover { background-color: #5e81ac; }")

        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setGeometry(QtCore.QRect(10, 265, 70, 41))
        self.pushButton.setFont(QtGui.QFont("Microsoft JhengHei UI", 16))
        self.pushButton.setStyleSheet(button_style)
        self.pushButton.setText("📁")
        self.pushButton.setObjectName("pushButton")

        self.pushButton_2 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_2.setGeometry(QtCore.QRect(100, 265, 70, 41))
        self.pushButton_2.setFont(QtGui.QFont("Microsoft JhengHei UI", 16))
        self.pushButton_2.setStyleSheet(button_style)
        self.pushButton_2.setText("❌")
        self.pushButton_2.setObjectName("pushButton_2")

        self.pushButton_3 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_3.setGeometry(QtCore.QRect(190, 265, 320, 41))
        self.pushButton_3.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Weight.Bold))
        self.pushButton_3.setStyleSheet(button_style)
        self.pushButton_3.setText("執  行")
        self.pushButton_3.setObjectName("pushButton_3")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(TitelName)


class FileProcessor(QtCore.QObject):
    progressUpdated = QtCore.pyqtSignal(int)
    processingFinished = QtCore.pyqtSignal(int, int, str)  # 成功, 失敗, log

    def __init__(self):
        super().__init__()
    
    # 處理圖片文件的壓縮
    def compress_image(self, input_file_path, output_file_path):
        try:
            # 壓縮圖片並保存到指定的輸出文件路徑
            source = tinify.from_file(input_file_path)
            source.to_file(output_file_path)
            return True
        except tinify.Error as e:
            # 紀錄錯誤訊息
            return str(e)

    def remove_comments(self, content, pattern):
        return re.sub(pattern, '', content)

    def remove_blank_lines(self, content):
        return re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)

    def process_file(self, file_path, log_file):
        try:
            # 獲取文件名和副檔名
            file_name, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()

            # 確認是圖片文件
            if file_extension in ['.png', '.jpg', '.jpeg', '.webp', '.apng']:
                # 輸出文件路徑
                output_file_path = os.path.join("output", os.path.basename(file_name) + "_compress" + file_extension)

                # 確保 output 資料夾存在
                if not os.path.exists("output"):
                    os.makedirs("output")

                result = self.compress_image(file_path, output_file_path)

                if result:
                    return True
                else:
                    # 錯誤訊息
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(f"壓縮失敗: {file_path}\n錯誤訊息: {result}\n")
                    return False
            else:
                # 如果不是圖片文件，記錄為處理未成功
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(f"忽略非圖片文件: {file_path}\n")
                return False

        except Exception as e:
            # 紀錄其他錯誤
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"[{current_time}]\n檔案: {file_path}\n錯誤: {str(e)}\n\n")
            return False

    def process_files(self, file_paths):
        success_count = 0
        fail_count = 0
        log_file = "Error_Log.txt"

        # 檢查是否有選擇檔案
        if file_paths:

            for i, file_path in enumerate(file_paths):
                if self.process_file(file_path, log_file):
                    success_count += 1
                else:
                    fail_count += 1

                progress = int((i + 1) / len(file_paths) * 100)
                self.progressUpdated.emit(progress)

        self.processingFinished.emit(success_count, fail_count, log_file)


class MainWindow(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 調用 Tinify API Key
        get_tinify_key()

        self.pushButton.clicked.connect(self.open_files)
        self.pushButton_2.clicked.connect(self.remove_selected_files)
        self.pushButton_3.clicked.connect(self.process_files)
        self.listWidget.setAcceptDrops(True)
        self.listWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DropOnly)

        self.listWidget.installEventFilter(self)  # 啟用事件過濾器

        self.file_processor = FileProcessor()
        self.file_processor.progressUpdated.connect(self.update_progress_bar)
        self.file_processor.processingFinished.connect(self.show_summary)

        # 文件處理線程
        self.thread_pool = ThreadPoolExecutor()

        # 右鍵菜單
        self.context_menu = QMenu(self)
        self.context_menu.addAction("開啟資料夾", self.open_folder)
        self.context_menu.addAction("刪除選擇", self.remove_selected_files)
        self.context_menu.addAction("清空全部", self.clear_all_files)
        self.context_menu.setStyleSheet(
            "QMenu { background-color: #3b4252; border: 1px solid #4c566a; }"
            "QMenu::item { padding: 5px 20px; }"
            "QMenu::item:selected { background-color: #5e81ac; }"
        )

    # 鍵盤觸發刪除
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key.Key_Delete:
            self.remove_selected_files()
        super().keyPressEvent(event)

    # 覆蓋事件過濾器函數
    def eventFilter(self, source, event):
        if source == self.listWidget:
            if event.type() == QtCore.QEvent.Type.DragEnter:
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
                    return True
            elif event.type() == QtCore.QEvent.Type.Drop:
                for url in event.mimeData().urls():
                    file_path = url.toLocalFile()
                    if not self.is_duplicate(file_path):
                        self.listWidget.addItem(file_path)
                return True
        return super().eventFilter(source, event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if not self.is_duplicate(file_path):
                self.listWidget.addItem(file_path)

    def open_files(self):
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "選擇文件", "", "所有文件 (*)")
        for file_path in file_paths:
            if not self.is_duplicate(file_path):
                self.listWidget.addItem(file_path)

    def is_duplicate(self, file_path):
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).text() == file_path:
                return True
        return False

    def remove_selected_files(self):
        selected_items = self.listWidget.selectedItems()
        for item in selected_items:
            self.listWidget.takeItem(self.listWidget.row(item))

    def clear_all_files(self):
        self.listWidget.clear()

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.context_menu.exec(event.globalPos())

    def update_progress_bar(self, value):
        self.progressBar.setValue(value)

    def show_summary(self, success_count, fail_count, log_file):
        self.progressBar.setValue(100)
        if fail_count > 0:
            message = f"完成: {success_count} 個，失敗: {fail_count} 個\n失敗的檔案已記錄在 {log_file}\n若為 API 問題可移除 TinyPNG.Key 重新輸入。"
        else:
            message = f"完成: {success_count} 個，失敗: {fail_count} 個"
        QMessageBox.information(self, "處理結果", message)

    def process_files(self):
        if self.listWidget.count() == 0:
            QMessageBox.warning(self, "警告", "請選擇至少一個文件進行處理")
            return

        file_paths = [self.listWidget.item(i).text() for i in range(self.listWidget.count())]
        self.progressBar.setValue(0)

        # 單線程處裡
        self.thread_pool.submit(self.file_processor.process_files, file_paths)

    def open_folder(self):
        selected_items = self.listWidget.selectedItems()
        if selected_items:
            for item in selected_items:
                file_path = item.text()
                folder_path = os.path.dirname(file_path)
                folder_path = Path(folder_path)  # 使用 pathlib 處理路徑

                if not folder_path.exists() or not folder_path.is_dir():
                    QMessageBox.warning(self, "警告", f"資料夾不存在: {folder_path}")
                    continue

                try:
                    os.startfile(str(folder_path))
                except Exception as e:
                    # 顯示其他錯誤訊息
                    QMessageBox.critical(self, "錯誤", f"發生錯誤:\n{e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
