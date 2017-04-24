#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from PyQt4 import QtGui, QtCore

from gui import mainui, fieldui, tableui, editui
from db.model import * 
import datetime
import json


class Config:
	def __init__(self):
		self.file = 'favorites.json'
		with open(self.file, 'r') as config:
			self.config = json.loads(config.read())
		
	def update(self):
		with open(self.file, 'w') as config:
			config.write(json.dumps(self.config, indent=4))

	def create(self, data):
		self.config.append(data)
		self.update()

	def get(self, name):
		for fav in self.config:
			if fav['name'] == name:
				return fav
		return False

	def has(self, name):
		for fav in self.config:
			if fav['name'] == name:
				return True
		return False

	def remove(self, name):
		for i in range(len(self.config)):
			if self.config[i]['name'] == name:
				self.config.pop(i)
		self.update()
		return True

	def edit(self, name, data):
		for i in range(len(self.config)):
			if self.config[i]['name'] == name:
				self.config[i] = data
		self.update()

class EditDialog(QtGui.QDialog, editui.Ui_Dialog):
	def __init__(self, parent):
		self.parent = parent
		super(EditDialog, self).__init__(parent)
		self.setupUi(self)
		

class FieldWindow(QtGui.QDialog, fieldui.Ui_Dialog):

	def __init__(self, parent=None):
		self.parent = parent
		super(FieldWindow, self).__init__(parent)
		self.setupUi(self)

	def getQuery(self):
		name = self.name.text()
		typ = self.type.currentText()
		size = self.length.text()
		if size != '':
			size = "(" + size + ")"
		unsigned = 'unsigned' if self.uns.checkState() == 2 else ''
		nullable = '' if self.nullable.checkState() else 'NOT NULL'
		key = self.key.currentText()
		if key != '':
			key = key + ' key'

		default = self.default_2.text()
		if default != '':
			default = 'DEFAULT %s' % default
		auto = 'auto_increment' if self.autoincrement.checkState() == 2 else ''

		return "`%s` %s%s %s %s %s %s %s" % (name, typ, size, unsigned, nullable, default, key, auto)

	def updateField(self):
		query = self.getQuery()
		res = self.parent.model.alterColumn(self.parent.table, self.defaultName, query)
		if res:
			self.accept()

	def createField(self):
		query = self.getQuery()
		res = self.parent.model.createColumn(self.parent.table, query)
		if res:
			self.accept()

class TableWindow(QtGui.QDialog, tableui.Ui_Dialog):

	def __init__(self, parent=None):
		self.parent = parent
		super(TableWindow, self).__init__(parent)
		self.setupUi(self)
		self.setWindowTitle('Create Table')
		self.cancelBtn.clicked.connect(self.close)
		self.autoFill()

	def fillCollation(self):
		charset = self.table_charset.currentText()
		collations = self.data[str(charset)]
		self.table_collation.clear()
		for c in collations:
			self.table_collation.addItem(c)

	def autoFill(self):
		self.data = dict()
		self.collations = self.parent.model.getCollations()
		self.table_charset.currentIndexChanged.connect(self.fillCollation)
		for collation in self.collations:
			if collation[1] in self.data:
				self.data[collation[1]].append(collation[0])
			else:
				self.data[collation[1]] = [collation[0]]
		
		for key, val in self.data.iteritems():
			self.table_charset.addItem(key)

		charset = self.table_charset.itemText(0)

		collations = self.data[str(charset)]
		for c in collations:
			self.table_collation.addItem(c)

		engines = self.parent.model.getEngines()
		default = ""
		for engine in engines:
			if engine[1] == "DEFAULT":
				default = engine[0]
			self.table_engine.addItem(engine[0])
		self.table_engine.setCurrentIndex(self.table_engine.findText(default))

	def createTable(self):
		name = self.table_name.text()
		engine = self.table_engine.currentText()
		charset = self.table_charset.currentText()
		collation = self.table_collation.currentText()
		res = self.parent.model.createTable(name, engine, charset, collation)
		if res:
			self.parent.selectDb(0)
			self.accept()

	def loadDefaults(self):
		index = self.parent.tables.selectedIndexes()[0]
		try:
			table = index.data(0).toString()
		except Exception as e:
			return False
		info = self.parent.model.getInfo(table)
		self.name = info[0]
		self.setWindowTitle('Edit Table - %s' % table)
		engine = info[1]
		collation = info[14]
		charset = self.parent.model.getCharset(collation)
		self.table_name.setText(self.name)
		self.table_collation.setCurrentIndex(self.table_collation.findText(collation))
		self.table_charset.setCurrentIndex	(self.table_charset.findText(charset))
		self.table_engine.setCurrentIndex(self.table_engine.findText(engine))
		return True

	def editTable(self):
		name = self.table_name.text()
		engine = self.table_engine.currentText()
		charset = self.table_charset.currentText()
		collation = self.table_collation.currentText()
		res = self.parent.model.editTable(self.name, name, engine, charset, collation)
		if res:
			self.parent.selectDb(0)
			self.accept()
		


class MainWindow(QtGui.QMainWindow, mainui.Ui_MainWindow):

	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setupUi(self)
		self.move(QtGui.QApplication.desktop().screen().rect().center() - self.rect().center())
		self.config = Config()
		self.config.new = False
		self.setupFavorites()
		self.model = dbs(self)
		self.setupLogging()
		logging.info('Starting the app')
		self.events()

	def setupLogging(self):
		logger = logging.getLogger()
		logger.setLevel(logging.DEBUG)
		logTextBox = QPlainTextEditLogger(self)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		logTextBox.setFormatter(formatter)
		logger.addHandler(logTextBox)

	def setupFavorites(self):
		self.favorites.clear()
		for favorite in self.config.config:
			self.favorites.addItem(favorite['name'])

	def fillFavorite(self, item):
		favorite = item.data(0).toString()
		favorite = self.config.get(favorite)
		if not favorite:
			return
		self.con_name.setText(favorite['name'])
		self.con_host.setText(favorite['host'])
		self.con_username.setText(favorite['username'])
		self.con_password.setText(favorite['password'])
		self.con_database.setText(favorite['database'])
		self.con_port.setText(favorite['port'])

	def setStructureTab(self):
		self.panel.setCurrentIndex(1)
		self.contentBtn.setChecked(False)
		self.tableinfoBtn.setChecked(False)

	def setContentTab(self):
		self.panel.setCurrentIndex(2)
		self.structureBtn.setChecked(False)
		self.tableinfoBtn.setChecked(False)

	def setInfoTab(self):
		self.panel.setCurrentIndex(3)
		self.contentBtn.setChecked(False)
		self.structureBtn.setChecked(False)


	def events(self):
		self.structureBtn.clicked.connect(self.setStructureTab)
		self.contentBtn.clicked.connect(self.setContentTab)
		self.tableinfoBtn.clicked.connect(self.setInfoTab)
		self.connectBtn.clicked.connect(self.connect)
		self.databases.currentIndexChanged.connect(self.selectDb)
		self.favorites.itemDoubleClicked.connect(self.fillFavorite)
		self.tables.itemDoubleClicked.connect(self.selectTable)
		self.structure.itemDoubleClicked.connect(self.editField)
		self.addFieldBtn.clicked.connect(self.createField)
		self.removeFieldBtn.clicked.connect(self.removeField)
		# favorite btn
		self.addFavoriteBtn.clicked.connect(self.addFavorite)
		self.saveFavoriteBtn.clicked.connect(self.saveFavorite)
		self.removeFavoriteBtn.clicked.connect(self.removeFavorite)
		# Table btn
		self.addTableBtn.clicked.connect(self.addTable)
		self.editTableBtn.clicked.connect(self.editTable)
		self.removeTableBtn.clicked.connect(self.removeTable)
		# data btn
		self.addRowBtn.clicked.connect(self.addDataRow)
		self.removeRowBtn.clicked.connect(self.removeDataRow)
		self.validateRowBtn.clicked.connect(self.validateData)
		self.cancelRowBtn.clicked.connect(self.cancelData)
		self.content.itemDoubleClicked.connect(self.openEditor)
		self.content.currentItemChanged.connect(self.addEdited)
		# 
		# 

	# Data

	def openEditor(self, item):
		t = self.fields[item.column()][1]
		typ, size, unsigned = getTypes(t)
		if typ == 'enum':
			c = QtGui.QComboBox()
			size = size.replace('\'', '')
			options = size.split(',')
			c.addItems(options)
			content = item.data(0).toString()
			c.setCurrentIndex(c.findText(content))
			self.content.setCellWidget( item.row(), item.column(), c)
			c.currentIndexChanged.connect(lambda i: item.setData(0, options[i]))
			c.activated.connect(lambda: self.content.removeCellWidget(item.row(), item.column()))
		elif typ == 'text':
			ed = EditDialog(self)
			ed.setWindowTitle('Change data')
			text = QtGui.QPlainTextEdit(ed)
			ed.verticalLayout.addWidget(text)
			text.setPlainText(item.data(0).toString())
			ed.accepted.connect(lambda: item.setText(text.toPlainText()))
			ed.exec_()
			item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

		# td = TypeDialog(self)
		# td.show()

	def addEdited(self, item):
		if item is None:
			return
			
		i = self.content.item(item.row(), 0)
		if i is None:
			return
			
		row = item.row()
		if row not in self.updatable:
			self.updatable.append(row)

	def addDataRow(self):
		self.content.insertRow( self.content.rowCount() )

	def removeDataRow(self):
		index = self.content.selectedIndexes()[0]
		id = index.data(0).toString()
		if self.model.remove(self.table, id):
			self.content.removeRow(index.row())

	def cancelData(self):
		self.fillData(self.table, self.fields)
		
	def validateData(self):
		fields = []
		bakfields = self.fields
		for field in bakfields:
			fields.append(field[0])
		actual = self.model.getCount(self.table)
		all = range(self.content.rowCount())
		update = all[:actual]
		insert = all[actual:]
		if len(update) > 0:
			self.updateRow(fields)

		for i in insert:
			data = []
			for f in range(len(fields)):
				item = self.content.item(i, f)
				if item is None:
					data.append(None)
				else:
					data.append( unicode(item.data(0).toString()) )
			self.insertRow(fields, data, bakfields)

	def updateRow(self, fields):
		if len(self.updatable) == 0:
			return
		data = self.model.getData(self.table)
		for i in self.updatable:
			newdata = []
			for f in range(len(fields)):
				item = self.content.item(i, f)
				if item is None:
					newdata.append(None)
				else:
					newdata.append( unicode(item.data(0).toString()) )
			self.model.update(self.table, list(fields), data[i], newdata)


	def insertRow(self, fields, data, bakfields):
		if self.model.insert(list(fields), data, self.table):
			self.fillData(self.table, bakfields)


	# Table
	def addTable(self):
		table = TableWindow(self)
		table.addBtn.clicked.connect(table.createTable)
		table.show()

	def editTable(self):
		table = TableWindow(self)
		table.addBtn.clicked.connect(table.editTable)
		if not table.loadDefaults():
			logging.error('Make sure a table is selected')
			return
		table.addBtn.setText('Edit')
		table.show()

	def removeTable(self):
		index = self.tables.selectedIndexes()[0]
		try:
			name = index.data(0).toString()
		except Exception as e:
			return
		self.model.deleteTable(name)
		tables = self.model.getTables()
		self.tables.clear()
		for table in tables:
			self.tables.addItem(table[0])


	# Favorites
	def clearFavoriteFields(self):
		self.con_name.setText('')
		self.con_host.setText('')
		self.con_port.setText('')
		self.con_username.setText('')
		self.con_password.setText('')
		self.con_database.setText('')

	def addFavorite(self):
		self.config.new = True
		self.clearFavoriteFields()
		item = QtGui.QListWidgetItem("New Favorite")
		self.favorites.currentTextChanged.connect(self.editFavoriteName)
		item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
		self.favorites.addItem(item)
		self.favorites.editItem(item)
		self.favorites.itemChanged.connect(self.disableFavoriteEdit)

	def editFavoriteName(self, text):
		self.con_name.setText(text)

	def disableFavoriteEdit(self, item):
		self.favorites.blockSignals(True)
		item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
		self.favorites.blockSignals(False)
		row = self.favorites.row(item)
		self.favorites.setCurrentRow(row)

	def saveFavorite(self):
		con_name = self.con_name.text()
		con_host = self.con_host.text()
		con_port = self.con_port.text()
		con_username = self.con_username.text()
		con_password = self.con_password.text()
		con_database = self.con_database.text()		
		data = {"name": str(con_name), "host": str(con_host), "username": str(con_username), "password": str(con_password), "database": str(con_database), "port": str(con_port)}
		if self.config.new == True:
			if self.config.has(con_name):
				logging.error("Favorite with name %s exists already." % con_name)
				return False
			self.config.create(data)
		else:
			self.config.edit(con_name, data)
		self.setupFavorites()
		self.config.new = False

	def removeFavorite(self):
		index = self.favorites.selectedIndexes()[0]
		try:
			name = index.data(0).toString()
		except Exception as e:
			return
		self.config.remove(name)
		self.clearFavoriteFields()
		self.setupFavorites()

	# Slot
	def connect(self):
		logging.info("Connecting to db...")
		if not self.model.connect():
			return
		# self.panel.setCurrentIndex(1)
		self.structureBtn.setChecked(True)
		self.setStructureTab()
		databases = self.model.getDatabases()
		for db in databases:
			self.databases.addItem(db[0])
		db = self.con_database.text()
		if db != '':
			self.databases.setCurrentIndex(self.databases.findText(db))
		self.sidebar.setCurrentIndex(1)

	def selectDb(self, index):
		logging.info("Changing database...")
		self.model.setDatabase(self.databases.currentText())
		tables = self.model.getTables()
		self.tables.clear()
		for table in tables:
			self.tables.addItem(table[0])

	def fillData(self, table, fields):
		self.updatable = []
		data = self.model.getData(table)
		self.content.setColumnCount(len(fields))
		for n in range(len(fields)):
			self.content.setHorizontalHeaderItem(n, QtGui.QTableWidgetItem(fields[n][0]))

		self.content.setRowCount(len(data))

		for n in range(len(data)):
			for i in range(len(fields)):
				item = data[n][i]
				if isinstance(item, datetime.datetime):
					item = item.strftime("%Y-%m-%d %H:%M:%S")
				elif item is None:
					item = ''
				elif type(item) is long:
					item = str(item)
				self.content.setItem(n, i, QtGui.QTableWidgetItem(item))

	def fillInfo(self, table):
		info = self.model.getInfo(table)
		self.engine_label.setText(str(info[1]))
		self.rows_label.setText(str(info[4]))
		if info[6] is None or info[8] is None:
			self.size_label.setText("~0 MB")
		else:
			size = round((float(info[6]) + info[8]) / 1024 / 1024, 2)
			self.size_label.setText("~" + str(size) + " MB")
		created = info[11]
		if created is None:
			created = ''
		else:
			created = created.strftime("%Y-%m-%d %H:%M:%S")
		self.created_label.setText(created)
		self.encoding_label.setText(info[14] if info[14] is not None else '')


	def selectTable(self, item):
		self.item = item
		table = item.data(0).toString()
		self.table = table
		self.fields = self.model.getFields(table)
		self.fillData(table, self.fields)
		self.fillInfo(table)

		self.structure.clearContents()
		self.structure.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
		self.structure.setRowCount(len(self.fields))
		self.structure.setColumnCount(8)
		for n in range(len(self.fields)):
			self.structure.setItem(n, 0, QtGui.QTableWidgetItem(unicode(self.fields[n][0])))
			typ, size, unsigned = getTypes(self.fields[n][1])
			self.structure.setItem(n, 1, QtGui.QTableWidgetItem(typ))
			self.structure.setItem(n, 2, QtGui.QTableWidgetItem(size))
			
			item = QtGui.QTableWidgetItem()
			item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
			check = QtCore.Qt.Checked if unsigned else QtCore.Qt.Unchecked
			item.setCheckState(check)
			self.structure.setItem(n, 3, item)

			item = QtGui.QTableWidgetItem()
			item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
			check = QtCore.Qt.Checked if self.fields[n][2] == 'YES' else QtCore.Qt.Unchecked
			item.setCheckState(check)

			self.structure.setItem(n, 4, item)
			self.structure.setItem(n, 5, QtGui.QTableWidgetItem(self.fields[n][3]))
			self.structure.setItem(n, 6, QtGui.QTableWidgetItem(self.fields[n][4] or ''))
			self.structure.setItem(n, 7, QtGui.QTableWidgetItem(self.fields[n][5]))

	def editField(self, item):
		index = self.structure.selectedIndexes()[0]
		field = self.fields[index.row()]

		fieldUi = FieldWindow(self)
		fieldUi.saveBtn.clicked.connect(fieldUi.updateField)
		name = unicode(field[0])
		fieldUi.setWindowTitle('Edit Field - %s' % name)
		fieldUi.defaultName = name
		fieldUi.name.setText(name)
		typ, size, unsigned = getTypes(field[1])
		if typ == 'enum':
			fieldUi.label_3.setText('Values')
		fieldUi.type.setCurrentIndex(fieldUi.type.findText(typ))
		fieldUi.length.setText(size)
		fieldUi.uns.setChecked(unsigned)
		fieldUi.nullable.setChecked(True if field[2] == 'YES' else False)
		# key
		key = field[3]
		if key == 'PRI':
			key = 1
		elif key == 'UNI':
			key = 2
		elif key == 'MUL':
			key = 3
		else:
			key = 0
		
		fieldUi.key.setCurrentIndex(key)
		fieldUi.default_2.setText(field[4] or '')
		isAuto = False
		if 'auto_increment' in field[5]:
			isAuto = True
		fieldUi.autoincrement.setChecked(isAuto)

		fieldUi.show()
		if fieldUi.exec_() == 1:
			self.selectTable(self.item)

	def createField(self):
		fieldUi = FieldWindow(self)
		fieldUi.setWindowTitle('Create Field')
		fieldUi.saveBtn.clicked.connect(fieldUi.createField)
		fieldUi.show()
		if fieldUi.exec_() == 1:
			self.selectTable(self.item)

	def removeField(self):
		try:
			index = self.structure.selectedIndexes()[0]
		except Exception as e:
			return
		field = index.data(0).toString()
		if self.model.removeField(self.table, field):
			self.selectTable(self.item)



class QPlainTextEditLogger(logging.Handler):

	def __init__(self, parent=None):
		super(QPlainTextEditLogger, self).__init__()
		self.widget = parent.log_viewer

	def emit(self, record):
		msg = self.format(record)
		self.widget.appendPlainText(msg)

	def write(self, m):
		pass


if __name__ == '__main__':
	File = QtCore.QFile('style.qss')
	File.open(QtCore.QFile.ReadOnly);
	styleSheet = str(File.readAll());
	app = QtGui.QApplication([])
	app.setStyleSheet(styleSheet);
	window = MainWindow()
	window.centralWidget().layout().setContentsMargins(0, 0, 0, 0)
	window.splitter.setSizes((3,7))
	window.show()
	app.exec_()