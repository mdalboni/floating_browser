import os
import shutil
import sys

from cx_Freeze import Executable

from windist import setup


class AppConstants:
    NAME = 'Floating Browser'
    VERSION = '0.0.1'
    COMPANY = 'Dalboni Corp'
    EXECUTABLE = 'floating.exe'
    INSTALLER = 'floating.msi'


###############################
# PARAMS
###############################

project_path = os.path.dirname(sys.argv[0])

# clean build and dist folders
shutil.rmtree(os.path.join(project_path, 'build'), ignore_errors=True)
shutil.rmtree(os.path.join(project_path, 'dist'), ignore_errors=True)

# version_file_path = os.path.join(project_path, 'app/core/version.py')
# with open(version_file_path, 'w') as f:
#     f.write(f"VERSION = '{product_version}'\n")

# env vars
python_root_path = os.path.dirname(os.path.dirname(sys.executable))
venv_lib_path = os.path.join(python_root_path, 'Lib\site-packages')
win32_path = os.path.join(venv_lib_path, 'win32')

# Make sure cx_freeze will find those env vars
os.environ['TCL_LIBRARY'] = r''
os.environ['TK_LIBRARY'] = r''

# -------------------- Arquivos Obrigatorios --------------------
# Dependencias Windows -> MSVCP140.dll / VCRUNTIME140.dll
# Dependencias Qt -> Qt5Core.dll / Qt5Gui.dll / Qt5Network.dll / Qt5Widgets.dll /
# Dependencias Win32.dll -> win32api.pyd / win32gui.pyd
# -------------------- Arquivos Obrigatorios --------------------

bdist_msi_options = {
    'target_name': AppConstants.NAME,
    'initial_target_dir': r'[ProgramFilesFolder]\%s\%s' % (AppConstants.COMPANY, AppConstants.NAME),
    'upgrade_code': '{F89D759E-6969-42FF-8EC6-211D4E7E6666}',
    'add_to_path': True
    # 'install_icon': os.path.join(project_path, 'app\\resources\\img\\decora.ico')
}

build_exe_options = {
    'packages': ['adblockparser', 'PySide2', 'shiboken2'],
    "include_files": [
        '3rdparty/msv1_0.dll',
        '3rdparty/msvcirt.dll',
        '3rdparty/msvcp60.dll',
        '3rdparty/msvcp100.dll',
        '3rdparty/msvcp110.dll',
        '3rdparty/msvcp110_win.dll',
        '3rdparty/msvcp120.dll',
        '3rdparty/msvcp120_clr0400.dll',
        '3rdparty/msvcp140.dll',
        '3rdparty/msvcp140_1.dll',
        '3rdparty/msvcp_win.dll',
        '3rdparty/msvcr100.dll',
        '3rdparty/msvcr100_clr0400.dll',
        '3rdparty/msvcr110.dll',
        '3rdparty/msvcr120.dll',
        '3rdparty/msvcr120_clr0400.dll',
        '3rdparty/msvcrt.dll',
        '3rdparty/vcruntime140.dll'
    ],
    'excludes': ['dist', 'build', 'Tkinter', 'tcl', 'tk', 'pandas', 'matplotlib'],
    'includes': ['resources'],
    'include_msvcr': True,
    'silent': True,
    'optimize': 2
}

exe = Executable(
    script='main.py',
    base='Win32GUI',
    shortcutName=AppConstants.NAME,
    shortcutDir='DesktopFolder',
    # icon=os.path.join(project_path, 'app\\resources\\img\\decora.ico'),
    targetName=AppConstants.EXECUTABLE,
    copyright=AppConstants.COMPANY,
    trademarks=AppConstants.COMPANY
)

setup(
    name=AppConstants.NAME,
    version=AppConstants.VERSION,
    description=AppConstants.NAME,
    executables=[exe],
    author=AppConstants.COMPANY,
    author_email='dalboni.max@hotmail.com',
    options={
        'bdist_msi': bdist_msi_options,
        'build_exe': build_exe_options
    }
)
