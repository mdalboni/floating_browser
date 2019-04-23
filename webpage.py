from PySide2.QtCore import QFile, QIODevice, QUrl, Slot
from PySide2.QtWebChannel import QWebChannel
from PySide2.QtWebEngineWidgets import QWebEnginePage


class WebEnginePage(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        super(WebEnginePage, self).__init__(*args, **kwargs)
        self.loadFinished.connect(self.load_finished)

    @Slot(bool)
    def load_finished(self, status):
        if status:
            self.load_qwebchannel()
            self.run_scripts_on_load()

    def load_qwebchannel(self):
        file = QFile("resources/qwebchannel.js")
        if file.open(QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            self.runJavaScript(content.data().decode())
        if self.webChannel() is None:
            self.setWebChannel(QWebChannel(self))

    def add_objects(self, objects):
        if self.webChannel() is not None:
            initial_script = ""
            end_script = ""
            self.webChannel().registerObjects(objects)
            for name, obj in objects.items():
                initial_script += "var {helper};".format(helper=name)
                end_script += "{helper} = channel.objects.{helper};".format(helper=name)
            js = initial_script + \
                 "new QWebChannel(qt.webChannelTransport, function (channel) {" + \
                 end_script + \
                 "} );"
            self.runJavaScript(js)

    def run_scripts_on_load(self):
        pass


class CustomWebPage(WebEnginePage):
    js = """
        function videoCountCallback(){
            qt_action.update_video_list(vids.length);
        }
               
        let vids = document.getElementsByTagName('video');        
        if ( vids == undefined ){
            vids = 0;                                      
        }
        setTimeout(videoCountCallback, 1000)
        
        
        function openVideo(index) {        
            let divs = document.getElementsByTagName("div");
            for (let i = 0; i < divs.length; i++) {
                divs[i].style.display = 'none';
            }
            
            let sections = document.getElementsByTagName("section");
            for (let i = 0; i < sections.length; i++) {
                sections [i].style.display = 'none';
            }
            
            document.body.style.background = "black";
            document.body.style.margin = "0";
            document.body.style.overflow = "hidden";
            document.body.style.border = "0";
            vids[index].style.maxHeight = "100%";
            vids[index].style.maxWidth = "100%";
            vids[index].style.height = "100%";
            vids[index].style.width = "100%";
            
            document.body.appendChild(vids[index]);
        }"""

    def __init__(self, signal, *args, **kwargs):
        WebEnginePage.__init__(self, *args, **kwargs)
        self.video_list_signal = signal
        self.featurePermissionRequested.connect(self.permission_requested)
        self.load(QUrl("https://google.com"))

    @Slot(QUrl, QWebEnginePage.Feature)
    def permission_requested(self, url, feature):
        if feature in (QWebEnginePage.MediaAudioCapture, QWebEnginePage.MediaVideoCapture, QWebEnginePage.MediaAudioVideoCapture):
            self.setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser)
        else:
            self.setFeaturePermission(url, feature, WebEnginePage.PermissionDeniedByUser)

    def run_scripts_on_load(self):
        self.add_objects({"qt_action": self})
        self.runJavaScript(self.js)

    @Slot(int)
    def update_video_list(self, size):
        self.video_list_signal.emit(size)
