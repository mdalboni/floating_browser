import re

from PySide2.QtCore import QEvent, QRect, QTimer, QUrl, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from PySide2.QtWidgets import QApplication, QMainWindow, QSizeGrip, QSizePolicy, QVBoxLayout
from adblockparser import AdblockRules

from qtloader import QtUiLoader


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
        self.widget.txtUrl.setVisible(False)
        self.widget.btnUrl.setVisible(False)
        self.widget.btnFix.setVisible(False)
        self.widget.btnOpacity.setVisible(False)
        self.widget.btnClose.setVisible(False)
        self.widget.btnMove.setVisible(False)
        self.sizegrip.setVisible(False)

        self.widget.setStyleSheet('''
        #wdgMenu{ background-color: transparent; }
        QPushButton{ border:none; }
        ''')

        self.widget.btnMove.setStyleSheet(self.css_off)

    def showItens(self):
        self.widget.txtUrl.setVisible(True)
        self.widget.btnUrl.setVisible(True)
        self.widget.btnFix.setVisible(True)
        self.widget.btnClose.setVisible(True)
        self.widget.btnMove.setVisible(True)
        self.widget.btnOpacity.setVisible(False)
        self.sizegrip.setVisible(True)
        self.widget.setStyleSheet('''
        #wdgMenu{ background-color: qlineargradient(spread:pad, x1:0.494636, y1:0.381, x2:0.523, y2:1, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 0)); }
        QPushButton{ border:none; }
        ''')

    def setup_signals(self):
        self.qwebview.urlChanged.connect(self.update_text)
        self.widget.txtUrl.returnPressed.connect(self.urlChanged)
        self.widget.wdgMenu.installEventFilter(self)
        self.widget.btnMove.installEventFilter(self)
        self.widget.btnClose.clicked.connect(self.close_event)

    def close_event(self):
        sys.exit(0)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter and source is self.widget.wdgMenu:
            self.showItens()

        if event.type() == QEvent.Leave and source is self.widget.wdgMenu:
            self.hideItens()

        if event.type() == QEvent.MouseButtonPress and source is self.widget.btnMove:
            self.offset = event.pos()

        if event.type() == QEvent.MouseMove and source is self.widget.btnMove:
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
        self.widget = QtUiLoader().load_ui('resources/main.ui', self)
        self.setLayout(QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.setCentralWidget(self.widget)

        self.sizegrip = QSizeGrip(self.widget.pnlResize)
        # self.wdg.wdgMenu.layout().addWidget(self.sizegrip, 0, Qt.AlignTop | Qt.AlignLeft)

        self.widget.btnMove.setIcon(self.img_move)

        self.widget.txtUrl.setMinimumWidth(150)
        self.widget.txtUrl.setMaximumWidth(2000)
        self.widget.txtUrl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.widget.btnFix.setIcon(self.img_pin_on)

        self.widget.btnOpacity.setVisible(False)
        # self.wdg.btnOpacity.setIcon(self.img_close)
        self.widget.btnClose.setIcon(self.img_close)

        self.setup_browser()

        self.widget.wdgWeb.setLayout(QVBoxLayout())
        self.widget.wdgWeb.layout().setMargin(0)
        self.widget.wdgWeb.layout().addWidget(self.qwebview)

    def setup_browser(self):
        # self.interceptor = WebEngineUrlRequestInterceptor()
        # QWebEngineProfile.defaultProfile().setRequestInterceptor(self.interceptor)
        self.qwebview = QWebEngineView()
        self.qwebview.setObjectName('webview')
        self.qwebview.layout().setMargin(0)
        self.qwebview.layout().setSpacing(0)
        self.qwebview.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.qwebview.load(QUrl('http://google.com'))
        self.qwebview.setMaximumSize(1920, 1080)

    def resizeEvent(self, *args, **kwargs):
        self.widget.wdgMenu.resize(self.width(), self.widget.wdgMenu.height())
        self.widget.wdgWeb.resize(self.width(), self.height() - 2)
        self.qwebview.setGeometry(QRect(0, 0, self.width(), self.height() - 2))
        # self.qwebview.resize(self.width(), self.height() - 2)
        self.widget.resize(self.width(), self.height() + 2)

    def update_text(self):
        self.disconnect_signals()
        self.widget.txtUrl.setText(self.qwebview.url().url())
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
        path = self.widget.txtUrl.text()
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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main_wdg = FloaterWindow()
    main_wdg.show()
    sys.exit(app.exec_())
