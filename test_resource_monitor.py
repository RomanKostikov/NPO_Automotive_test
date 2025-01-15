import unittest
from PyQt5.QtWidgets import QApplication
from logic import ResourceMonitorLogic
from ui import ResourceMonitorUI
from db import DatabaseManager
import os


class TestResourceMonitorApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем экземпляры модулей для тестирования."""
        cls.app = QApplication([])
        cls.db = DatabaseManager("test_resources.db")  # Используем тестовую базу данных
        cls.ui = ResourceMonitorUI()
        cls.logic = ResourceMonitorLogic(cls.db, cls.ui)

    @classmethod
    def tearDownClass(cls):
        """Закрываем соединение с базой данных и удаляем тестовую базу."""
        cls.db.close()
        os.remove("test_resources.db")
        cls.app.quit()

    def test_ui_initialization(self):
        """Проверяем, что UI элементы инициализированы."""
        self.assertIsNotNone(self.ui.cpu_label)
        self.assertIsNotNone(self.ui.ram_label)
        self.assertIsNotNone(self.ui.disk_label)
        self.assertIsNotNone(self.ui.start_button)
        self.assertIsNotNone(self.ui.history_button)

    def test_database_connection(self):
        """Проверяем подключение к базе данных и создание таблицы."""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records';")
        self.assertIsNotNone(cursor.fetchone())

    def test_timer_interval_update(self):
        """Проверяем обновление интервала таймера."""
        self.ui.update_interval_input.setText("2000")
        self.logic.update_timer_interval()
        self.assertEqual(self.logic.update_timer.interval(), 2000)

    def test_start_and_stop_recording(self):
        """Проверяем старт и остановку записи."""
        self.logic.start_recording()
        self.assertTrue(self.logic.record_timer.isActive())

        self.logic.stop_recording()
        self.assertFalse(self.logic.record_timer.isActive())

    def test_record_data(self):
        """Проверяем запись данных в базу."""
        self.logic.record_data()
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM records")
        records = cursor.fetchall()
        self.assertGreater(len(records), 0)

    def test_show_history(self):
        """Проверяем показ истории."""
        # Добавляем тестовую запись
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO records (cpu_usage, ram_free, disk_free) VALUES (10, 5, 200)")
        self.db.conn.commit()

        # Проверяем вызов функции
        self.logic.show_history()
        self.assertIsNotNone(self.ui.history_window)

    def test_update_record_duration(self):
        """Проверяем обновление таймера записи."""
        self.logic.record_start_time = 0
        self.logic.update_record_duration()
        self.assertEqual(self.logic.record_start_time, 1)


if __name__ == "__main__":
    unittest.main()
