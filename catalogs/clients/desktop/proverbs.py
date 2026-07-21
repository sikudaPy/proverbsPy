import sys, json, re
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
    def __init__(self, catalogs):
        super().__init__()
        self.catalogs = catalogs    

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
        if self.catalogs:
            return len(self.catalogs)
        else:
            return 0

    def columnCount(self, index):
        return 2 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пословицы")
        file_menu = self.menuBar().addMenu("&File")
        self.exit_action = file_menu.addAction("E&xit")
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        help_menu = self.menuBar().addMenu("&Help")
        about_qt_action = help_menu.addAction("About Qt", qApp.aboutQt)

        self.catalogs_all = []
        self.table = QtWidgets.QTableView()

        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.findLayout = QHBoxLayout()
        self.verticalLayout.insertLayout(0, self.findLayout)

        findLabel = QLabel("Найти:")
        self.findLayout.addWidget( findLabel, stretch=100, alignment=Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignRight)
        self.findText = QLineEdit()
        self.findText.setPlaceholderText(" Find text in table ")
        self.findText.setFixedWidth(800)  
        self.findLayout.addWidget(self.findText, stretch=10, alignment=Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight)
        self.findText.textChanged.connect(self.find)
        
        self.verticalLayout.addWidget(self.table)
        self.setCentralWidget(self.centralwidget)

        # Инициализация менеджера сети
        self.network_manager = QNetworkAccessManager(self)
        self.start_request()

    def start_request(self):
              
        url = QUrl("https://proverbs.python1c.ru/catalogs/api?format=json")
        request = QNetworkRequest(url)
        
        # Отправляем GET запрос
        self.reply = self.network_manager.get(request)
        
        # Подключаем сигнал завершения
        self.reply.finished.connect(self.handle_response)

    def handle_response(self):
        if self.reply.error() == QNetworkReply.NetworkError.NoError:
            # Читаем данные
            str_catalog = self.reply.readAll().data().decode("utf-8")
            self.catalogs_all = json.loads(str_catalog)
            self.table.setModel(TableModel(self.catalogs_all))
        else:
            # Обработка ошибки
            error_str = self.reply.errorString()
            str_catalog = '[{"id":49,"name":"Богу молись, а к берегу гребись.","title":"(Пословица означает, "'+error_str+'"}]'
            self.catalogs_all = json.loads(str_catalog)
            self.table.setModel(TableModel(self.catalogs_all))
            
        self.reply.deleteLater()
     
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
        strFind = self.findText.text().upper()
        catalogs = list(filter(lambda item: strFind in item['name'].upper() or strFind in item['title'].upper() , self.catalogs_all))
        self.table.catalogs = catalogs
        self.table.setModel(TableModel(catalogs))
       
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()

window.setMinimumWidth(800)
window.setMinimumHeight(600)
window.resize(1024, 768)
window.show()
app.exec()    