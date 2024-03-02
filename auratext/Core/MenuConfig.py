import importlib
import json
import os
import sys

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from .plugin_interface import MenuPluginInterface

local_app_data = os.path.join(os.getenv("LocalAppData"), "AuraText")
with open(f"{local_app_data}/data/theme.json", "r") as themes_file:
    _themes = json.load(themes_file)


# noinspection PyArgumentList
def configure_menuBar(self):
    menubar = self.menuBar()

    self.setMenuBar(menubar)
    self.setStyleSheet(
        f"""
QMenuBar {{
    background-color: {_themes["menubar_bg"]};
}}

QMenuBar::item {{
    background-color: {_themes["menubar_bg"]};
    color: rgb(255, 255, 255);
}}

QMenuBar::item::selected {{
    background-color: #1b1b1b;
}}

QMenu {{
    background-color: rgb(49, 49, 49);
    color: rgb(255, 255, 255);
    border: 0px solid #000;
}}

QMenu::item::selected {{
    background-color: rgb(30, 30, 30);
}}
"""
    )

    whats_this_action = QAction(self)
    whats_this_action.setShortcut("Shift+F1")
    menubar.addAction(whats_this_action)

    file_menu = QMenu("文件", self)
    file_menu.addAction("新建", self.cs_new_document).setWhatsThis("Create a New File")
    file_menu.addAction("打开", self.open_document).setWhatsThis("Open an existing file")
    file_menu.addSeparator()
    file_menu.addAction("新建项目", self.new_project).setWhatsThis("Create a new project")
    file_menu.addAction("打开项目", self.open_project).setWhatsThis("Open an existing project")
    file_menu.addAction("Open Project as Treeview", self.open_project_as_treeview).setWhatsThis(
        "Open an existing project as a treeview dock"
    )

    # git_menu = QMenu("&Git", self)
    # git_menu.addAction("Clone Project from Git", self.gitClone)
    # file_menu.addMenu(git_menu)
    # file_menu.addSeparator()

    file_menu.addAction("保存",self.save_py_file).setWhatsThis("Save the document")
    file_menu.addAction("另存为", self.save_document).setWhatsThis("Save the document as")
    file_menu.addSeparator()
    file_menu.addAction("概览", self.summary).setWhatsThis(
        "Get basic info of a file (Eg: Number of lines)"
    )
    file_menu.addSeparator()
    file_menu.addAction("设置", self.expandSidebar__Settings)
    file_menu.addAction("退出", sys.exit).setWhatsThis("Exit Aura Text")
    menubar.addMenu(file_menu)

    whats_this_action.setWhatsThis("Click on a menu item to see its help text")
    whats_this_action.setShortcut("Shift+F1")

    edit_menu = QMenu("编辑", self)
    edit_menu.addAction("剪切", self.cut_document).setWhatsThis("Cut selected text")
    edit_menu.addAction("复制", self.copy_document).setWhatsThis("Copy selected text")
    edit_menu.addAction("粘贴", self.paste_document).setWhatsThis("Paste selected text")
    edit_menu.addAction("撤销", self.undo_document).setWhatsThis("Undo last edit")
    edit_menu.addAction("重做", self.redo_document).setWhatsThis("Redo last edit")
    edit_menu.addSeparator()
    # edit_menu.addAction("Duplicate Line", self.duplicate_line).setWhatsThis("Duplicate a line to another line")
    # edit_menu.addAction("Reverse Line",).setWhatsThis("Reverse the alphabets of a line (Eg: Hello -->  olleH")
    # edit_menu.addSeparator()
    # edit_menu.addAction("Find & Replace", self.find_replace).setWhatsThis("Find a specific word inside the editor")
    menubar.addMenu(edit_menu)




    view_menu = QMenu("视图", self)
    view_menu.addAction("全屏", self.fullscreen).setWhatsThis("Makes the window full screen")
    view_menu.addAction("项目目录", self.expandSidebar__Explorer).setWhatsThis(
        "Shows the files and folder in your project as treeview"
    )
    view_menu.addSeparator()
    view_menu.addAction("终端", self.terminal_widget)
    view_menu.addAction("Python控制台", self.python_console)

    run_menu = QMenu("运行", self)
    run_menu.addAction("运行程序", self.run_code).setWhatsThis("Run")
    # edit_menu.addAction("Duplicate Line", self.duplicate_line).setWhatsThis("Duplicate a line to another line")
    # edit_menu.addAction("Reverse Line",).setWhatsThis("Reverse the alphabets of a line (Eg: Hello -->  olleH")
    # edit_menu.addSeparator()
    # edit_menu.addAction("Find & Replace", self.find_replace).setWhatsThis("Find a specific word inside the editor")
    menubar.addMenu(run_menu)

    def read_only():
        if toggle_read_only_action.isChecked():
            self.toggle_read_only()
        else:
            self.read_only_reset()

    toggle_read_only_action = QAction("Read-Only", self)
    toggle_read_only_action.setCheckable(True)
    toggle_read_only_action.triggered.connect(read_only)
    view_menu.addAction(toggle_read_only_action)
    # menubar.addMenu(view_menu)R

    code_menu = QMenu("代码", self)
    snippet_menu = QMenu("代码片段", self)
    snippet_menu.addAction("从所选内容创建代码段", self.create_snippet)
    snippet_menu.addAction("导入代码片段", self.import_snippet)
    code_menu.addAction("代码格式化", self.code_formatting).setWhatsThis(
        "Beautifies and Formats the code in your current tab with pep-8 standard"
    )
    code_menu.addMenu(snippet_menu)
    # menubar.addMenu(code_menu)

    tools_menu = QMenu("工具", self)

    tools_menu.addAction("上传数据", self.pastebin).setWhatsThis(
        "Uploads the entire text content in your current editor to Pastebin and automatically copies the link"
    )
    tools_menu.addAction("节点", self.notes).setWhatsThis(
        "Creates a new dock to write down ideas and temporary stuffs. The contents will be erased if you close the dock or the app"
    )
    #
    device_menu = QMenu("设备", self)
    
    connect_external_device_action = QAction("连接外部设备", self)
    #terminal_action = QAction("打开终端", self)
    video_tools_action = QAction("视频工具", self)
    connect_settings_action = QAction("连接设置", self)

    device_menu.addAction(connect_external_device_action)
    #device_menu.addAction(terminal_action)
    device_menu.addAction(video_tools_action)
    device_menu.addAction(connect_settings_action)

    menubar.addMenu(device_menu)
    # menubar.addMenu(tools_menu)

    prefernces_menu = QMenu("偏好设置", self)
    # language_menu = QMenu("&Languages", prefernces_menu)
    # a_menu = QMenu("&A", language_menu)
    # b_menu = QMenu("&B", language_menu)
    # c_menu = QMenu("&C", language_menu)
    # d_menu = QMenu("&D", language_menu)
    # e_menu = QMenu("&E", language_menu)
    # f_menu = QMenu("&F", language_menu)
    # g_menu = QMenu("&G", language_menu)
    # h_menu = QMenu("&H", language_menu)
    # i_menu = QMenu("&I", language_menu)
    # j_menu = QMenu("&J", language_menu)
    # k_menu = QMenu("&K", language_menu)
    # l_menu = QMenu("&L", language_menu)
    # m_menu = QMenu("&M", language_menu)
    # n_menu = QMenu("&N", language_menu)
    # o_menu = QMenu("&O", language_menu)
    # p_menu = QMenu("&P", language_menu)
    # q_menu = QMenu("&Q", language_menu)
    # r_menu = QMenu("&R", language_menu)
    # s_menu = QMenu("&S", language_menu)
    # t_menu = QMenu("&T", language_menu)
    # u_menu = QMenu("&U", language_menu)
    # v_menu = QMenu("&V", language_menu)
    # w_menu = QMenu("&W", language_menu)
    # x_menu = QMenu("&X", language_menu)
    # y_menu = QMenu("&Y", language_menu)
    # z_menu = QMenu("&Z", language_menu)

    action_py = QAction("Python", self, checkable=True)
    action_py.triggered.connect(self.python)
    self.action_group.addAction(action_py)

    action_cpp = QAction("C++", self, checkable=True)
    action_cpp.triggered.connect(self.cpp)
    self.action_group.addAction(action_cpp)

    action_java = QAction("Java", self, checkable=True)
    action_java.triggered.connect(self.java)
    self.action_group.addAction(action_java)

    action_fortran = QAction("Fortran", self, checkable=True)
    action_fortran.triggered.connect(self.fortran)
    self.action_group.addAction(action_fortran)

    action_js = QAction("JavaScript", self, checkable=True)
    action_js.triggered.connect(self.js)
    self.action_group.addAction(action_js)
    action_py.setChecked(True)

    action_bash = QAction("Bash", self, checkable=True)
    action_js.triggered.connect(self.bash)
    self.action_group.addAction(action_bash)

    action_csharp = QAction("C#", self, checkable=True)
    action_csharp.triggered.connect(self.csharp)
    self.action_group.addAction(action_csharp)
    action_py.setChecked(True)

    action_ruby = QAction("Ruby", self, checkable=True)
    action_ruby.triggered.connect(self.ruby)
    self.action_group.addAction(action_ruby)

    action_pascal = QAction("Pascal", self, checkable=True)
    action_pascal.triggered.connect(self.pascal)
    self.action_group.addAction(action_pascal)

    action_perl = QAction("Perl", self, checkable=True)
    action_perl.triggered.connect(self.perl)
    self.action_group.addAction(action_perl)

    action_mk = QAction("MakeFile", self, checkable=True)
    action_mk.triggered.connect(self.makefile)
    self.action_group.addAction(action_mk)

    action_md = QAction("Markdown", self, checkable=True)
    action_md.triggered.connect(self.markdown)
    self.action_group.addAction(action_md)

    action_html = QAction("HTML", self, checkable=True)
    action_html.triggered.connect(self.html)
    self.action_group.addAction(action_html)

    action_yaml = QAction("YAML", self, checkable=True)
    action_yaml.triggered.connect(self.yaml)
    self.action_group.addAction(action_yaml)

    action_json = QAction("JSON", self, checkable=True)
    action_json.triggered.connect(self.json)
    self.action_group.addAction(action_json)

    action_css = QAction("CSS", self, checkable=True)
    action_css.triggered.connect(self.css)
    self.action_group.addAction(action_css)

    action_batch = QAction("Batch", self, checkable=True)
    action_css.triggered.connect(self.batch)
    self.action_group.addAction(action_batch)

    action_avs = QAction("AVS", self, checkable=True)
    action_css.triggered.connect(self.avs)
    self.action_group.addAction(action_avs)

    action_asm = QAction("ASM", self, checkable=True)
    action_css.triggered.connect(self.asm)
    self.action_group.addAction(action_asm)

    action_cmake = QAction("CMake", self, checkable=True)
    action_css.triggered.connect(self.cmake)
    self.action_group.addAction(action_cmake)

    action_postscript = QAction("PostScript", self, checkable=True)
    action_css.triggered.connect(self.postscript)
    self.action_group.addAction(action_postscript)

    action_coffeescript = QAction("CoffeeScript", self, checkable=True)
    action_css.triggered.connect(self.coffeescript)
    self.action_group.addAction(action_coffeescript)

    action_srec = QAction("SREC", self, checkable=True)
    action_css.triggered.connect(self.coffeescript)
    self.action_group.addAction(action_coffeescript)

    action_sql = QAction("SQL", self, checkable=True)
    action_sql.triggered.connect(self.sql)
    self.action_group.addAction(action_sql)

    action_lua = QAction("Lua", self, checkable=True)
    action_lua.triggered.connect(self.lua)
    self.action_group.addAction(action_lua)

    action_idl = QAction("IDL", self, checkable=True)
    action_idl.triggered.connect(self.idl)
    self.action_group.addAction(action_idl)

    action_matlab = QAction("MATLAB", self, checkable=True)
    action_matlab.triggered.connect(self.matlab)
    self.action_group.addAction(action_matlab)

    action_spice = QAction("Spice", self, checkable=True)
    action_spice.triggered.connect(self.spice)
    self.action_group.addAction(action_spice)

    action_vhdl = QAction("VHDL", self, checkable=True)
    action_vhdl.triggered.connect(self.vhdl)
    self.action_group.addAction(action_vhdl)

    action_octave = QAction("Octave", self, checkable=True)
    action_octave.triggered.connect(self.octave)
    self.action_group.addAction(action_octave)

    action_fortran77 = QAction("Fortran77", self, checkable=True)
    action_fortran77.triggered.connect(self.fortran77)
    self.action_group.addAction(action_fortran77)

    action_tcl = QAction("Tcl", self, checkable=True)
    action_tcl.triggered.connect(self.tcl)
    self.action_group.addAction(action_tcl)

    # VB action
    action_verilog = QAction("Verilog", self, checkable=True)
    action_verilog.triggered.connect(self.verilog)
    self.action_group.addAction(action_verilog)

    # TeX action
    action_tex = QAction("TeX", self, checkable=True)
    action_tex.triggered.connect(self.tex)
    self.action_group.addAction(action_tex)

    # p menu
    # p_menu.addAction(action_pascal)
    # p_menu.addAction(action_perl)
    # p_menu.addAction(action_postscript)
    # p_menu.addAction(action_py)
    #
    # # h menu
    # h_menu.addAction(action_html)
    #
    # # y menu
    # y_menu.addAction(action_yaml)
    #
    # # r menu
    # r_menu.addAction(action_ruby)
    #
    # # v menu
    # v_menu.addAction(action_verilog)
    # v_menu.addAction(action_vhdl)
    #
    # # m menu
    # m_menu.addAction(action_mk)
    # m_menu.addAction(action_md)
    # m_menu.addAction(action_matlab)
    #
    # # c menu
    # c_menu.addAction(action_cmake)
    # c_menu.addAction(action_coffeescript)
    # c_menu.addAction(action_cpp)
    # c_menu.addAction(action_csharp)
    # c_menu.addAction(action_css)
    #
    # # f menu
    # f_menu.addAction(action_fortran)
    # f_menu.addAction(action_fortran77)
    #
    # # b menu
    # b_menu.addAction(action_bash)
    # b_menu.addAction(action_batch)
    #
    # # j menu
    # j_menu.addAction(action_java)
    # j_menu.addAction(action_js)
    # j_menu.addAction(action_json)
    #
    # # i menu
    # i_menu.addAction(action_idl)
    #
    # # a menu
    # a_menu.addAction(action_asm)
    # a_menu.addAction(action_avs)
    #
    # # s menu
    # s_menu.addAction(action_spice)
    # s_menu.addAction(action_sql)
    # s_menu.addAction(action_srec)
    #
    # # t menu
    # t_menu.addAction(action_tcl)
    # t_menu.addAction(action_tex)
    #
    # # o menu
    # o_menu.addAction(action_octave)
    #
    # # l menu
    # l_menu.addAction(action_lua)
    #
    # language_menu.addMenu(a_menu)
    # language_menu.addMenu(b_menu)
    # language_menu.addMenu(c_menu)
    # # language_menu.addMenu(d_menu)
    # # language_menu.addMenu(e_menu)
    # language_menu.addMenu(f_menu)
    # # language_menu.addMenu(g_menu)
    # language_menu.addMenu(h_menu)
    # language_menu.addMenu(i_menu)
    # language_menu.addMenu(j_menu)
    # # language_menu.addMenu(k_menu)
    # language_menu.addMenu(l_menu)
    # language_menu.addMenu(m_menu)
    # # language_menu.addMenu(n_menu)
    # language_menu.addMenu(o_menu)
    # language_menu.addMenu(p_menu)
    # # language_menu.addMenu(q_menu)
    # language_menu.addMenu(r_menu)
    # language_menu.addMenu(s_menu)
    # language_menu.addMenu(t_menu)
    # # language_menu.addMenu(u_menu)
    # language_menu.addMenu(v_menu)
    # # language_menu.addMenu(w_menu)
    # # language_menu.addMenu(x_menu)
    # language_menu.addMenu(y_menu)
    # # language_menu.addMenu(z_menu)

    # prefernces_menu.addMenu(language_menu)
    prefernces_menu.addAction("其他首选项", self.additional_prefs)
    prefernces_menu.addAction("导入主题", self.import_theme)
    menubar.addMenu(prefernces_menu)

    
    
    help_menu = QMenu("&帮助", self)
    help_menu.addAction("帮助文档", self.getting_started).setWhatsThis(
        "Manuals and tutorials on how to use Aura Text"
    )
    help_menu.addAction("提交错误报告", self.bug_report).setWhatsThis(
        "Submit a bug report if you've faced any bug(s)"
    )
    # help_menu.addAction("A Byte of Humour!", self.code_jokes).setWhatsThis(
    #     "Shows a joke to cheer you up!"
    # )
    help_menu.addSeparator()
    # help_menu.addAction("GitHub", self.about_github).setWhatsThis("GitHub repository")
    # help_menu.addAction(
    #     "Contribute to Aura Text",
    # ).setWhatsThis("For developers who are looking forward to make Aura Text even better")
    # help_menu.addAction("Join Discord Server", self.discord).setWhatsThis(
    #     "Join Aura Text's Discord server"
    # )
    # help_menu.addAction("Buy Me A Coffee", self.buymeacoffee).setWhatsThis(
    #     "Donate to Aura Text developer"
    # )
    help_menu.addAction("关于", self.version).setWhatsThis("Shows current version of Aura Text")
    menubar.addMenu(help_menu)

    # Define a dictionary to map section names to corresponding QMenu instances
    sections = {

        "File": file_menu,
        "Edit": edit_menu,
        "Run":run_menu,
        "View": view_menu,
        "Code": code_menu,
        "Tools": tools_menu,
        "Device":device_menu,
        "Preferences": prefernces_menu,
        "?": help_menu,
    }

    # Load and categorize plugins
    plugin_dir = os.path.abspath(f"{self.local_app_data}/plugins")  # Path to your plugins directory
    if os.path.exists(plugin_dir):
        sys.path.append(plugin_dir)

        for file_name in os.listdir(plugin_dir):
            if file_name.endswith(".py"):
                plugin_module_name = os.path.splitext(file_name)[0]
                try:
                    plugin_module = importlib.import_module(plugin_module_name)
                    for obj_name in dir(plugin_module):
                        obj = getattr(plugin_module, obj_name)
                        if (
                                isinstance(obj, type)
                                and issubclass(obj, MenuPluginInterface)
                                and obj != MenuPluginInterface
                        ):
                            plugin = obj(self.current_editor)
                            section = plugin.section
                            if section in sections:
                                plugin.add_menu_items(sections[section])
                except Exception as e:
                    print(f"Error loading plugin {plugin_module_name}: {e}")

    for section, submenu in sections.items():
        menubar.addMenu(submenu)
