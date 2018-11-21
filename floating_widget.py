import os
import re

from PySide2 import QtUiTools
from PySide2.QtCore import QEvent, QFile, QRect, QTimer, QUrl, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView
from PySide2.QtWidgets import QApplication, QLineEdit, QMainWindow, QPushButton, QSizeGrip, QSizePolicy, QVBoxLayout, QWidget
from adblockparser import AdblockRules


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):

    def __init__(self):
        QWebEngineUrlRequestInterceptor.__init__(self)
        with open("easylist.txt") as f:
            self.raw_rules = f.readlines()
            self.rules = AdblockRules(self.raw_rules)

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if self.rules.should_block(url):
            info.block(True)


class FloaterWindow(QMainWindow):
    css_off = '''
    QPushButton{border:none; background:transparent}
    '''

    css_on = '''
    QPushButton{border:1px; background:red}
    '''

    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(300, 220)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setup_images()
        self.setup_ui()
        self.setup_signals()

    def hideItens(self):
        self.txt_url.setVisible(False)
        self.btn_url.setVisible(False)
        self.btn_fix.setVisible(False)
        self.btn_opacity.setVisible(False)
        self.btn_close.setVisible(False)
        self.btn_move.setVisible(False)
        self.sizegrip.setVisible(False)

        self.wdg.setStyleSheet('''
        #wdgMenu{ background-color: transparent; }
        QPushButton{ border:none; }
        ''')

        self.btn_move.setStyleSheet(self.css_off)

    def showItens(self):
        self.txt_url.setVisible(True)
        self.btn_url.setVisible(True)
        self.btn_fix.setVisible(True)
        self.btn_close.setVisible(True)
        self.btn_move.setVisible(True)
        self.btn_opacity.setVisible(False)
        self.sizegrip.setVisible(True)
        self.wdg.setStyleSheet('''
        #wdgMenu{ background-color: qlineargradient(spread:pad, x1:0.494636, y1:0.381, x2:0.523, y2:1, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 0)); }
        QPushButton{ border:none; }
        ''')

    def setup_signals(self):
        self.qwebview.urlChanged.connect(self.update_text)
        self.txt_url.returnPressed.connect(self.urlChanged)
        self.top_menu.installEventFilter(self)
        self.btn_move.installEventFilter(self)
        self.btn_close.clicked.connect(self.close_event)

    def close_event(self):
        sys.exit(0)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter and source is self.top_menu:
            self.showItens()

        if event.type() == QEvent.Leave and source is self.top_menu:
            self.hideItens()

        if event.type() == QEvent.MouseButtonPress and source is self.btn_move:
            self.offset = event.pos()

        if event.type() == QEvent.MouseMove and source is self.btn_move:
            x = event.globalX()
            y = event.globalY()
            x_w = self.offset.x() + 20
            y_w = self.offset.y() + 6
            self.move(x - x_w, y - y_w)

        return super(FloaterWindow, self).eventFilter(source, event)

    def setup_images(self):
        self.img_pin_on = QIcon('resources/pin_on.png')
        self.img_pin_off = QIcon('resources/pin_off.png')
        self.img_resize = QIcon('resources/resize.png')
        self.img_close = QIcon('resources/close.png')
        self.img_move = QIcon('resources/move.png')

    def setup_ui(self):
        self.setStyleSheet('QMainWindow{padding-top:-10px}')
        self.wdg = FloaterWindow.load_ui('main.ui', self)
        self.setLayout(QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.setCentralWidget(self.wdg)

        self.top_menu = self.wdg.findChild(QWidget, 'wdgMenu')
        self.pnl_resize = self.wdg.findChild(QWidget, 'pnlResize')
        self.sizegrip = QSizeGrip(self.pnl_resize)
        # self.top_menu.layout().addWidget(self.sizegrip, 0, Qt.AlignTop | Qt.AlignLeft)

        self.pnlBrowser = self.wdg.findChild(QWidget, 'wdgWeb')

        self.btn_move = self.wdg.findChild(QPushButton, 'btnMove')
        self.btn_move.setIcon(self.img_move)

        self.btn_url = self.wdg.findChild(QPushButton, 'btnUrl')

        self.txt_url = self.wdg.findChild(QLineEdit, 'txtUrl')
        self.txt_url.setMinimumWidth(150)
        self.txt_url.setMaximumWidth(2000)
        self.txt_url.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_fix = self.wdg.findChild(QPushButton, 'btnFix')
        self.btn_fix.setIcon(self.img_pin_on)

        self.btn_opacity = self.wdg.findChild(QPushButton, 'btnOpacity')
        self.btn_opacity.setVisible(False)
        # self.btn_opacity.setIcon(self.img_close)
        self.btn_close = self.wdg.findChild(QPushButton, 'btnClose')
        self.btn_close.setIcon(self.img_close)

        self.setup_browser()

        self.pnlBrowser.setLayout(QVBoxLayout())
        self.pnlBrowser.layout().setMargin(0)
        self.pnlBrowser.layout().addWidget(self.qwebview)

    def setup_browser(self):
        self.interceptor = WebEngineUrlRequestInterceptor()
        QWebEngineProfile.defaultProfile().setRequestInterceptor(self.interceptor)
        self.qwebview = QWebEngineView()
        self.qwebview.setObjectName('webview')
        self.qwebview.layout().setMargin(0)
        self.qwebview.layout().setSpacing(0)
        # self.qwebview.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.qwebview.load(QUrl('http://google.com'))
        self.qwebview.setMaximumSize(1920, 1080)

    def resizeEvent(self, *args, **kwargs):
        self.wdg.resize(self.width(), self.height() + 2)
        self.top_menu.resize(self.width(), self.top_menu.height())
        self.pnlBrowser.resize(self.width(), self.height() - 2)
        self.qwebview.setGeometry(QRect(0, 0, self.width(), self.height() - 2))
        self.qwebview.resize(self.width(), self.height() - 2)
        self.repaint()

    def update_text(self):
        self.disconnect_signals()
        self.txt_url.setText(self.qwebview.url().url())
        if '/watch?v=' in self.qwebview.url().url():
            self.urlChanged()

    def disconnect_signals(self):
        QTimer.singleShot(1500, self.setup_url_signal)
        try:
            self.qwebview.urlChanged.disconnect()
        except:
            pass

    def setup_url_signal(self):
        self.qwebview.urlChanged.connect(self.update_text)

    def urlChanged(self):
        self.disconnect_signals()
        path = self.txt_url.text()
        if 'www' in path or '.com' in path:
            if 'http://' not in path and 'https://' not in path:
                path = 'http://' + path
        if 'youtube.com' in path and '/watch' in path:
            groups = re.search('http[s]?:\/\/[w]{0,3}\.?youtube\.com\/watch\?v=([a-zA-Z0-9]*)', path, re.IGNORECASE)
            extracted_youtube = groups.group(1)
            self.qwebview.load(QUrl(self.load_html(extracted_youtube)))
        else:
            self.qwebview.load(QUrl(path))

    def load_html(self, video):
        return f"https://www.youtube.com/embed/{video}?controls=1"

    @staticmethod
    def load_ui(file_name, where=None):
        ui_file_path = os.path.join('resources', file_name)
        loader = QtUiTools.QUiLoader()
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        ui = loader.load(ui_file, where)
        ui_file.close()
        return ui


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main_wdg = FloaterWindow()
    main_wdg.show()
    sys.exit(app.exec_())
