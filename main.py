import sys
import json
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QSpinBox, QProgressBar, QLabel, QPushButton, QWidget
)
from PyQt5.QtCore import QCoreApplication, pyqtSignal, QObject
from PyQt5.uic import loadUi

class SignalEmitter(QObject):
    update_progress = pyqtSignal(int)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('design.ui', self)

        self.start_button.clicked.connect(self.startButtonClicked)

        self.signal_emitter = SignalEmitter()
        self.signal_emitter.update_progress.connect(self.updateProgressBar)

    def startButtonClicked(self):
        num_processes = self.num_of_processes.value()
        num_threads = self.num_of_threads.value()

        self.fetchData(num_processes, num_threads)

    def fetchData(self, num_processes, num_threads):
        start_time = time.time()
        num_of_products = 100
        file_name = 'Data.json'

        successful_results = []

        print(f"Starting with {num_processes} processes and {num_threads} threads...")

        with ProcessPoolExecutor(max_workers=num_processes) as process_executor:
            for ind, result in enumerate(process_executor.map(fetch_product_data, range(1, num_of_products + 1))):
                self.signal_emitter.update_progress.emit(int((ind + 1) / num_of_products * 100))

                QCoreApplication.instance().processEvents()

                if result is not None:
                    successful_results.append(result)

        with ThreadPoolExecutor(max_workers=num_threads) as thread_executor:
            thread_results = list(thread_executor.map(json.dumps, successful_results))

        with open(file_name, 'w') as file:
            for ind, result in enumerate(thread_results):
                file.write(result)
                if ind != len(thread_results) - 1:
                    file.write(',\n')

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Everything fetched and saved to {file_name}")
        print(f"Elapsed time: {elapsed_time} seconds")
        self.message_label.setText(f"Elapsed time: {round(elapsed_time, 2)} seconds\n"
                                   f"Product information stored in Data.json")

    def updateProgressBar(self, value):
        self.progress_bar.setValue(value)

def fetch_product_data(product_id):
    url = f'https://dummyjson.com/products/{product_id}'
    print(f"Fetching data for product {product_id}...")
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Successfully fetched data for product {product_id}")
        return response.json()
    else:
        print(f"Failed to fetch data for product {product_id}. Status code: {response.status_code}")
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Scrapping with Pools | GE")
    window.setFixedSize(690, 540)
    window.show()
    sys.exit(app.exec_())
