import MySQLdb as mdb
import sys
import db

con = db.connect_to_mysql()

if con:
	cur = con.cursor()
	cur.execute("SELECT * FROM playerRoster")
	table=cur.fetchall()
	for element in table:
		try:
			cur.execute('DELETE FROM playerRoster WHERE first_name = "%s" AND last_name = "%s" AND player_id > "%d"' % (element[2], element[1], element[0]))
					
		except mdb.Error, e:
			print "ERROR %d: %s" % (e.args[0], e.args[1])

	con.close()
