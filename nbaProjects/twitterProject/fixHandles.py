import MySQLdb as mdb
import db

con = db.connect_to_mysql()

if con:
	cur = con.cursor()
	cur.execute("SELECT player_id, twitter_handle FROM playerRoster")
	players = cur.fetchall()

for baller in players:
	print baller
