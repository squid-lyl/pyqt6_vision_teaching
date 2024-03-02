from PyQt6.QtWidgets import QMainWindow, QPushButton, QFileDialog,QApplication
import json


# 定义一个类，继承自QMainWindow
class ApplyTheme(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle("File Replace App")

        # 创建一个按钮，并设置其位置和大小
        self.button = QPushButton("Replace JSON File", self)
        self.button.setGeometry(50, 50, 200, 30)
        # 将按钮的点击事件与replace_file_contents函数连接
        self.button.clicked.connect(self.replace_file_contents)

    # 定义一个函数，用于替换文件内容
    def replace_file_contents(self):
        # 创建一个文件对话框
        file_dialog = QFileDialog()
        # 获取用户选择的文件路径和文件类型
        file_path, _ = file_dialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")

        # 如果用户选择了文件
        if file_path:
            # 定义一个新的字典，用于替换文件内容
            new_contents = {
                "message": "This content has been replaced."
            }

            try:
                # 以写入模式打开文件
                with open(file_path, "w") as json_file:
                    # 将新字典的内容写入文件
                    json.dump(new_contents, json_file, indent=4)
                # 打印成功信息
                print("File contents replaced successfully.")
            except Exception as e:
                # 打印错误信息
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    import sys

    # 创建一个应用程序对象
    app = QApplication(sys.argv)

    # 创建一个窗口对象
    window = ApplyTheme()
    # 显示窗口
    window.show()

    # 进入应用程序事件循环
    sys.exit(app.exec())