import sys
from PyQt5.QtWidgets import QApplication
from db import DatabaseManager
from logic import ResourceMonitorLogic
from ui import ResourceMonitorUI


def main():
    app = QApplication(sys.argv)

    db = DatabaseManager()
    ui = ResourceMonitorUI()
    logic = ResourceMonitorLogic(db, ui)

    ui.show()
    sys.exit(app.exec_())
    db.close()


if __name__ == "__main__":
    main()
