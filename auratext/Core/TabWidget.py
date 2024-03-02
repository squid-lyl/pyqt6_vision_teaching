from PyQt6.QtCore import QMimeData, QPoint, Qt
from PyQt6.QtGui import QCursor, QDrag, QPixmap, QRegion, QAction
from PyQt6.QtWidgets import QTabWidget, QMenu

class TabWidget(QTabWidget):
    # 初始化函数
    def __init__(self, parent=None, new=None):
        # 调用父类的初始化函数
        super().__init__(parent)
        # 设置接受拖入事件
        self.setAcceptDrops(True)
        # 设置鼠标跟踪
        self.tabBar().setMouseTracking(True)
        # 设置可移动
        self.setMovable(True)
        # 设置文档模式
        self.setDocumentMode(True)
        # 如果new为True，则调用setup函数
        if new:
            TabWidget.setup(self)

    # 设置状态函数
    def __setstate__(self, data):
        # 调用自身的初始化函数
        self.__init__(new=False)
        # 设置父窗口
        self.setParent(data["parent"])
        # 遍历data中的tabs，添加标签页
        for widget, tabname in data["tabs"]:
            self.addTab(widget, tabname)
        # 调用setup函数
        TabWidget.setup(self)

    # 获取状态函数
    def __getstate__(self):
        # 创建data字典
        data = {
            "parent": self.parent(),
            "tabs": [],
        }
        # 创建tab_list列表
        tab_list = data["tabs"]
        # 遍历标签页，添加到tab_list
        for k in range(self.count()):
            tab_name = self.tabText(k)
            widget = self.widget(k)
            tab_list.append((widget, tab_name))
        # 返回data
        return data

    # 设置函数
    def setup(self):
        pass

    # 鼠标移动事件
    def mouseMoveEvent(self, e):
        # 获取全局坐标
        globalPos = self.mapToGlobal(e.pos())
        # 获取标签栏
        tabBar = self.tabBar()
        # 获取标签栏中的坐标
        posInTab = tabBar.mapFromGlobal(globalPos)
        # 获取标签页索引
        index = tabBar.tabAt(e.pos())
        # 获取标签页矩形
        tabRect = tabBar.tabRect(index)

        # 创建QPixmap
        pixmap = QPixmap(tabRect.size())
        # 渲染标签页
        tabBar.render(pixmap, QPoint(), QRegion(tabRect))
        # 创建QMimeData
        mimeData = QMimeData()

    # 上下文菜单事件
    def contextMenuEvent(self, event):
        # 创建QMenu
        menu = QMenu(self)
        # 创建关闭所有标签页的QAction
        close_alltabs = QAction("Close All Tabs", self)

        # 连接信号和槽
        close_alltabs.triggered.connect(self.close_all_tabs)

        # 添加QAction到QMenu
        menu.addAction(close_alltabs)

        # 执行QMenu
        menu.exec(event.globalPos())

    # 关闭所有标签页函数
    def close_all_tabs(self):
        # 清空标签页
        self.clear()