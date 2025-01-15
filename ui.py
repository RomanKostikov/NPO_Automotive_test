from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout, QMessageBox,
    QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtCore import QTimer, Qt


class ResourceMonitorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мониторинг ресурсов")
        self.setGeometry(100, 100, 400, 300)

        # UI Elements
        self.cpu_label = QLabel("ЦП: --%")
        self.ram_label = QLabel("ОЗУ: --% свободно/--% всего")
        self.disk_label = QLabel("ПЗУ: --% свободно/--% всего")

        self.update_interval_label = QLabel("Интервал обновления (мс):")
        self.update_interval_input = QLineEdit()
        self.update_interval_input.setPlaceholderText("Введите интервал (мс)")
        self.apply_button = QPushButton("Применить")

        self.start_button = QPushButton("Начать запись")
        self.history_button = QPushButton("Просмотр истории")
        self.timer_label = QLabel("Время записи: 00:00")

        # Layouts
        resource_layout = QVBoxLayout()
        resource_layout.addWidget(self.cpu_label)
        resource_layout.addWidget(self.ram_label)
        resource_layout.addWidget(self.disk_label)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(self.update_interval_label)
        interval_layout.addWidget(self.update_interval_input)
        interval_layout.addWidget(self.apply_button)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.history_button)
        button_layout.addWidget(self.timer_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(resource_layout)
        main_layout.addLayout(interval_layout)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def display_history(self, records):
        """Отображает записи в отдельном окне."""
        if not records:
            QMessageBox.information(self, "История", "Нет записей для отображения.")
            return

        # Сохраняем окно как атрибут класса
        self.history_window = QWidget()
        self.history_window.setWindowTitle("История записей")

        # Создаем таблицу
        table = QTableWidget(len(records), 5)
        table.setHorizontalHeaderLabels(["ID", "ЦП (%)", "ОЗУ (ГБ)", "ПЗУ (ГБ)", "Время"])
        for i, row in enumerate(records):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(val) if val is not None else ""))

        # Добавляем таблицу в окно
        layout = QVBoxLayout()
        layout.addWidget(table)
        self.history_window.setLayout(layout)

        # Показываем окно
        self.history_window.setAttribute(Qt.WA_DeleteOnClose)  # Удаляем окно после закрытия
        self.history_window.show()
