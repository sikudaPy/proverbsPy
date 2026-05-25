import sys, json
import requests
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class ItemDialog(QDialog):
    def __init__(self, name, title):
        super().__init__()
        self.setWindowTitle("Пословица")

        # Create a layout to hold widgets
        layout = QVBoxLayout()

        text = "<h1>"+name+"</h1><p>"+title+"</p>"
        self.label = QLabel(text)
        self.label.setWordWrap(True) 

        # Add label to the layout and set the layout for the dialog
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.close_btn = QPushButton("Закрыть")
        layout.addWidget(self.close_btn)
        self.close_btn.clicked.connect(self.reject)

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.catalogs = json.loads(data)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section  == 0:
                return "Name"
            else:
                return "Title"
        return super().headerData(section, orientation, role)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # index.row() индексирует по внешнему списку, index.column() — по подсписку
            if index.column() == 0: 
                return self.catalogs[index.row()]["name"]
            else: 
                return self.catalogs[index.row()]["title"]

    def rowCount(self, index):
        return len(self.catalogs)

    def columnCount(self, index):
        return 2 #len(self._data)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пословицы")
        self.table = QtWidgets.QTableView()

        url = "https://python1c.ru/catalogs/api?format=json"
        try:
            catalog = requests.get(url)
            self.table.setModel(TableModel(catalog.text))
        except:
            print("Не могу получить данные https://python1c.ru")
            str_catalog = '[{"id":49,"name":"Богу молись, а к берегу гребись. ","title":"(Пословица означает, что недостаточно того, что ты просишь Высшие Силы тебе помочь в твоем деле, нужно еще и самому прилагать усилия, для успеха в нем.)"}]'
            self.table.setModel(TableModel(str_catalog))
        
        self.setCentralWidget(self.table)
        self.table.setAlternatingRowColors(True)
        self.table.resizeColumnToContents(0)
        self.table.setColumnWidth(1, 600)
        self.table.clicked.connect(self.show_item)

    def show_item(self, index):

        model = self.table.model()
        indexName  = model.index(index.row(), 0)
        indexTitle = model.index(index.row(), 1)
        name = model.data(indexName, Qt.DisplayRole)
        title = model.data(indexTitle, Qt.DisplayRole)
        dialog = ItemDialog(name, title)
        dialog.exec()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.setMinimumWidth(640)
window.setMinimumHeight(480)
window.show()
app.exec()    