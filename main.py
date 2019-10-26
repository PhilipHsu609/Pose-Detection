from PyQt5 import QtWidgets
from src.main_window import MainUi
import sys


def run_app():
    app = QtWidgets.QApplication(sys.argv)
    window = MainUi()
    window.show()
    app.exec_()


if __name__ == "__main__":
    run_app()
