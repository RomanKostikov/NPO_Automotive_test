import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from main import ResourceMonitorApp
import sqlite3
import os


class TestResourceMonitorApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем экземпляр приложения для тестирования."""
        cls.app = QApplication([])
        cls.window = ResourceMonitorApp()

    @classmethod
    def tearDownClass(cls):
        """Закрываем приложение после тестов."""
        cls.window.conn.close()
        os.remove("resources.db")  # Удаляем тестовую базу
        cls.app.quit()

    def test_ui_initialization(self):
        """Проверяем, что UI элементы инициализированы."""
        self.assertIsNotNone(self.window.cpu_label)
        self.assertIsNotNone(self.window.ram_label)
        self.assertIsNotNone(self.window.disk_label)
        self.assertIsNotNone(self.window.start_button)
        self.assertIsNotNone(self.window.history_button)

    def test_database_connection(self):
        """Проверяем подключение к базе данных и создание таблицы."""
        cursor = self.window.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records';")
        self.assertIsNotNone(cursor.fetchone())

    def test_timer_interval_update(self):
        """Проверяем обновление интервала таймера."""
        self.window.update_interval_input.setText("2000")
        self.window.update_timer_interval()
        self.assertEqual(self.window.timer.interval(), 2000)

    def test_start_and_stop_recording(self):
        """Проверяем старт и остановку записи."""
        self.window.start_recording()
        self.assertTrue(hasattr(self.window, "record_timer"))
        self.assertTrue(self.window.record_timer.isActive())

        self.window.stop_recording()
        self.assertFalse(self.window.record_timer.isActive())

    def test_record_data(self):
        """Проверяем запись данных в базу."""
        self.window.record_data()
        cursor = self.window.conn.cursor()
        cursor.execute("SELECT * FROM records")
        records = cursor.fetchall()
        self.assertGreater(len(records), 0)

    def test_show_history(self):
        """Проверяем показ истории."""
        # Добавляем тестовую запись
        cursor = self.window.conn.cursor()
        cursor.execute("INSERT INTO records (cpu_usage, ram_free, disk_free) VALUES (10, 5, 200)")
        self.window.conn.commit()

        # Проверяем вызов функции
        self.window.show_history()
        self.assertIsNotNone(self.window.history_window)

    def test_update_record_duration(self):
        """Проверяем обновление таймера записи."""
        self.window.record_start_time = 0
        self.window.update_record_duration()
        self.assertEqual(self.window.record_start_time, 1)


if __name__ == "__main__":
    unittest.main()
