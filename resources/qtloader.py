import sys

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
import defusedxml.minidom


class QtUiLoader(QUiLoader):
    def _get_class_def(self, module, classname):
        try:
            submodules = sys.modules[module].__dict__.keys()
        except:
            return None

        if classname not in submodules:
            for submodule in submodules:
                found = self._get_class_def(f'{module}.{submodule}', classname)
                if found is not None:
                    return found

            return None

        return getattr(sys.modules[module], classname)

    def load_ui(self, filename, parent=None):
        qfile = QFile(filename)
        qfile.open(QFile.ReadOnly)
        widget_instance = self.load(qfile, parent)
        qfile.close()

        document = defusedxml.minidom.parse(filename)
        widgets = document.getElementsByTagName('widget')
        for widget in widgets:
            try:
                name = widget.attributes['name'].value
                classname = widget.attributes['class'].value
                setattr(widget_instance, name, widget_instance.findChild(self._get_class_def('PySide2', classname), name))
            except:
                print(f'Widget {name} class name error.')

        return widget_instance
