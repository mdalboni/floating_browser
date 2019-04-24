import os
import re
import sys

from PySide2.QtCore import QEvent, QRect, QTimer, QUrl, Qt, Signal
from PySide2.QtGui import QIcon, QPixmap, qApp
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from PySide2.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QMenu, QSizeGrip, QSizePolicy, QVBoxLayout
from adblockparser import AdblockRules

from resources.qtloader import QtUiLoader
from webpage import CustomWebPage


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):

    def __init__(self, path=''):
        QWebEngineUrlRequestInterceptor.__init__(self)
        with open(f'{path}resources/easylist.txt') as f:
            self.raw_rules = f.readlines()
            self.rules = AdblockRules(self.raw_rules)

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if self.rules.should_block(url):
            info.block(True)


class FloaterWindow(QMainWindow):
    IS_PRODUCTION = getattr(sys, 'frozen', False)
    path = os.path.join(os.path.dirname(sys.executable), 'lib/') if IS_PRODUCTION else ''
    video_list_signal = Signal(int)

    def __init__(self):
        QMainWindow.__init__(self)
        self.setAccessibleName("MainForm")
        self.setObjectName("MainForm")
        self.setStyleSheet("#MainForm{background:black;}")
        self.setMinimumSize(350, 150)
        self.resize(300, 220)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.videos_menu = QMenu()
        self.video_available = False
        self.setup_images()
        self.setup_ui()
        self.setup_signals()
        self.original_flags = self.windowFlags()
        self.css_original = self.widget.styleSheet()

    def hideItens(self):
        self.widget.txtUrl.setVisible(False)
        self.widget.btnUrl.setVisible(False)
        self.widget.btnVideos.setVisible(False)
        self.widget.btnFix.setVisible(False)
        self.widget.btnClose.setVisible(False)
        self.widget.btnMove.setVisible(False)
        self.sizegrip.setVisible(False)

        self.widget.setStyleSheet('''
        #wdgMenu{ background-color: transparent; }
        QPushButton{ border:none; }
        ''')

    def showItens(self):
        self.widget.txtUrl.setVisible(True)
        self.widget.btnUrl.setVisible(True)
        self.widget.btnFix.setVisible(True)
        self.widget.btnVideos.setVisible(self.video_available)
        self.widget.btnClose.setVisible(True)
        self.widget.btnMove.setVisible(True)
        self.sizegrip.setVisible(True)
        self.widget.setStyleSheet(self.css_original)
        self.widget.txtUrl.setFocus()

    def setup_signals(self):
        self.qwebview.urlChanged.connect(self.update_text)
        self.widget.txtUrl.returnPressed.connect(self.urlChanged)
        self.widget.btnClose.clicked.connect(self.close_event)
        self.widget.wdgMenu.installEventFilter(self)
        self.widget.btnMove.installEventFilter(self)
        self.widget.btnFix.clicked.connect(self.toogle_visibility)
        self.video_list_signal.connect(self.update_video_list)

    def update_video_list(self, size):
        if self.widget.btnVideos.menu():
            self.widget.btnVideos.menu().clear()

        if size:
            self.video_available = True
            self.videos_menu = QMenu()
            for video_idx in range(size):
                self.videos_menu.addAction(f'Video #{video_idx + 1}', lambda value=f'openVideo({video_idx});': self.page.runJavaScript(value))
            self.widget.btnVideos.setMenu(self.videos_menu)
        else:
            self.video_available = False

    def close_event(self):
        sys.exit(0)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter and source is self.widget.wdgMenu:
            self.showItens()

        if event.type() == QEvent.FocusAboutToChange and source is self.qwebview:
            self.hideItens()

        if event.type() == QEvent.Leave and source is self.widget.wdgMenu:
            if not self.videos_menu.isVisible():
                self.hideItens()

        if event.type() == QEvent.MouseButtonPress and source is self.widget.btnMove:
            self.offset = event.pos()

        if event.type() == QEvent.MouseMove and source is self.widget.btnMove:
            x = event.globalX()
            y = event.globalY()
            x_w = self.offset.x() + 27
            y_w = self.offset.y() + 9
            self.move(x - x_w, y - y_w)

        return super(FloaterWindow, self).eventFilter(source, event)

    def setup_images(self):
        self.img_pin_on = QIcon(f'{self.path}resources/pin_on.png')
        self.img_pin_off = QIcon(f'{self.path}resources/pin_off.png')
        self.img_resize = QIcon(f'{self.path}resources/resize.png')
        self.img_close = QIcon(f'{self.path}resources/close.png')
        self.img_move = QIcon(f'{self.path}resources/move.png')
        self.img_video = QIcon(f'{self.path}resources/video.png')

    def setup_ui(self):
        self.setStyleSheet('QMainWindow{padding-top:-10px}')
        self.widget = QtUiLoader().load_ui(f'{self.path}resources/main.ui', self)
        self.setLayout(QHBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.setCentralWidget(self.widget)

        self.sizegrip = QSizeGrip(self.widget.pnlResize)

        self.widget.txtUrl.setMinimumWidth(50)
        self.widget.txtUrl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        fix_icon = QIcon()
        fix_icon.addPixmap(QPixmap(f'{self.path}resources/view.png'), QIcon.Normal, QIcon.On)
        fix_icon.addPixmap(QPixmap(f'{self.path}resources/hide.png'), QIcon.Normal, QIcon.Off)

        self.widget.btnMove.setIcon(self.img_move)
        self.widget.btnFix.setIcon(fix_icon)
        self.widget.btnVideos.setIcon(self.img_video)
        self.widget.btnUrl.setIcon(QIcon(f'{self.path}resources/share.png'))
        self.widget.btnClose.setIcon(self.img_close)

        self.setup_browser()

        self.widget.wdgWeb.setLayout(QVBoxLayout())
        self.widget.wdgWeb.layout().setMargin(0)
        self.widget.wdgWeb.layout().addWidget(self.qwebview)

    def setup_browser(self):
        self.qwebview = QWebEngineView()
        self.qwebview.setStyleSheet("background:black")
        self.page = CustomWebPage(self.video_list_signal)
        self.page.profile().clearHttpCache()
        self.qwebview.setPage(self.page)
        self.qwebview.setObjectName('webview')
        self.qwebview.layout().setMargin(0)
        self.qwebview.layout().setSpacing(0)
        self.qwebview.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

    def resizeEvent(self, *args, **kwargs):
        self.widget.wdgMenu.resize(self.width(), self.widget.wdgMenu.height())
        self.widget.wdgWeb.resize(self.width(), self.height())
        self.qwebview.setGeometry(QRect(0, 0, self.width(), self.height()))
        self.widget.resize(self.width(), self.height())

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
        self.hideItens()
        self.disconnect_signals()
        path = self.widget.txtUrl.text()
        if 'www' in path or '.com' in path:
            if 'http://' not in path and 'https://' not in path:
                path = 'http://' + path
        if 'youtube.com' in path and '/watch' in path:
            groups = re.search('http[s]?:\/\/[w]{0,3}\.?youtube\.com\/watch\?v=([a-zA-Z0-9]*)', path, re.IGNORECASE)
            extracted_youtube = groups.group(1)
            self.qwebview.load(QUrl(self.load_html(extracted_youtube)))
            self.video_available = False
        else:
            self.qwebview.load(QUrl(path))
            self.video_available = True

    def load_html(self, video):
        return f"https://www.youtube.com/embed/{video}?controls=1"

    def toogle_visibility(self):
        if not self.widget.btnFix.isChecked():
            self.setWindowFlags(self.original_flags)
            self.show()
        else:
            self.setWindowFlags(self.original_flags | Qt.WindowStaysOnTopHint)
            self.show()

    def widgets_at(self, pos):
        widgets = []
        widget_at = qApp.widgetAt(pos)

        while widget_at:
            widgets.append(widget_at)

            # Make widget invisible to further enquiries
            widget_at.setAttribute(Qt.WA_TransparentForMouseEvents)
            widget_at = qApp.widgetAt(pos)

        # Restore attribute
        for widget in widgets:
            widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        return widgets


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main_wdg = FloaterWindow()
    main_wdg.show()
    sys.exit(app.exec_())
