from fileinput import close
from imp import reload
import os
import sys
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from adblockparser import AdblockRules
from PyQt5.QtWebEngineCore import *

abs_path = os.path.dirname(__file__)
print(abs_path)

with open(abs_path + "/easylist.txt", encoding='utf-8') as f:
    raw_rules = f.readlines()
    rules = AdblockRules(raw_rules)
    
class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if rules.should_block(url):
            print("block::::::::::::::::::::::", url)
            info.block(True)
            
def last_opened(rel_path):
    with open(abs_path + "/" + rel_path, "r") as file:
        url = file.read()
        return url

class MainBrowser(QMainWindow):
    def __init__(self):
        self.reading = True
        super(MainBrowser, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.browser = QWebEngineView()
        self.readingList = QWebEngineView()
        self.readingList.setUrl(QUrl(last_opened("lasturl2.txt")))
        #self.browser.resize(int(self.browser.frameGeometry().width()*0.7), int(self.browser.frameGeometry().height()*1))
        self.browser.setUrl(QUrl(last_opened("lasturl.txt")))
        self.browser.setZoomFactor(1.5)
        self.browser.urlChanged.connect(self.zoom)
        self.readingList.urlChanged.connect(self.zoom)
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        self.stacked.addWidget(self.browser)
        self.stacked.addWidget(self.readingList)
        self.showMaximized()

        navigation = QToolBar("Navigation")
        navigation.setOrientation(Qt.Vertical)
        navigation.setIconSize(QSize(0, 0))
        navigation.setFixedWidth(0)
        navigation.setFixedHeight(0)
        
        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.go_back)
        back_btn.setShortcut(QKeySequence("Alt+Left"))
        navigation.addAction(back_btn)
        
        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.go_forward)
        forward_btn.setShortcut(QKeySequence("Alt+Right"))
        navigation.addAction(forward_btn)
        
        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.reload)
        reload_btn.setShortcut(QKeySequence("Ctrl+R"))
        navigation.addAction(reload_btn)
        
        hide_search = QAction("Hide Search", self)
        hide_search.triggered.connect(self.hide_search_bar)
        hide_search.setShortcut(QKeySequence("Ctrl+Q"))
        navigation.addAction(hide_search)
        
        switch_btn = QAction("Switch", self)
        switch_btn.triggered.connect(self.switch_view)
        switch_btn.setShortcut(QKeySequence("Ctrl+D"))
        navigation.addAction(switch_btn)
        
        exit_btn = QAction("Exit", self)
        exit_btn.triggered.connect(self.close_app)
        exit_btn.setShortcut(QKeySequence("Ctrl+W"))
        navigation.addAction(exit_btn)
        
        home_btn = QAction("Exit", self)
        home_btn.triggered.connect(self.go_home)
        home_btn.setShortcut(QKeySequence("Ctrl+E"))
        navigation.addAction(home_btn)
        
        self.addToolBar(Qt.LeftToolBarArea, navigation)
        
        self.search_bar = QToolBar("Search Bar")
        self.search_bar.setVisible(False)
        self.search_bar.setMovable(False)
        self.url_bar = QLineEdit()
        self.url_bar.setText(self.browser.url().toDisplayString())
        self.url_bar.setFixedHeight(38)
        self.url_bar.returnPressed.connect(self.go_to_url)
        self.url_bar.setFont(QFont("Helvetica Neue", 12))
        self.search_bar.addWidget(self.url_bar)
        self.search_bar.setFixedHeight(40)
        self.addToolBar(self.search_bar)
        
    def go_back(self):
        if self.stacked.currentIndex() == 0:
            self.browser.back()
        else:
            self.readingList.back()
        
    def go_forward(self):
        if self.stacked.currentIndex() == 0:
            self.browser.forward()
        else:
            self.readingList.forward()
    
    def reload(self):
        if self.stacked.currentIndex() == 0:
            self.browser.reload()
        else:
            self.readingList.reload()
            
    def switch_view(self):
        if not self.reading:
            self.stacked.setCurrentIndex(0)
            self.reading = True
            self.url_bar.setText(self.browser.url().toDisplayString())
        else:
            self.reading = False
            self.stacked.setCurrentIndex(1)
            self.url_bar.setText(self.readingList.url().toDisplayString())
    
    def hide_search_bar(self):
        if self.search_bar.isHidden() == False:
            self.search_bar.setHidden(True)
        else:
            self.search_bar.setHidden(False)
            
    def go_to_url(self):
        if self.stacked.currentIndex() == 0:
            changing = self.browser
        else:
            changing = self.readingList
            
        url = self.url_bar.text()
        if url.startswith("g-> "):
            addon = url.split("> ")[1].replace(" ", "+")
            changing.setUrl(QUrl("https://google.com/search?q=" + addon))
            changing.setZoomFactor(1.5)
        else:
            changing.setUrl(QUrl(url))
            changing.setZoomFactor(1.5)
        
    def zoom(self, q):
        if self.stacked.currentIndex() == 0:
            changing = self.browser
        else:
            changing = self.readingList
            
        self.url_bar.setText(q.toString())
        changing.setZoomFactor(1.5)
    
    def close_app(self):
        with open(abs_path + "/lasturl.txt", "w") as file:
            file.write(self.browser.url().toDisplayString())
        
        with open(abs_path + "/lasturl2.txt", "w") as file:
            file.write(self.readingList.url().toDisplayString())
        
        self.close()
    
    def go_home(self):
        if self.stacked.currentIndex() == 0:
            self.browser.setUrl(QUrl("https://readcomiconline.li"))
        else:
            self.readingList.setUrl(QUrl("https://marvelguides.com/"))
        
        
app = QApplication(sys.argv)
QApplication.setApplicationName("Reading Browser")
interceptor = WebEngineUrlRequestInterceptor()
QWebEngineProfile.defaultProfile().setRequestInterceptor(interceptor)
browser = MainBrowser()
browser.setWindowTitle("Comic Browser")
sys.exit(app.exec_())