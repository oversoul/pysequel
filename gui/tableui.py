# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/tableui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(380, 176)
        Dialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.table_name = QtGui.QLineEdit(Dialog)
        self.table_name.setObjectName(_fromUtf8("table_name"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.table_name)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.table_charset = QtGui.QComboBox(Dialog)
        self.table_charset.setEditable(False)
        self.table_charset.setObjectName(_fromUtf8("table_charset"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.table_charset)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.table_collation = QtGui.QComboBox(Dialog)
        self.table_collation.setObjectName(_fromUtf8("table_collation"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.table_collation)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.table_engine = QtGui.QComboBox(Dialog)
        self.table_engine.setObjectName(_fromUtf8("table_engine"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.table_engine)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelBtn = QtGui.QPushButton(Dialog)
        self.cancelBtn.setAutoDefault(False)
        self.cancelBtn.setObjectName(_fromUtf8("cancelBtn"))
        self.horizontalLayout.addWidget(self.cancelBtn)
        self.addBtn = QtGui.QPushButton(Dialog)
        self.addBtn.setObjectName(_fromUtf8("addBtn"))
        self.horizontalLayout.addWidget(self.addBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        self.table_charset.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "Table Name:", None))
        self.label_2.setText(_translate("Dialog", "Table Encoding:", None))
        self.label_3.setText(_translate("Dialog", "Table Collation:", None))
        self.label_4.setText(_translate("Dialog", "Table Type:", None))
        self.cancelBtn.setText(_translate("Dialog", "Cancel", None))
        self.addBtn.setText(_translate("Dialog", "Add", None))

