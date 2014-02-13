import urllib2
from HTMLParser import HTMLParser
import dataDirs as dataDir
import json

# url containing roster data
k_baseUrl = 'http://www.eskimo.com/~pbender/rosters.html'

# create subclass and override the handler methods?
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

# get the html from the roster url and parse it out
def parseRoster():
  roster_page = urllib2.urlopen(k_baseUrl)
  roster_page_html_shitty = roster_page.read()
  roster_page.close()
  roster_page_html = roster_page_html_shitty.replace("#", "")

  theHTMLparser = rosterHTMLParser()
  return theHTMLparser.print_pre_contents(roster_page_html)

def teamsData():
  teamsFileString = (dataDir.k_teamsDir + 'teams.json')
  teamsFile = open(teamsFileString)
  teamData = json.load(teamsFile)
  teamsFile.close()
  return teamData['teams']

def combineData(htmlData, jsonData):
  leagueRoster = []
  # for each team
  for hTeam in htmlData:
    print hTeam
    # split the html team data by line and look at each line
    teamArray = hTeam.split('\n')
    for playerLine in teamArray:
      # for this site, if a line conatains '...' its a platyer
      if '...' in playerLine:
        # split each line by a ' '
        # 0 - player number
        # 1 - first name
        # 2 - last name
        # 3 - "...." place holder
        # 4 - position
        # 5 - height
        # 6 - weight
        # 7 - birthday
        # 8 - college
        # 9 - experience
        info = playerLine.split()
        print info
        if info[0] == "3?*Shawne":
          player = {
            'firstName' : "Shawne",
            'lastName' : info[1],
            'number' : "3",
            'height' : info[4],
            'weight' : info[5],
            'position' : info[3],
            'experience' : info[8],
            'born' : info[5],
            'college' : info[7]
          }
        elif info[1] == "Mirza":
          player = {
            'firstName' : info[1],
            'lastName' : info[2],
            'number' : info[0],
            'height' : info[5],
            'weight' : info[6],
            'position' : info[4],
            'experience' : "1",
            'born' : info[6],
            'college' : info[8]
          }
        elif info[1] == "Nene":
          player = {
            'firstName' : info[1],
            'lastName' : "",
            'number' : info[0],
            'height' : info[4],
            'weight' : info[5],
            'position' : info[3],
            'experience' : info[7],
            'born' : info[5],
            'college' : info[7]
          }
        else:
          player = {
            'firstName' : info[1],
            'lastName' : info[2],
            'number' : info[0],
            'height' : info[5],
            'weight' : info[6],
            'position' : info[4],
            'experience' : info[9],
            'born' : info[6],
            'college' : info[8]
          }
        leagueRoster.append(player)
  return leagueRoster

def saveData(dataAsList):
  jsonRoster = json.dumps(dataAsList, sort_keys=True, indent=2)
  jsonFile = open(dataDir.k_rosterDir + 'leagueRoster.json', 'w')
  jsonFile.write(jsonRoster)
  jsonFile.close()

saveData(combineData(parseRoster(), teamsData()))
