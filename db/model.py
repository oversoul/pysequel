import MySQLdb
import logging


def getTypes(ty):
	text = ty.split(' ')
	unsigned = False
	if len(text) == 1:
		unsigned = False
	else:
		if text[1] == 'unsigned':
			unsigned = True
	text = text[0].split('(')

	size = ''

	if len(text) == 1:
		ty = text[0]
	else:
		ty = text[0]
		size = text[1].strip(')')

	return [ty, size, unsigned]


class dbs:
	def __init__(self, window):
		self.window = window

	def connect(self):
		host = unicode(self.window.con_host.text())
		username = unicode(self.window.con_username.text())
		password = unicode(self.window.con_password.text())
		database = unicode(self.window.con_database.text())
		port = self.window.con_port.text()
		if port == "":
			port = 3306
		try:
			self.db = MySQLdb.connect(host=host, user=username, passwd=password, db=database, port=port)
		except Exception as e:
			logging.error(e)
			return False
		logging.info('Connected...')
		return True

	def deleteTable(self, name):
		cur = self.db.cursor()
		try:
			cur.execute("drop table %s" % name)		
		except Exception as e:
			logging.error(e)
			return False
		cur.close()
		return True

	def getCollations(self):
		cur = self.db.cursor()
		cur.execute("show collation")
		data = cur.fetchall()
		cur.close()
		return data

	def getCharset(self, collation):
		cur = self.db.cursor()
		cur.execute("show collation where collation = '%s'" % collation)
		data = cur.fetchone()
		cur.close()
		return data[1]

	def getCharsets(self):
		cur = self.db.cursor()
		cur.execute("show character set")
		data = cur.fetchall()
		cur.close()
		return data

	def getEngines(self):
		cur = self.db.cursor()
		cur.execute("show engines")
		data = cur.fetchall()
		cur.close()
		return data

	def createTable(self, name, engine, charset, collation):
		q = "CREATE TABLE %s ( id int unsigned primary key auto_increment) ENGINE = %s, CHARACTER SET = %s, DEFAULT COLLATE = %s" % (name, engine, charset, collation)
		cur = self.db.cursor()
		try:
			cur.execute(q)
		except Exception as e:
			logging.error(e)
			return False
		cur.close()
		return True

	def editTable(self, old, name, engine, charset, collation):
		cur = self.db.cursor()
		try:
			if old != name:
				cur.execute("RENAME TABLE `%s` TO `%s`" % (old, name))
			cur.execute("ALTER TABLE `%s` CHARACTER SET `%s`, COLLATE `%s`, ENGINE = `%s`;" % (name, charset, collation, engine))
		except Exception as e:
			logging.error(e)
			return False
		cur.close()
		return True


	def getInfo(self, table):
		cur = self.db.cursor()
		cur.execute("SHOW TABLE STATUS WHERE Name = '%s'" % table)
		data = cur.fetchone()
		cur.close()
		return data

	def getDatabases(self):
		cur = self.db.cursor()
		cur.execute("SHOW DATABASES;")
		data = cur.fetchall()
		cur.close()
		return data

	def setDatabase(self, dbname):
		cur = self.db.cursor()
		cur.execute("use %s;" % dbname)
		cur.close()

	def getTables(self):
		logging.info("getting tables")
		cur = self.db.cursor()
		cur.execute("show tables;")
		tables = cur.fetchall()
		cur.close()
		return tables

	def getFields(self, table):
		logging.info("getting fields from table [%s]" % table)
		cur = self.db.cursor()
		cur.execute("SHOW COLUMNS FROM `%s`" % table)
		fields = cur.fetchall()
		cur.close()
		return fields

	def alterColumn(self, table, field, new):
		q = "alter table %s change %s %s;" % (table, field, new)
		logging.info(q)
		cur = self.db.cursor()
		try:
			cur.execute(q)
		except Exception as e:
			logging.error(e)
			return False
		cur.close()
		return True

	def createColumn(self, table, query):
		q = "alter table %s add column %s" % (table, query)
		logging.info(q)
		cur = self.db.cursor()
		try:
			cur.execute(q)
		except Exception as e:
			logging.error(e)
			return False
		cur.close()
		return True


	def update(self, table, fields, olddata, newdata):
		q = "UPDATE %s SET " % table
		values = {}
		for i in range(len(fields)):
			field = fields[i]
			q = q + field + " = %(" + field + ")s, "
			values[field] = newdata[i]

		key = fields[0]
		values[key] = olddata[0]

		q = q[:-2]
		q = q + " WHERE " + key + " = %(" + key + ")s"

		cur = self.db.cursor()
		try:
			cur.execute(q, values)
		except Exception as e:
			logging.error(e)
			return False
		return True
		


	def insert(self, fields, data, table):
		if len(fields) != len(data):
			logging.error("Data can't be inserted")
			return False

		q = "INSERT INTO %s (" % table
		q = q + ', '.join(fields) + ") VALUES ("
		holder = ""
		values = {}
		for i in range(len(fields)):
			holder = holder + "%(" + fields[i] + ")s, "
			values[fields[i]] = data[i]
		holder = holder[:-2]
		q = q + holder + ")"

		cur = self.db.cursor()
		try:
			cur.execute(q, values)
		except Exception as e:
			logging.error(e)
			return False
		return True

	def remove(self, table, id):
		q = "DELETE FROM %s" % table
		q = q + " WHERE id = %(id)s"
		cur = self.db.cursor()
		try:
			cur.execute(q, {'id': id})
		except Exception as e:
			logging.error(e)
			return False
		return True


	def getCount(self, table):
		cur = self.db.cursor()
		try:
			cur.execute("SELECT count(*) from `%s`" % table)
		except Exception as e:
			logging.error(e)
			return False
		data = cur.fetchone()
		cur.close()
		return long(data[0])

	def getData(self, table):
		q = "SELECT * from `%s`" % table
		cur = self.db.cursor()
		try:
			cur.execute(q)
		except Exception as e:
			logging.error(e)
			return False
		data = cur.fetchall()
		cur.close()
		return data

	def removeField(self, table, field):
		q = "ALTER TABLE '%s' DROP COLUMN `%s`;" % (table, field)
		cur = self.db.cursor()
		try:
			cur.execute(q)
		except Exception as e:
			logging.error(e)
			return False
		return True