import re
from typing import Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, QEventLoop, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QLineEdit, QPushButton, QComboBox, QStatusBar, QTextEdit

from appSettings import Settings
from contacts import ContactCache, Contact
from scriptRunner import SmsSender

settings = Settings.from_file('settings.json')

def sleep_ms(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec_()

class MyQMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_eventing = False
        self.contacts_cache :ContactCache
        self.listWidget :QListWidget
        self.nameFilterLineEdit :QLineEdit
        self.companyFilterLineEdit :QLineEdit
        self.saveAsLineEdit :QLineEdit
        self.saveAsPushButton :QPushButton
        self.savedComboBox :QComboBox
        self.sendButton:QPushButton
        self.messageTextEdit :QTextEdit
        self.invertPushButton:QPushButton
        self.nameFilter = ''
        self.companyFilter = ''
        QtCore.QTimer.singleShot(500, self.on_start)

    def resizeEvent(self, event) -> None:
        global settings
        # print("Window resized to:", event.size())
        if settings and self.is_eventing:
            settings.app_height = self.size().height()
            settings.app_width = self.size().width()
            settings.to_file("settings.json")

    def on_start(self) -> None:
        self.resize(settings.app_width, settings.app_height)
        self.is_eventing = True
        self.contacts_cache = ContactCache()
        self.listWidget = self.findChild(QListWidget)
        self.nameFilterLineEdit = self.findChild(QLineEdit, 'nameLineEdit')
        self.companyFilterLineEdit = self.findChild(QLineEdit, 'companyLineEdit')
        self.saveAsLineEdit = self.findChild(QLineEdit, 'saveAsLineEdit')
        self.saveAsPushButton = self.findChild(QPushButton, 'saveAsPushButton')
        self.saveAsPushButton.setEnabled(False)
        self.savedComboBox = self.findChild(QComboBox, 'listNameComboBox')
        self.sendButton = self.findChild(QPushButton, 'sendButton')
        self.messageTextEdit = self.findChild(QTextEdit, 'messageTextEdit')
        self.invertPushButton = self.findChild(QPushButton, 'invertPushButton')
        self.messageTextEdit.setAcceptRichText(False)
        self.fill_contacts()
        self.nameFilterLineEdit.textChanged.connect(self.fill_contacts)
        self.companyFilterLineEdit.textChanged.connect(self.fill_contacts)
        self.saveAsLineEdit.textChanged.connect(self.save_as_text_changed)
        self.saveAsPushButton.clicked.connect(self.save_as_clicked)
        self.savedComboBox.currentIndexChanged.connect(self.change_list)
        self.messageTextEdit.textChanged.connect(self.message_text_changed)
        self.savedComboBox.addItem('<none>')
        for key in settings.saved_contacts.keys():
            self.savedComboBox.addItem(key)
        self.sendButton.clicked.connect(self.send_message)
        self.invertPushButton.clicked.connect(self.invert_checked_contacts)
        self.messageTextEdit.setFocus()

    def message_text_changed(self):
        self.sendButton.setEnabled(len(self.messageTextEdit.toPlainText()) > 0)

    def send_message(self):
        destinations = self.get_checked_items()
        message = self.messageTextEdit.toPlainText()
        # first_message = True
        if len(destinations) > 0 and len(message) > 0:
            for key in destinations:
                contact = self.contacts_cache.cache[key]
                phone_number = contact.phoneNumber.removeprefix("+1")
                phone_number = "+1" + str(''.join(re.findall(r'[0-9]*', phone_number)))
                self.statusBar().showMessage("Sending message to " + contact.key())
                print("Sending message to {} at {}", contact.key(), phone_number)
                SmsSender.send_sms(phone_number, message)
                self.statusBar().showMessage("Message sent to " + contact.key())

    def invert_checked_contacts(self):
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked)


    def change_list(self):
        selected_list = str(self.savedComboBox.currentText())
        if selected_list == '<none>':
            self.fill_contacts()
        else:
            self.listWidget.clear()
            for key in settings.saved_contacts[selected_list]:
                self.append_contact(self.contacts_cache.cache[key], is_checked=True)

    def save_as_clicked(self):
        global settings
        saved_name = str(self.saveAsLineEdit.text())
        saved_contacts = self.get_checked_items()
        if len(saved_contacts) > 0:
            settings.save_contacts(saved_name, saved_contacts)
            settings.to_file("settings.json")
            self.savedComboBox.addItem(saved_name)

    def get_checked_items(self) -> list[Any]:
        saved_contacts = []
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            if item.checkState() == Qt.Checked:
                saved_contacts.append(item.data(Qt.UserRole).key())
        return saved_contacts

    def save_as_text_changed(self):
        self.saveAsPushButton.setEnabled(len(self.saveAsLineEdit.text()) >0)

    def fill_contacts(self):
        self.listWidget.clear()
        self.nameFilter = self.nameFilterLineEdit.text()
        self.companyFilter = self.companyFilterLineEdit.text()
        for contact in self.contacts_cache.get_contacts(self.is_good_contact):
            self.append_contact(contact)

    def append_contact(self, contact, is_checked=False):
        item = QListWidgetItem(contact.to_string())
        item.setData(Qt.UserRole, contact)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if is_checked else Qt.Unchecked)
        self.listWidget.addItem(item)

    def is_good_contact(self, contact :Contact) -> bool:
        if len(self.nameFilter) > 0:
            if not self.nameFilter in contact.givenName and not self.nameFilter in contact.familyName:
                return False
        if len(self.companyFilter) > 0:
            if not self.companyFilter in contact.companyName:
                return False
        return True


class MyQUiLoader(QUiLoader):
    def createWidget(self, class_name, parent=None, name="") -> QtWidgets.QWidget:
        if class_name == "QMainWindow":               # replace or add promoted name checks
            w = MyQMainWindow(parent)
            w.setObjectName(name)
            return w
        # print('creating widget:', class_name)
        return super().createWidget(class_name, parent, name)

def main():
    app = QtWidgets.QApplication([])
    loader = MyQUiLoader()
    window = loader.load("sendTexts.ui", None)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
