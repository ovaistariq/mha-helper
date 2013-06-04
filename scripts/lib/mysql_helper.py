import MySQLdb
import re

class MySQL_helper(object):
    def __init__(self, host, user, password):
        self._host = host
        self._user = user
        self._password = password

    def connect(self):
        try:
            self._connection = MySQLdb.connect(host=self._host, user=self._user, passwd=self._password)
        except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False

        return True

    def disconnect(self):
        self._connection.close()

    def is_read_only_query(self, sql):
        if re.match('^select', sql, re.I) != None:
            return True

        if re.match('^show', sql, re.I) != None:
            return True

        return False

    def get_version(self):
        cursor = self._connection.cursor()
        cursor.execute("SELECT VERSION()")
        row = cursor.fetchone()
	cursor.close()

        return row[0]

    def get_connection_id(self):
	return self._connection.thread_id()

    def get_current_user(self):
        return self._user

    def set_read_only(self):
        cursor = self._connection.cursor()
	try:
            cursor.execute("SET GLOBAL read_only = 1")
	except MySQLdb.Error as e:
	    print "Error %d: %s" % (e.args[0], e.args[1])
	    return False
	finally:
	    cursor.close()

        return True

    def unset_read_only(self):
        cursor = self._connection.cursor()
	try:
            cursor.execute("SET GLOBAL read_only = 0")
	except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False
        finally:
            cursor.close()

        return True

    def is_read_only(self):
	cursor = self._connection.cursor()
	cursor.execute("SELECT @@read_only")
	row = cursor.fetchone()
	cursor.close()

	if row[0] == 1:
	    return True

	return False

    def disable_log_bin(self):
        cursor = self._connection.cursor()
	try:
            cursor.execute("SET SQL_LOG_BIN = 0")
	except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False
        finally:
            cursor.close()

        return True

    def enable_log_bin(self):
        cursor = self._connection.cursor()
        try:
            cursor.execute("SET SQL_LOG_BIN = 1")
        except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False
        finally:
            cursor.close()

        return True

    def get_processlist(self):
	cursor = self._connection.cursor(MySQLdb.cursors.DictCursor)
	try:
	    cursor.execute("SHOW PROCESSLIST")
	    threads = cursor.fetchall()
	except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False
        finally:
	    cursor.close()

	return threads

    def get_all_users(self):
	cursor = self._connection.cursor(MySQLdb.cursors.DictCursor)
	try:
	    cursor.execute("SELECT * from mysql.user")
	    users = cursor.fetchall()
	except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False
        finally:
            cursor.close()

	return users

    def get_user_grants(self, username):
	cursor = self._connection.cursor()
        grants = []
	try:
            cursor.execute("SHOW GRANTS FOR %s" % username)
            for row in cursor.fetchall():
                grants.append(row[0])
        except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False
        finally:
            cursor.close()

	return grants

    def kill_connection(self, connection_id):
	cursor = self._connection.cursor()
	try:
	    cursor.execute("KILL CONNECTION %d" % connection_id)
	except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False
        finally:
            cursor.close()

	return True

    def revoke_all_privileges(self, user):
	cursor = self._connection.cursor()
	try:
	    cursor.execute("REVOKE ALL PRIVILEGES, GRANT OPTION FROM %s" % user)
	except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False
        finally:
            cursor.close()

	return True

    def execute_admin_query(self, sql):
	cursor = self._connection.cursor()
	try:
	    cursor.execute(sql)
	except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return False
        finally:
            cursor.close()

	return True
