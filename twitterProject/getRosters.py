import urllib2
from HTMLParser import HTMLParser
import MySQLdb as mdb
import sys
import db

#create subclass and override the handler methods?
class rosterHTMLParser(HTMLParser):
	def print_pre_contents(self, html):
		self.tag_stack = ["dummy"]
		self.roster_stack = []
		self.feed(html)
		return self.roster_stack

	def handle_starttag(self, tag, attrs):
		self.tag_stack.append(tag)

	def handle_endtag(self, tag):
		if len(self.tag_stack) > 0:
			self.tag_stack.pop()

	def handle_data(self, data):
		if len(self.tag_stack) > 0 and  self.tag_stack[-1] == 'pre':
			self.roster_stack.append(data)

url = 'http://www.eskimo.com/~pbender/rosters.html'

roster_page = urllib2.urlopen(url)
roster_page_html_shitty = roster_page.read()
roster_page.close()
roster_page_html = roster_page_html_shitty.replace("#", "")

theHTMLparser = rosterHTMLParser()
roster_list = theHTMLparser.print_pre_contents(roster_page_html)

players = [[],[]]

for team in roster_list:
	team_array = team.split('\n')
	for player_line in team_array:
		if '...' in player_line:
			info = player_line.split(' ')
			#they have a one digit jersey number
			if len(info[0])==0:
				if ".." not in info[4]:
					players.append([info[4],info[3]])
				else:
					players.append([info[3],info[2]])
			#they have a two digit jersey number
			else:
				if '..' not in info[3]:
					players.append([info[3],info[2]])
				else:
					players.append([info[2],info[1]])

con = db.connect_to_mysql()

if con:
	try:
		cur = con.cursor()
		for baller in players:
			if len(baller)>1:	
				cur.execute('INSERT INTO playerRoster(last_name,first_name) VALUES("%s","%s")' % (baller[0],baller[1]))
				print cur.fetchall()

	except mdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])

	con.close()
