import sys
import MySQLdb as mdb
from HTMLParser import HTMLParser
import db
import urllib2

class handlerHTMLParser(HTMLParser):
		def print_li_contents(self, html):
			self.tag_stack = ['dummy']
			self.player_name = ''
			self.player_info = [[]]
			self.feed(html)
			return self.player_info

		def handle_starttag(self, tag, attrs):
			self.tag_stack.append(tag)

		def handle_endtag(self, tag):
			if len(self.tag_stack) > 0:
				self.tag_stack.pop()

		def handle_data(self, data):
			if len(self.tag_stack) > 0 and self.tag_stack[-1] == 'li':
				self.player_name = data

			elif len(self.tag_stack) > 0 and self.tag_stack[-1] == 'a' and self.tag_stack[-2] == 'li':
				row = [self.player_name, data]
				self.player_info.append(row)
				
url = 'http://hoopeduponline.com/2009/03/30/a-list-of-every-nba-player-on-twitter/'

handler_page = urllib2.urlopen(url)
handler_page_html = handler_page.read()
handler_page.close()

html_parser = handlerHTMLParser()
shitty_handler_list = html_parser.print_li_contents(handler_page_html)

handler_list = [[]]

for element in shitty_handler_list:
	if len(element)>1:
		if '@' in element[1]:
			names =  element[0].split(' ')
			row = [names[0], names[1], element[1]]
			handler_list.append(row)


handler_list.append(['Kawhi', 'Leonard', '@TheBig_Island'])
handler_list.append(['Jermy', 'Lin', '@JLin7'])
handler_list.append(['Kobe', 'Bryant', '@kobebryant'])
handler_list.append(['Jermaine', "O'Neal", '@jermainoneal'])
handler_list.append(['Maurice', 'Williams', '@mowilliams'])
handler_list.append(['Leandro', 'Barbosa', '@leandrinhooo20'])
handler_list.append(['Amare', 'Stoudemire', '@Amareisreal'])
handler_list.append(['Derrick', 'Rose', '@drose'])
handler_list.append(['LeBron', 'James', '@KingJames'])
handler_list.append(['Udonis', 'Haslem', '@ThisIsUD'])
handler_list.append(['Kyle', "O'Quinn", '@KO_STAT_2'])
handler_list.append(["E'Twaun", 'Moore', '@ETwaun55'])

con = db.connect_to_mysql()

if con:
	cur = con.cursor()
	for player in handler_list:
		if len(player)>1:
			try:
				cur.execute('UPDATE playerRoster SET twitter_handle = "%s" WHERE first_name = "%s" AND last_name = "%s"' % (player[2], player[0], player[1]))
				print cur.fetchall()

			except mdb.Error, e:
				print "Error %d: %s" % (e.args[0], e.args[1])

	con.close()
