import json
import os
import sys,logging
import matplotlib
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from auratext.Core.window import Window
from auratext.Core import get_started

""" 
This file includes the code to run the app. It also scans if the app is being opened for the first time in order to show the
setup instructions.
"""

# local_app_data = os.path.join(os.getenv("LocalAppData"), "AuraText")
local_app_data = './auratext'
if not os.path.exists(local_app_data):
    os.mkdir(local_app_data)
if not os.path.exists(f"{local_app_data}/data"):
    os.mkdir(f"{local_app_data}/data")

with open(f"{local_app_data}/data/config.json", "w") as config_file:
    _config = {"first_time_open": True}
    json.dump(_config, config_file)

with open(f"{local_app_data}/data/theme.json", "r") as config_file:
    _theme = json.load(config_file)


def main():
    app = QApplication(sys.argv)
    if _theme["theming"] == "material":
        theme = _theme["material_type"] + ".xml"
        apply_stylesheet(app, theme=theme)
    #logging.info("进入主事件循环")
    ex = Window()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sys.exit(app.exec())
    #logging.info("主事件循环结束")

if __name__ == "__main__":
    main()
