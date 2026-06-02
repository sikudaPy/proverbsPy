import sys, json
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout,QLineEdit,QMessageBox
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl

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
        self._file_menu = self.menuBar().addMenu("&File")

        self.table = QtWidgets.QTableView()

        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.findLayout = QHBoxLayout()
        self.verticalLayout.insertLayout(0, self.findLayout)
        self.findText = QLineEdit()
        self.findText.setPlaceholderText(" Find text in table ")
        self.findLayout.addWidget(self.findText, stretch=100, alignment=Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight)
        self.findButton = QPushButton(" Find... ")
        self.findLayout.addWidget(self.findButton, stretch=10, alignment=Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight)
        self.findButton.clicked.connect(self.find)

        self.verticalLayout.addWidget(self.table)
        self.setCentralWidget(self.centralwidget)

        # Инициализация менеджера сети
        self.network_manager = QNetworkAccessManager(self)
        self.start_request()

    def start_request(self):
              
        url = QUrl("https://python1c.ru/catalogs/api?format=json")
        request = QNetworkRequest(url)
        
        # Отправляем GET запрос
        self.reply = self.network_manager.get(request)
        
        # Подключаем сигнал завершения
        self.reply.finished.connect(self.handle_response)

    def handle_response(self):
        if self.reply.error() == QNetworkReply.NetworkError.NoError:
            # Читаем данные
            str_catalog = self.reply.readAll().data().decode("utf-8")
            self.table.setModel(TableModel(str_catalog))
        else:
            # Обработка ошибки
            error_str = self.reply.errorString()
            str_catalog = '[{"id":49,"name":"Богу молись, а к берегу гребись.","title":"(Пословица означает, "'+error_str+'"}]'
            self.table.setModel(TableModel(str_catalog))
            
        self.reply.deleteLater()
     
        #self.setCentralWidget(self.table)
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

    # @Slot()
    def find(self):
        findString = self.findText.text()
        dlg = QMessageBox(self)
        dlg.setWindowTitle(self.tr("Пословицы"))
        dlg.setText(self.tr("text: '"+findString+"' будет найден"))
        dlg.exec()

            

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.setMinimumWidth(1024)
window.setMinimumHeight(768)
window.show()
app.exec()    