import distutils
import msilib
import os
import shutil
from time import sleep

from cx_Freeze import windist
from cx_Freeze.dist import Distribution, _AddCommandClass, build, build_exe, install
from cx_Freeze.dist import install_exe as dist_install_exe


def remove_unused_dependencies():
    sleep(1)

    lib_path = os.path.abspath('./build/exe.win-amd64-3.6/lib/PySide2')
    files_to_remove = [
        # "examples", "include", "qml", "resources", "translations", "libclang.dll", "opengl32sw.dll", "Qt5Designer.dll", "linguist.exe",
        # "Qt5DesignerComponents.dll", "Qt5Location.dll", "QtMultimedia.pyd", "Qt5Charts.dll", "Qt3DRender.pyd", "d3dcompiler_47.dll",
        # "Qt5XmlPatterns.dll", "Qt53DRender.dll", "Qt5QuickTemplates2.dll", "Qt5Multimedia.dll", "lupdate.exe", "MSVCP140.dll", "Qt53DExtras.dll", "designer.exe",
        # "QtLocation.pyd", "vcamp140.dll", "Qt3DExtras.pyd", "qtdiag.exe", "pyside2-rcc.exe", "lrelease.exe", "Qt5Bluetooth.dll", "Qt53DAnimation.dll"
    ]

    if os.path.exists(lib_path):
        for file in files_to_remove:
            try:
                delete_path = os.path.join(lib_path, file)
                if not os.path.exists(delete_path):
                    print(f'Already deleted {delete_path}')
                    continue
                elif os.path.isdir(delete_path):
                    shutil.rmtree(delete_path, ignore_errors=True)
                else:
                    os.remove(delete_path)
                print(f'Deleting {delete_path}')
            except:
                pass

        sleep(1)


class install_exe(dist_install_exe):
    def run(self):
        if not self.skip_build:
            remove_unused_dependencies()
            self.run_command('build_exe')

        self.outfiles = self.copy_tree(self.build_dir, self.install_dir)


class bdist_msi(windist.bdist_msi):
    user_options = windist.bdist_msi.user_options + [
        ('install-icon=', None, 'icon path to add/remove programs ')
    ]

    def add_config(self, fullname):
        windist.bdist_msi.add_config(self, fullname)

    def add_properties(self):
        metadata = self.distribution.metadata
        props = [
            ('DistVersion', metadata.get_version()),
            ('DefaultUIFont', 'DlgFont8'),
            ('ErrorDialog', 'ErrorDlg'),
            ('Progress1', 'Install'),
            ('Progress2', 'installs'),
            ('MaintenanceForm_Action', 'Repair'),
            ('ALLUSERS', '1')
        ]

        email = metadata.author_email or metadata.maintainer_email
        if email:
            props.append(("ARPCONTACT", email))

        if metadata.url:
            props.append(("ARPURLINFOABOUT", metadata.url))

        if self.upgrade_code is not None:
            props.append(("UpgradeCode", self.upgrade_code))

        if self.install_icon:
            props.append(('ARPPRODUCTICON', 'InstallIcon'))
            msilib.add_data(self.db, "Icon", [("InstallIcon", msilib.Binary(self.install_icon))])

        msilib.add_data(self.db, 'Property', props)

    def initialize_options(self):
        windist.bdist_msi.initialize_options(self)
        self.install_icon = None


def setup(**attrs):
    attrs.setdefault("distclass", Distribution)
    command_classes = attrs.setdefault("cmdclass", {})
    _AddCommandClass(command_classes, "bdist_msi", bdist_msi)
    _AddCommandClass(command_classes, "build", build)
    _AddCommandClass(command_classes, "build_exe", build_exe)
    _AddCommandClass(command_classes, "install", install)
    _AddCommandClass(command_classes, "install_exe", install_exe)
    distutils.core.setup(**attrs)
