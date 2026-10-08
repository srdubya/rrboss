import re
import sys
from typing import Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QLineEdit, QPushButton, QComboBox, QTextEdit, \
    QSpinBox

from appSettings import Settings
from contacts import ContactCache, Contact
from smsSender import SmsSender, Destination
from datetime import datetime

settings = Settings.from_file()

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
        self.clearPushButton:QPushButton
        self.batchSizeSpinBox :QSpinBox
        self.itemCheckedSuspended :bool = True
        self.nameFilter = ''
        self.companyFilter = ''
        QtCore.QTimer.singleShot(100, self.on_start)

    def on_start(self) -> None:
        self.resize(settings.app_width, settings.app_height)
        self.move(settings.app_x, settings.app_y)
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
        self.batchSizeSpinBox = self.findChild(QSpinBox, 'batchSizeSpinBox')
        self.messageTextEdit.setAcceptRichText(False)
        self.fill_contacts()
        self.nameFilterLineEdit.textChanged.connect(self.fill_contacts)
        self.companyFilterLineEdit.textChanged.connect(self.fill_contacts)
        self.saveAsLineEdit.textChanged.connect(self.save_as_text_changed)
        self.saveAsPushButton.clicked.connect(self.save_as_clicked)
        self.savedComboBox.currentIndexChanged.connect(self.change_list)
        self.messageTextEdit.textChanged.connect(self.message_text_changed)
        self.listWidget.itemChanged.connect(self.recalc_list_count)
        self.savedComboBox.addItem('<none>')
        for key in settings.saved_contacts.keys():
            self.savedComboBox.addItem(key)
        self.sendButton.clicked.connect(self.send_message)
        self.invertPushButton.clicked.connect(self.invert_checked_contacts)
        self.clearPushButton.clicked.connect(self.clear_checked_contacts)
        self.batchSizeSpinBox.setValue(settings.batch_size)
        self.batchSizeSpinBox.valueChanged.connect(self.on_new_batch_size)
        self.messageTextEdit.setFocus()

    def moveEvent(self, event):
        global settings
        if settings and self.is_eventing:
            pos = self.pos()
            settings.app_x = pos.x()
            settings.app_y = pos.y()
            settings.to_file()
        super().moveEvent(event)

    def resizeEvent(self, event) -> None:
        global settings
        # print("Window resized to:", event.size())
        if settings and self.is_eventing:
            settings.app_height = self.size().height()
            settings.app_width = self.size().width()
            settings.to_file()
        super().resizeEvent(event)

    def on_new_batch_size(self, value :int):
        global settings
        if settings and self.is_eventing:
            settings.batch_size = value
            settings.to_file()

    def recalc_list_count(self) -> None:
        if self.itemCheckedSuspended:
            return
        total_count = self.listWidget.count()
        checked_count = 0
        for index in range(total_count):
            item = self.listWidget.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                checked_count += 1
        self.statusBar().showMessage('%d of %d selected' % (checked_count, total_count))

    def message_text_changed(self):
        self.sendButton.setEnabled(len(self.messageTextEdit.toPlainText()) > 0)

    def send_message(self):
        self.setEnabled(False)
        QtCore.QTimer.singleShot(100, self.send_the_messages)

    def send_the_messages(self) -> None:
        try:
            checked_items = self.get_checked_items()
            message = self.messageTextEdit.toPlainText()
            SmsSender.max_phone_nums = self.batchSizeSpinBox.value()
            destinations :list[Destination] = []
            if len(checked_items) > 0 and len(message) > 0:
                for key in checked_items:
                    contact = self.contacts_cache.cache[key]
                    phone_number = contact.phoneNumber.removeprefix("+1")
                    phone_number = "+1" + str(''.join(re.findall(r'[0-9]*', phone_number)))
                    if len(phone_number) == 12:  # +13456789012
                        destinations.append(Destination(contact.givenName, contact.familyName, phone_number))
                    else:
                        print(f"Bad phone number: {phone_number} for: {contact.key()}", file=sys.stderr)
                if len(destinations) > 0:
                    SmsSender.send_sms(destinations, message)
                    print(f"   {datetime.now()}: Send completed")
        finally:
            self.setEnabled(True)

    def invert_checked_contacts(self):
        self.itemCheckedSuspended = True
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            item.setCheckState(
                Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
            )
        self.itemCheckedSuspended = False
        self.recalc_list_count()

    def clear_checked_contacts(self):
        self.itemCheckedSuspended = True
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)
        self.itemCheckedSuspended = False
        self.recalc_list_count()

    def change_list(self):
        self.itemCheckedSuspended = True
        selected_list = str(self.savedComboBox.currentText())
        if selected_list == '<none>':
            self.fill_contacts()
        else:
            self.listWidget.clear()
            for key in settings.saved_contacts[selected_list]:
                self.append_contact(self.contacts_cache.cache[key], is_checked=True)
        self.itemCheckedSuspended = False
        self.recalc_list_count()

    def save_as_clicked(self):
        global settings
        saved_name = str(self.saveAsLineEdit.text())
        saved_contacts = self.get_checked_items()
        if len(saved_contacts) > 0:
            settings.save_contacts(saved_name, saved_contacts)
            settings.to_file()
            self.savedComboBox.addItem(saved_name)

    def get_checked_items(self) -> list[Any]:
        saved_contacts = []
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                saved_contacts.append(item.data(Qt.ItemDataRole.UserRole).key())
        return saved_contacts

    def save_as_text_changed(self):
        self.saveAsPushButton.setEnabled(len(self.saveAsLineEdit.text()) >0)

    def fill_contacts(self):
        self.itemCheckedSuspended = True
        self.listWidget.clear()
        self.nameFilter = self.nameFilterLineEdit.text()
        self.companyFilter = self.companyFilterLineEdit.text()
        for contact in self.contacts_cache.get_contacts(self.is_good_contact):
            self.append_contact(contact)
        self.itemCheckedSuspended = False
        self.recalc_list_count()

    def append_contact(self, contact, is_checked=False):
        item = QListWidgetItem(contact.to_string())
        item.setData(Qt.ItemDataRole.UserRole, contact)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
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
    window = loader.load("mainWindow.ui", None)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
