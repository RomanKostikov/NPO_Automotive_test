import sys
import psutil
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout,
    QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QTimer, Qt


class ResourceMonitorApp(QMainWindow):
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

        # Timer for updating resource usage
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_resource_usage)
        self.timer.start(1000)  # Default interval: 1000 ms (1 second)

        # Database
        self.conn = sqlite3.connect("resources.db")
        self.create_table()

        # Timer for recording duration
        self.record_duration_timer = QTimer()
        self.record_duration_timer.timeout.connect(self.update_record_duration)
        self.record_start_time = None

        # Connect buttons
        self.apply_button.clicked.connect(self.update_timer_interval)
        self.start_button.clicked.connect(self.start_recording)
        self.history_button.clicked.connect(self.show_history)

    def create_table(self):
        """Создаем таблицу для записи данных."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_usage REAL,
                ram_free REAL,
                disk_free REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def update_resource_usage(self):
        """Обновляем показатели ресурсов."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        self.cpu_label.setText(f"ЦП: {cpu}%")
        self.ram_label.setText(
            f"ОЗУ: {ram.available / (1024 ** 3):.2f}ГБ свободно/{ram.total / (1024 ** 3):.2f}ГБ всего")
        self.disk_label.setText(
            f"ПЗУ: {disk.free / (1024 ** 3):.2f}ГБ свободно/{disk.total / (1024 ** 3):.2f}ГБ всего")

    def update_timer_interval(self):
        """Обновляем интервал времени таймера и записи."""
        try:
            interval = int(self.update_interval_input.text())
            if interval < 100:  # Ограничение минимального интервала
                raise ValueError("Интервал должен быть не менее 100 мс.")

            # Обновляем интервал обновления ресурса
            self.timer.setInterval(interval)

            # Если запись активна, обновляем также интервал записи
            if hasattr(self, 'record_timer') and self.record_timer.isActive():
                self.record_timer.setInterval(interval)

            QMessageBox.information(self, "Успешно",
                                    f"Интервал обновления установлен на {interval} мс.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def start_recording(self):
        """Начинаем запись данных в БД."""
        self.start_button.setText("Остановить запись")
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.stop_recording)

        self.record_timer = QTimer()
        # Ставим интервал записи равным текущему интервалу обновления
        self.record_timer.setInterval(self.timer.interval())
        self.record_timer.timeout.connect(self.record_data)
        self.record_timer.start()

        # Инициализируем время записи
        self.record_start_time = 0
        self.record_duration_timer.start(1000)  # Таймер для обновления времени записи

    def stop_recording(self):
        """Останавливаем запись данных."""
        self.record_timer.stop()
        self.record_duration_timer.stop()
        self.timer_label.setText("Время записи: 00:00")  # Сброс таймера на интерфейсе
        self.start_button.setText("Начать запись")
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.start_recording)

    def update_record_duration(self):
        """Обновляем отображение времени записи."""
        if self.record_start_time is not None:  # Проверяем, что запись началась
            self.record_start_time += 1
            minutes, seconds = divmod(self.record_start_time, 60)
            self.timer_label.setText(f"Время записи: {minutes:02}:{seconds:02}")

    def record_data(self):
        """Записываем данные о загрузке в БД."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO records (cpu_usage, ram_free, disk_free) VALUES (?, ?, ?)", (
            cpu, ram.available / (1024 ** 3), disk.free / (1024 ** 3)
        ))
        self.conn.commit()

    def show_history(self):
        """Показываем историю записей."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, cpu_usage, ram_free, disk_free, timestamp FROM records")
            records = cursor.fetchall()

            if not records:
                print("No records found in the database.")
                return

            # Создаем окно для истории
            self.history_window = QWidget()  # Сохраняем как атрибут класса
            self.history_window.setWindowTitle("История записей")
            layout = QVBoxLayout()

            # Создаем таблицу для отображения данных
            table = QTableWidget(len(records), 5)
            table.setHorizontalHeaderLabels(["ID", "ЦП (%)", "ОЗУ (ГБ)", "ПЗУ (ГБ)", "Время"])

            for i, row in enumerate(records):
                for j, val in enumerate(row):
                    table.setItem(i, j, QTableWidgetItem(str(val) if val is not None else ""))

            layout.addWidget(table)
            self.history_window.setLayout(layout)

            # Показываем окно
            self.history_window.setAttribute(Qt.WA_DeleteOnClose)
            self.history_window.show()
        except Exception as e:
            print(f"Error while showing history: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResourceMonitorApp()
    window.show()
    sys.exit(app.exec_())
