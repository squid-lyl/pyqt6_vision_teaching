#coding:utf-8
import datetime
import subprocess
import importlib
import json
import os
import random
import sys
import time
import webbrowser
import chardet
from tkinter import filedialog
# import git
# import pyjokes
import qdarktheme
from pyqtconsole.console import PythonConsole
from PyQt6.QtCore import Qt, QSize,QPoint
from PyQt6.QtGui import QColor, QFont, QActionGroup, QFileSystemModel, QPixmap, QIcon,QPainter,QPalette
from PyQt6.QtWidgets import QToolTip,QLabel
from PyQt6.QtWidgets import (
    QSplitter,
    QMainWindow,
    QInputDialog,
    QDockWidget,
    QTreeView,
    QFileDialog,
    QSplashScreen,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QStatusBar,
    QTextEdit
)

from io import StringIO
import contextlib

from . import Lexers
from . import get_started
from . import MenuConfig
from . import additional_prefs
from . import Modules as ModuleFile
from . import PluginDownload
from . import ThemeDownload
from . import WelcomeScreen
from . import config_page
from . import terminal
from .AuraText import CodeEditor
from .TabWidget import TabWidget
from .plugin_interface import Plugin

local_app_data = os.path.join(os.getenv("LocalAppData"), "AuraText")

path_project = open(f"{local_app_data}/data/CPath_Project.txt", "r+")
cpath = path_project.read()

path_file = open(f"{local_app_data}/data/CPath_File.txt", "r+")
cfile = path_file.read()

exp_path = "./实验"

class Sidebar(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFixedWidth(40)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

# noinspection PyUnresolvedReferences
# no inspection for unresolved references as pylance flags inaccurately sometimes
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.local_app_data = local_app_data

        # self._terminal_history = ""

        # COMMENTED OUT CODE FOR FRAMELESS WINDOW. IN DEVELOPMENT
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # theme file
        with open(f"{local_app_data}/data/theme.json", "r") as themes_file:
            self._themes = json.load(themes_file)

        # config file
        with open(f"{local_app_data}/data/config.json", "r") as config_file:
            self._config = json.load(config_file)
            if self._config["show_setup_info"] == "True":
                pass
                # get_started.show_setup_window()

        # terminal history file
        with open(f"{local_app_data}/data/terminal_history.txt", "r+") as thfile:
            self.terminal_history = thfile.readlines()

        # keymap file
        with open(f"{local_app_data}/data/shortcuts.json", "r+") as kmfile:
            self._shortcuts = json.load(kmfile)

        from qt_material import apply_stylesheet

        if self._themes["theming"] == "flat":
            qdarktheme.setup_theme(
                self._themes["theme_type"], custom_colors={"primary": self._themes["theme"]}
            )
        else:
            pass

        self._config["show_setup_info"] = "False"

        # Keymaps
        settings_keymap = self._shortcuts["settings"]
        terminal_keymap = self._shortcuts["terminal"]

        # Shortcuts
        settings_action = self.addAction("settings_trigger")
        settings_action.setShortcut(settings_keymap)
        settings_action.triggered.connect(self.expandSidebar__Settings)

        def splashScreen():
            # Splash Screen
            splash_pix = ""
            current_time = datetime.datetime.now().time()
            sunrise_time = current_time.replace(hour=6, minute=0, second=0, microsecond=0)
            sunset_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)

            # Check which time interval the current time falls into
            if sunrise_time <= current_time < sunrise_time.replace(hour=12):
                splash_pix = QPixmap(f"{local_app_data}/icons/splash_morning.png")
            elif sunrise_time.replace(hour=12) <= current_time < sunset_time:
                splash_pix = QPixmap(f"{local_app_data}/icons/splash_afternoon.png")
            else:
                splash_pix = QPixmap(f"{local_app_data}/icons/splash_night.png")

            splash = QSplashScreen(splash_pix)
            splash.show()
            time.sleep(1)
            splash.hide()

        if self._config["splash"] == "True":
            splashScreen()
        else:
            pass

        self.tab_widget = TabWidget()
        self.current_editor = ""

        if self._config["explorer_default_open"] == "True":
            self.expandSidebar__Explorer()
        else:
            pass

        if cpath == "" or cpath == " ":
            welcome_widget = WelcomeScreen.WelcomeWidget(self)
            self.tab_widget.addTab(welcome_widget, "Welcome")
        else:
            pass

        self.tab_widget.setTabsClosable(True)

        self.md_dock = QDockWidget("Markdown Preview")
        self.mdnew = QDockWidget("Markdown Preview")

        # Sidebar
        
        self.sidebar_main = Sidebar("", self)
        self.sidebar_main.setTitleBarWidget(QWidget())
        self.sidebar_widget = QWidget(self.sidebar_main)
        self.sidebar_widget.setStyleSheet(f"QWidget{{background-color: {self._themes['sidebar_bg']};}}")
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_main.setWidget(self.sidebar_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar_main)

        self.bottom_bar = QStatusBar()
        # self.setStatusBar(self.bottom_bar)

        self.statusbar = Sidebar("", self)
        self.statusbar.setTitleBarWidget(QWidget())
        self.statusbar_widget = QWidget(self.statusbar)
        self.statusbar_widget.setStyleSheet(f"QWidget{{background-color: {self._themes['sidebar_bg']};}}")
        self.statusbar_layout = QVBoxLayout(self.statusbar_widget)
        self.statusbar_layout.addStretch()
        self.statusbar_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        #self.statusbar_layout.setAlign(Qt.AlignmentFlag.AlignHCenter)
        self.statusbar.setWidget(self.statusbar_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.statusbar)

        #SideBarButton=SideBarButton()
        #QToolTip.setPalette(QColor(0, 0, 0, 0))
        explorer_icon = QIcon(f"./auratext/icons/openfile.png")
        self.explorer_button = QPushButton(self)
        self.explorer_button.setToolTip('<font color="blue">打开文件资源管理器</font>')
        self.explorer_button.setIcon(explorer_icon)
        self.explorer_button.setIconSize(QSize(23, 23))
        self.explorer_button.setFixedSize(28, 28)
        self.explorer_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )

        plugin_icon = QIcon(f"./auratext/icons/plug-in.png")
        self.plugin_button = QPushButton(self)
        self.plugin_button.setToolTip('<font color="blue">安装插件</font>')
        self.plugin_button.setIcon(plugin_icon)
        self.plugin_button.setIconSize(QSize(23, 23))
        self.plugin_button.setFixedSize(28, 28)
        self.plugin_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )
#set Run_button
        run_icon=QIcon(f"./auratext/icons/play1.png")
        self.run_button=QPushButton(self)
        self.run_button.setToolTip('<font color="blue">运行程序</font>')
        self.run_button.setIcon(run_icon)
        self.run_button.setIconSize(QSize(23, 23))
        self.run_button.setFixedSize(28, 28)
        self.run_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )
        
#set newfile_button 
        newfile_icon=QIcon(f"./auratext/icons/newfile.png")
        self.newfile_button=QPushButton(self)
        self.newfile_button.setToolTip('<font color="blue">创建新文件</font>')
        self.newfile_button.setIcon(newfile_icon)
        self.newfile_button.setIconSize(QSize(23, 23))
        self.newfile_button.setFixedSize(28, 28)
        self.run_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )
        
#set save_button 
        save_icon=QIcon(f"./auratext/icons/save.png")
        self.save_button=QPushButton(self)
        self.save_button.setToolTip('<font color="blue">保存文件</font>')
        self.save_button.setIcon(save_icon)
        self.save_button.setIconSize(QSize(23, 23))
        self.save_button.setFixedSize(28, 28)
        self.save_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )
       
#set cut_button
        cut_icon=QIcon(f"./auratext/icons/cut.png")
        self.cut_button=QPushButton(self)
        self.cut_button.setToolTip('<font color="blue">剪切选中内容</font>')
        self.cut_button.setIcon(cut_icon)
        self.cut_button.setIconSize(QSize(23, 23))
        self.cut_button.setFixedSize(32, 32)
        self.cut_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )

#set copy_button 
        copy_icon=QIcon(f"./auratext/icons/copy.png")
        self.copy_button=QPushButton(self)
        self.copy_button.setToolTip('<font color="blue">复制</font>')
        self.copy_button.setIcon(copy_icon)
        self.copy_button.setIconSize(QSize(23, 23))
        self.copy_button.setFixedSize(28, 28)
        self.copy_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )
       
#set undo_button
        undo_icon=QIcon(f"./auratext/icons/undo.png")
        self.undo_button=QPushButton(self)
        self.undo_button.setToolTip('<font color="blue">撤消</font>')
        self.undo_button.setIcon(undo_icon)
        self.undo_button.setIconSize(QSize(23, 23))
        self.undo_button.setFixedSize(28, 28)
        self.undo_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )

#set paste_button
        paste_icon=QIcon(f"./auratext/icons/paste.png")
        self.paste_button=QPushButton(self)
        self.paste_button.setToolTip('<font color="blue">粘贴</font>')
        self.paste_button.setIcon(paste_icon)
        self.paste_button.setIconSize(QSize(23, 23))
        self.paste_button.setFixedSize(28, 28)
        self.paste_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )
       
#set reset_button
        reset_icon=QIcon(f"./auratext/icons/reset.png")
        self.reset_button=QPushButton(self)
        self.reset_button.setToolTip('<font color="blue">外部设备连接重置</font>')
        self.reset_button.setIcon(reset_icon)
        self.reset_button.setIconSize(QSize(23, 23))
        self.reset_button.setFixedSize(28, 28)
        self.reset_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )
        
#set link_button 
        link_icon=QIcon(f"./auratext/icons/link.png")
        self.link_button=QPushButton(self)
        self.link_button.setToolTip('<font color="blue">连接外部设备</font>')
        self.link_button.setIcon(link_icon)
        self.link_button.setIconSize(QSize(23, 23))
        self.link_button.setFixedSize(28, 28)
        self.link_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )
       
#set disconnect_button
        disconnect_icon=QIcon(f"./auratext/icons/disconnect.png")
        self.disconnect_button=QPushButton(self)
        self.disconnect_button.setToolTip('<font color="blue">断开外部设备</font>')
        self.disconnect_button.setIcon(disconnect_icon)
        self.disconnect_button.setIconSize(QSize(23, 23))
        self.disconnect_button.setFixedSize(28, 28)
        self.disconnect_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius:10;
                text-align: botton;
            }
            QPushButton:hover {
                background-color: #4e5157;
            }
            """
        )
        
               
        self.sidebar_layout.insertWidget(0, self.explorer_button)
        self.sidebar_layout.insertWidget(1, self.plugin_button)
        self.sidebar_layout.insertWidget(2, self.run_button)
        self.sidebar_layout.insertWidget(3, self.newfile_button)
        self.sidebar_layout.insertWidget(4, self.save_button)
        self.sidebar_layout.insertWidget(5, self.cut_button)
        self.sidebar_layout.insertWidget(6, self.copy_button)
        self.sidebar_layout.insertWidget(7, self.paste_button)
        self.sidebar_layout.insertWidget(8, self.undo_button)
        self.sidebar_layout.insertWidget(9, self.reset_button)
        self.sidebar_layout.insertWidget(10, self.link_button)
        self.sidebar_layout.insertWidget(11, self.disconnect_button)
        
        self.sidebar_layout.addStretch()
        self.statusbar_layout.addStretch()
        self.statusbar_layout.addSpacing(45)

        # Connect the button's clicked signal to the slot
        # self.explorer_button.clicked.connect(self.expandSidebar__Explorer)
        self.explorer_button.clicked.connect(self.expandSidebar__Experiment)
        self.plugin_button.clicked.connect(self.expandSidebar__Plugins)


        self.spliiter = QSplitter(Qt.Orientation.Horizontal,self)
        self.spliiter.addWidget(self.tab_widget)
        self.setCentralWidget(self.spliiter)

        # self.setCentralWidget(self.tab_widget)

        self.editors = []
        self.py_files_path = []

        if self._config["open_last_file"] == "True":
            if cfile != "" or cfile != " ":
                self.open_last_file()
            else:
                pass
        else:
            pass

        self.action_group = QActionGroup(self)
        self.action_group.setExclusive(True)

        self.tab_widget.setStyleSheet("QTabWidget {border: none;}")

        self.tab_widget.currentChanged.connect(self.change_text_editor)
        self.tab_widget.tabCloseRequested.connect(self.remove_editor)
        # self.new_document()
        self.setWindowTitle("工业视觉教学平台")
        self.setWindowIcon(QIcon(f"{local_app_data}/icons/icon.ico"))
        self.configure_menuBar()
        sys.path.append(f"{local_app_data}/plugins")
        self.load_plugins()

        self.console()

        self.showMaximized()

    # def mousePressEvent(self, event):
    #   self.dragPos = event.globalPosition().toPoint()

    # def mouseMoveEvent(self, event):
    # self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
    # self.dragPos = event.globalPosition().toPoint()
    # event.accept()

    def create_editor(self):
        self.text_editor = CodeEditor(self)
        return self.text_editor

    def load_plugins(self):
        self.plugins = []
        plugin_files = [
            f.split(".")[0] for f in os.listdir(f"{local_app_data}/plugins") if f.endswith(".py")
        ]
        print(plugin_files)
        for plugin_file in plugin_files:
            module = importlib.import_module(plugin_file)
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, Plugin) and obj is not Plugin:
                    print("hello")
                    try:
                        print("hi")
                        self.plugins.append(obj(self))
                    except Exception as e:
                        print(e)

    def onPluginDockVisibilityChanged(self, visible):
        if visible:
            self.plugin_button.setIcon(QIcon(f"{local_app_data}/icons/extension_filled.png"))
        else:
            self.plugin_button.setIcon(QIcon(f"{local_app_data}/icons/extension_unfilled.png"))

    def onExplorerDockVisibilityChanged(self, visible):
        if visible:
            self.explorer_button.setIcon(QIcon(f"{local_app_data}/icons/explorer_filled.png"))
        else:
            self.explorer_button.setIcon(QIcon(f"{local_app_data}/icons/explorer_unfilled.png"))

    def treeview_project(self, path):
        self.dock = QDockWidget("Explorer", self)
        self.dock.visibilityChanged.connect(
            lambda visible: self.onExplorerDockVisibilityChanged(visible)
        )
        # dock.setStyleSheet("QDockWidget { background-color: #191a1b; color: white;}")
        self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        tree_view = QTreeView()
        self.model = QFileSystemModel()
        bg = self._themes["sidebar_bg"]
        tree_view.setStyleSheet(
            f"QTreeView {{background-color: {bg}; color: white; border: none; }}"
        )
        tree_view.setModel(self.model)
        tree_view.setRootIndex(self.model.index(path))
        self.model.setRootPath(path)
        self.dock.setWidget(tree_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

        tree_view.setFont(QFont("Consolas"))

        tree_view.setColumnHidden(1, True)  # File type column
        tree_view.setColumnHidden(2, True)  # Size column
        tree_view.setColumnHidden(3, True)  # Date modified column

        tree_view.doubleClicked.connect(self.open_file)

    def expandSidebar__Explorer(self):
        self.dock = QDockWidget("Explorer", self)
        self.dock.setMinimumWidth(200)
        self.dock.visibilityChanged.connect(
            lambda visible: self.onExplorerDockVisibilityChanged(visible)
        )
        self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        tree_view = QTreeView()

        self.model = QFileSystemModel()
        bg = self._themes["sidebar_bg"]
        tree_view.setStyleSheet(
            f"QTreeView {{background-color: {bg}; color: white; border: none; }}"
        )
        tree_view.setModel(self.model)
        tree_view.setRootIndex(self.model.index(cpath))
        self.model.setRootPath(cpath)
        self.dock.setWidget(tree_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

        tree_view.setFont(QFont("Consolas"))

        tree_view.setColumnHidden(1, True)  # File type column
        tree_view.setColumnHidden(2, True)  # Size column
        tree_view.setColumnHidden(3, True)  # Date modified column

        tree_view.doubleClicked.connect(self.open_file)

    def expandSidebar__Experiment(self):
        self.exp_dock = QDockWidget("Experiment", self)
        self.exp_dock.setMinimumWidth(200)
        # self.exp_dock.visibilityChanged.connect(
        #     lambda visible: self.onExplorerDockVisibilityChanged(visible)
        # )
        self.exp_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        tree_view = QTreeView()

        self.model2 = QFileSystemModel()
        bg = self._themes["sidebar_bg"]
        tree_view.setStyleSheet(
            f"QTreeView {{background-color: {bg}; color: white; border: none; }}"
        )
        tree_view.setModel(self.model2)
        full_path = os.path.abspath(exp_path)
        tree_view.setRootIndex(self.model2.index(full_path))
        self.model2.setRootPath(full_path)
        self.exp_dock.setWidget(tree_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.exp_dock)

        tree_view.setFont(QFont("Consolas"))

        tree_view.setColumnHidden(1, True)  # File type column
        tree_view.setColumnHidden(2, True)  # Size column
        tree_view.setColumnHidden(3, True)  # Date modified column

        tree_view.doubleClicked.connect(self.open_file_exp)


    def create_snippet(self):
        ModuleFile.CodeSnippets.snippets_gen(self.current_editor)

    def import_snippet(self):
        ModuleFile.CodeSnippets.snippets_open(self.current_editor)

    def expandSidebar__Settings(self):
        self.settings_dock = QDockWidget("Settings", self)

        self.settings_dock.setStyleSheet("QDockWidget {background-color : #1b1b1b; color : white;}")
        self.settings_dock.setFixedWidth(200)
        self.settings_widget = config_page.ConfigPage(self)
        self.settings_layout = QVBoxLayout(self.settings_widget)
        self.settings_layout.addWidget(self.settings_widget)
        self.settings_dock.setWidget(self.settings_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.settings_dock)
        self.splitDockWidget(self.sidebar_main, self.settings_dock, Qt.Orientation.Horizontal)

    def expandSidebar__Plugins(self):
        self.plugin_dock = QDockWidget("Extensions", self)
        self.theme_dock = QDockWidget("Themes", self)
        background_color = (
            self.plugin_button.palette().color(self.plugin_button.backgroundRole()).name()
        )
        if background_color == "#3574f0":
            self.plugin_dock.destroy()
            self.theme_dock.destroy()
        else:
            self.plugin_dock.visibilityChanged.connect(
                lambda visible: self.onPluginDockVisibilityChanged(visible)
            )
            self.plugin_dock.setMinimumWidth(300)
            self.plugin_widget = PluginDownload.FileDownloader(self)
            self.plugin_layout = QVBoxLayout()
            self.plugin_layout.addStretch(1)
            self.plugin_layout.addWidget(self.plugin_widget)
            self.plugin_dock.setWidget(self.plugin_widget)

            self.theme_widget = ThemeDownload.ThemeDownloader(self)
            self.theme_layout = QVBoxLayout()
            self.theme_layout.addStretch(1)
            self.theme_layout.addWidget(self.theme_widget)
            self.theme_dock.setWidget(self.theme_widget)

            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.plugin_dock)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.theme_dock)
            self.tabifyDockWidget(self.theme_dock, self.plugin_dock)

    def new_project(self):
        new_folder_path = filedialog.askdirectory(
            title="Create New Folder", initialdir="./", mustexist=False
        )
        with open(f"{self.local_app_data}/data/CPath_Project.txt", "w") as file:
            file.write(new_folder_path)

    # def code_jokes(self):
    #     a = pyjokes.get_joke(language="en", category="neutral")
    #     QMessageBox.information(self, "A Byte of Humour!", a)

    def terminal_widget(self):
        self.terminal_dock = QDockWidget("Terminal", self)
        terminal_widget = terminal.AuraTextTerminalWidget(self)
        # self.sidebar_layout_Terminal = QVBoxLayout(terminal_widget)
        self.terminal_dock.setWidget(terminal_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)

    def python_console(self):
        self.console_dock = QDockWidget("Python Console", self)
        console_widget = PythonConsole()
        console_widget.eval_in_thread()
        # self.sidebar_layout_Terminal = QVBoxLayout()
        self.console_dock.setWidget(console_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)

    def console(self):
        self.result_dock = QDockWidget("控制台", self)
        # console_widget = PythonConsole()
        # console_widget.eval_in_thread()
        self.result_widget = QTextEdit()
        self.result_widget.setReadOnly(True)
        self.result_widget.setFont(QFont(self._themes["font"]))
        # self.sidebar_layout_Terminal = QVBoxLayout()
        self.result_dock.setWidget(self.result_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.result_dock)

    def closeEvent(self, event):
        # reply = QMessageBox.question(
        #     self,
        #     "Save File",
        #     random.choice(ModuleFile.emsg_save_list),
        #     QMessageBox.StandardButton.Save
        #     | QMessageBox.StandardButton.Discard
        #     | QMessageBox.StandardButton.Cancel,
        #     QMessageBox.StandardButton.Save,
        # )
        # if reply == QMessageBox.StandardButton.Save:
        #     self.save_document()
        #     event.accept()
        # elif reply == QMessageBox.StandardButton.Discard:
        #     event.accept()
        # else:
        #     event.ignore()
        pass

    def showMsg(self,msg):
        messagebox = QMessageBox()
        messagebox.setWindowTitle("Path Error"), messagebox.setText(
            msg
        )
        messagebox.exec()

    def gitClone(self):
        try:
            from git import Repo

            repo_url, ok = QInputDialog.getText(self, "Git Repo", "URL of the Repository")
            try:
                path = filedialog.askdirectory(title="Repo Path", initialdir="./", mustexist=False)
            except:
                messagebox = QMessageBox()
                messagebox.setWindowTitle("Path Error"), messagebox.setText(
                    "The folder should be EMPTY! Please try again with an EMPTY folder"
                )
                messagebox.exec()

            try:
                Repo.clone_from(repo_url, path)
                with open(f"{self.local_app_data}/data/CPath_Project.txt", "w") as file:
                    file.write(path)
                messagebox = QMessageBox()
                messagebox.setWindowTitle("Success!"), messagebox.setText(
                    "The repository has been cloned successfully!"
                )
                messagebox.exec()
                self.treeview_project(path)
            except git.GitCommandError:
                pass

        except ImportError:
            messagebox = QMessageBox()
            messagebox.setWindowTitle("Git Import Error"), messagebox.setText(
                "Aura Text can't find Git in your PC. Make sure Git is installed and has been added to PATH."
            )
            messagebox.exec()

    def markdown_open(self, path_data):
        ModuleFile.markdown_open(self, path_data)

    def markdown_new(self):
        ModuleFile.markdown_new(self)

    def open_file(self, index):
        path = self.model.filePath(index)
        image_extensions = ["png", "jpg", "jpeg", "ico", "gif", "bmp"]
        ext = path.split(".")[-1]

        def add_image_tab():
            ModuleFile.add_image_tab(self, self.tab_widget, path, os.path.basename(path))

        if path:
            try:
                if ext in image_extensions:
                    add_image_tab()
                    return

            except UnicodeDecodeError:
                messagebox = QMessageBox()
                messagebox.setWindowTitle("Wrong Filetype!"), messagebox.setText(
                    "This file type is not supported!"
                )
                messagebox.exec()

            try:
                f = open(path, "r")
                try:
                    filedata = f.read()
                    self.new_document(title=os.path.basename(path))
                    self.current_editor.insert(filedata)
                    if ext.lower() == "md":
                        self.markdown_open(filedata)
                    elif ext.lower() == "png":
                        add_image_tab()
                    f.close()

                except UnicodeDecodeError:
                    messagebox = QMessageBox()
                    messagebox.setWindowTitle("Wrong Filetype!"), messagebox.setText(
                        "This file type is not supported!"
                    )
                    messagebox.exec()
            except FileNotFoundError:
                return

    def open_file_exp(self, index):
        path = self.model2.filePath(index)
        image_extensions = ["png", "jpg", "jpeg", "ico", "gif", "bmp"]
        ext = path.split(".")[-1]


        # print("zzz",ext)

        def detect_encoding(file_path):
            with open(file_path, 'r',encoding='utf-8') as f:
                rawdata = f.read()
                result = chardet.detect(rawdata)
                encoding = result['encoding']
                confidence = result['confidence']
                return encoding

        def add_image_tab():
            ModuleFile.add_image_tab(self, self.tab_widget, path, os.path.basename(path))

        def add_pdf_tab():
            ModuleFile.add_pdf_tab(self, self.tab_widget, path, os.path.basename(path))

        def add_pdf_dock():

            ModuleFile.add_pdf_dock(self,path,self.tab_widget)

        if path:
            try:
                if ext in image_extensions:
                    add_image_tab()
                    return

            except UnicodeDecodeError:
                messagebox = QMessageBox()
                messagebox.setWindowTitle("Wrong Filetype!"), messagebox.setText(
                    "This file type is not supported!"
                )
                messagebox.exec()

            try:
                if ext == "pdf":
                    add_pdf_tab()
                    # add_pdf_dock()
                    return


            except Exception as e:
                print(e)
                print("Exception in opening pdf file")


            try:
                # encoding = detect_encoding(path)


                f = open(path, "r",encoding='utf-8')

                try:
                    filedata = f.read()
                    self.new_document2(path,title=os.path.basename(path))
                    self.current_editor.insert(filedata)
                    if ext.lower() == "md":
                        self.markdown_open(filedata)
                    elif ext.lower() == "png":
                        add_image_tab()
                    f.close()

                except UnicodeDecodeError:
                    messagebox = QMessageBox()
                    messagebox.setWindowTitle("Wrong Filetype!"), messagebox.setText(
                        "This file type is not supported!"
                    )
                    messagebox.exec()
            except FileNotFoundError:
                return


    def configure_menuBar(self):
        MenuConfig.configure_menuBar(self)

    def python(self):
        Lexers.python(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def csharp(self):
        Lexers.csharp(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def json(self):
        Lexers.json(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def duplicate_line(self):
        ModuleFile.duplicate_line(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def yaml(self):
        Lexers.yaml(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def xml(self):
        Lexers.xml(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def html(self):
        Lexers.html(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def toggle_read_only(self):
        self.current_editor.setReadOnly(True)
        # self.read_only_button.setIcon(self.read_only_icon)

    def read_only_reset(self):
        self.current_editor.setReadOnly(False)
        # @self.read_only_button.setIcon(self.write_button_icon)

    def cpp(self):
        Lexers.cpp(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def ruby(self):
        Lexers.ruby(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def perl(self):
        Lexers.perl(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def pascal(self):
        Lexers.pascal(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def css(self):
        Lexers.css(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def sql(self):
        Lexers.sql(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def lua(self):
        Lexers.lua(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def cmake(self):
        Lexers.cmake(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def postscript(self):
        Lexers.postscript(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def asm(self):
        Lexers.asm(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def avs(self):
        Lexers.avs(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def coffeescript(self):
        Lexers.coffeescript(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def batch(self):
        Lexers.bat(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def bash(self):
        Lexers.bash(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def srec(self):
        Lexers.srec(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def idl(self):
        Lexers.idl(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def matlab(self):
        Lexers.matlab(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def tcl(self):
        Lexers.tcl(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def verilog(self):
        Lexers.verilog(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def spice(self):
        Lexers.spice(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def vhdl(self):
        Lexers.vhdl(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def octave(self):
        Lexers.octave(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def fortran77(self):
        Lexers.fortran77(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def tex(self):
        Lexers.tex(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def makefile(self):
        Lexers.makefile(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def markdown(self):
        Lexers.markdown(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def js(self):
        Lexers.js(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def fortran(self):
        Lexers.fortran(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def java(self):
        Lexers.java(self)
        self.current_editor.setMarginsBackgroundColor(QColor(self._themes["margin_theme"]))
        self.current_editor.setMarginsForegroundColor(QColor("#FFFFFF"))

    def pastebin(self):
        ModuleFile.pastebin(self)

    def code_formatting(self):
        ModuleFile.code_formatting(self)

    def goto_line(self):
        line_number, ok = QInputDialog.getInt(self, "Goto Line", "Line:")
        if ok:
            self.setCursorPosition(line_number - 1, 0)

    def import_theme(self):
        theme_open = filedialog.askopenfilename(title="Open JSON File", defaultextension='.json',
                                                filetypes=[('JSON file', '*.json')])
        theme_path = os.path.abspath(theme_open)

        import shutil

        shutil.copyfile(theme_path, f'{local_app_data}/data/theme.json')  # copy src to dst

    def open_project(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dialog.exec():
            project_path = dialog.selectedFiles()[0]
            pathh = str(project_path)
            with open(f"{self.local_app_data}/data/CPath_Project.txt", "w") as file:
                file.write(pathh)
            messagebox = QMessageBox()
            messagebox.setWindowTitle("New Project"), messagebox.setText(
                f"New project created at {project_path}"
            )
            messagebox.exec()
            self.treeview_project(project_path)

    def open_project_as_treeview(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dialog.exec():
            project_path = dialog.selectedFiles()[0]
            self.treeview_project(project_path)

    def additional_prefs(self):
        settings = additional_prefs.SettingsWindow()
        settings.exec()

    def new_document(self, checked=False, title="Scratch 1"):
        self.current_editor = self.create_editor()
        self.load_plugins()

        self.editors.append(self.current_editor)
        self.tab_widget.addTab(self.current_editor, title)
        self.tab_widget.setCurrentWidget(self.current_editor)

    def new_document2(self, path, checked=False, title="Scratch 1"):
        self.current_editor = self.create_editor()
        self.load_plugins()

        self.editors.append(self.current_editor)
        self.tab_widget.addTab(self.current_editor, title)
        self.tab_widget.setCurrentWidget(self.current_editor)
        self.py_files_path.append(path)

    def custom_new_document(self, title, checked=False):
        self.current_editor = self.create_editor()
        self.editors.append(self.current_editor)
        self.tab_widget.addTab(self.current_editor, title)
        self.tab_widget.setCurrentWidget(self.current_editor)

    def cs_new_document(self, checked=False):
        text, ok = QInputDialog.getText(None, "New File", "Filename:")
        if text != "":
            ext = text.split(".")[-1]
            self.current_editor = self.create_editor()
            self.editors.append(self.current_editor)
            self.tab_widget.addTab(self.current_editor, text)
            self.load_plugins()
            if os.path.isfile(f"{local_app_data}/plugins/Markdown.py"):
                self.markdown_new()
            else:
                pass
            self.tab_widget.setCurrentWidget(self.current_editor)
        else:
            pass

    def change_text_editor(self, index):
        if index < len(self.editors):
            # Set the previous editor as read-only
            if self.current_editor:
                self.current_editor.setReadOnly(True)

            self.current_editor = self.editors[index]

            self.current_editor.setReadOnly(False)

    def undo_document(self):
        self.current_editor.undo()

    def notes(self):
        note_dock = QDockWidget("Notes", self)
        terminal_widget = QPlainTextEdit(note_dock)
        terminal_widget.setFont(QFont(self._themes["font"]))
        note_dock.setWidget(terminal_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, note_dock)
        note_dock.show()

    def redo_document(self):
        self.current_editor.redo()

    def cut_document(self):
        self.current_editor.cut()

    def copy_document(self):
        self.current_editor.copy()

    def summary(self):
        lines = str(self.current_editor.lines())
        text = self.current_editor.text()
        text = "Number of Lines: " + lines
        messagebox = QMessageBox()
        messagebox.setText(text), messagebox.setWindowTitle("Summary")
        messagebox.exec()

    def paste_document(self):
        self.current_editor.paste()


    def save_py_file(self,index=None):
        def save_file(path,content):
            with open(path,'w',encoding='utf-8') as file:
                file.write(content)
        if index==None :
            index = self.tab_widget.currentIndex()
        save_file(self.py_files_path[index],self.current_editor.text())


    def remove_editor(self, index):
        self.tab_widget.removeTab(index)
        self.save_py_file(index)
        if index < len(self.editors):
            del self.editors[index]
            del self.py_files_path[index]


    def open_document(self):
        a = ModuleFile.open_document(self)
        self.load_plugins()

    def open_last_file(self, title=os.path.basename(cfile)):
        try:
            file = open(cfile, "r+")
            self.current_editor = self.create_editor()
            text = file.read()
            self.editors.append(self.current_editor)
            self.current_editor.setText(text)
            self.tab_widget.addTab(self.current_editor, title)
            self.tab_widget.setCurrentWidget(self.current_editor)
        except FileNotFoundError and OSError:
            pass

    def save_document(self):
        ModuleFile.save_document(self)

    @staticmethod
    def about_github():
        webbrowser.open_new_tab("https://github.com/rohankishore/Aura-Notes")

    @staticmethod
    def version():
        text_var = ("工业视觉教学平台 v1.0")
        msg_box = QMessageBox()
        msg_box.setWindowTitle("关于")
        msg_box.setText(text_ver)
        msg_box.exec()

    @staticmethod
    def getting_started():
        webbrowser.open_new_tab("https://github.com/rohankishore/Aura-Text/wiki")

    @staticmethod
    def buymeacoffee():
        webbrowser.open_new_tab("https://www.buymeacoffee.com/auratext")

    def fullscreen(self):
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            self.showMaximized()

    @staticmethod
    def bug_report():
        webbrowser.open_new_tab("https://github.com/rohankishore/Aura-Text/issues/new/choose")

    @staticmethod
    def discord():
        webbrowser.open_new_tab("https://discord.gg/4PJfTugn")


    def run_code(self):
        # print("run code")
        if hasattr(self,"text_editor") and self.text_editor!=None:
            # self.text_editor.run_code()
            # result = self.text_editor.result
            code = self.text_editor.text()
            # a = 1
            output_stream = StringIO()

            with contextlib.redirect_stdout(output_stream):
                try:
                    basepath = os.path.dirname(self.py_files_path[self.tab_widget.currentIndex()])
                    os.chdir(basepath)
                    exec(code)
                    # exe_path = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe"

                    # self.showMsg(exe_path+" \""+ self.py_files_path[self.tab_widget.currentIndex()]+"\"")

                    # result = subprocess.run(exe_path+" \""+ self.py_files_path[self.tab_widget.currentIndex()]+"\"")
                except Exception as e:
                    print(e)

            output = output_stream.getvalue()
            # output = result.stdout.decode()
            self.result_widget.setPlainText(output)
