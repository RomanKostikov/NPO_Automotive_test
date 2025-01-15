import psutil
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox


class ResourceMonitorLogic:
    def __init__(self, db, ui):
        self.db = db
        self.ui = ui
        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self.record_data)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_resource_usage)
        self.update_timer.start(1000)

        self.record_duration_timer = QTimer()
        self.record_duration_timer.timeout.connect(self.update_record_duration)
        self.record_start_time = None

        # Connect UI actions
        self.ui.apply_button.clicked.connect(self.update_timer_interval)
        self.ui.start_button.clicked.connect(self.start_recording)
        self.ui.history_button.clicked.connect(self.show_history)

    def update_resource_usage(self):
        """Обновляем показатели ресурсов."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        self.ui.cpu_label.setText(f"ЦП: {cpu}%")
        self.ui.ram_label.setText(
            f"ОЗУ: {ram.available / (1024 ** 3):.2f}ГБ свободно/{ram.total / (1024 ** 3):.2f}ГБ всего")
        self.ui.disk_label.setText(
            f"ПЗУ: {disk.free / (1024 ** 3):.2f}ГБ свободно/{disk.total / (1024 ** 3):.2f}ГБ всего")

    def update_timer_interval(self):
        """Обновляем интервал времени таймера и записи."""
        try:
            interval = int(self.ui.update_interval_input.text())
            if interval < 100:
                raise ValueError("Интервал должен быть не менее 100 мс.")

            self.update_timer.setInterval(interval)

            if self.record_timer.isActive():
                self.record_timer.setInterval(interval)

            QMessageBox.information(self.ui, "Успешно",
                                    f"Интервал обновления установлен на {interval} мс.")
        except ValueError as e:
            QMessageBox.warning(self.ui, "Ошибка", str(e))

    def start_recording(self):
        """Начинаем запись данных в БД."""
        self.ui.start_button.setText("Остановить запись")
        self.ui.start_button.clicked.disconnect()
        self.ui.start_button.clicked.connect(self.stop_recording)

        self.record_timer.setInterval(self.update_timer.interval())
        self.record_timer.start()

        self.record_start_time = 0
        self.record_duration_timer.start(1000)

    def stop_recording(self):
        """Останавливаем запись данных."""
        self.record_timer.stop()
        self.record_duration_timer.stop()
        self.ui.timer_label.setText("Время записи: 00:00")
        self.ui.start_button.setText("Начать запись")
        self.ui.start_button.clicked.disconnect()
        self.ui.start_button.clicked.connect(self.start_recording)

    def update_record_duration(self):
        """Обновляем отображение времени записи."""
        if self.record_start_time is not None:
            self.record_start_time += 1
            minutes, seconds = divmod(self.record_start_time, 60)
            self.ui.timer_label.setText(f"Время записи: {minutes:02}:{seconds:02}")

    def record_data(self):
        """Записываем данные о загрузке в БД."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        self.db.insert_record(cpu, ram.available / (1024 ** 3), disk.free / (1024 ** 3))

    def show_history(self):
        """Показывает историю записей."""
        records = self.db.fetch_all_records()
        print(f"Извлечено записей: {len(records)}")  # Отладочный вывод
        self.ui.display_history(records)
