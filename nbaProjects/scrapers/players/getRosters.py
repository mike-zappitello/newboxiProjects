import urllib2
from HTMLParser import HTMLParser
import dataDirs as dataDir
import json
import re

# url containing roster data
k_baseUrl = 'http://www.eskimo.com/~pbender/rosters.html'

# open up the team json file
# create a json string with our new team data
# save and close the file
def saveTeamData(teamData):
  teamsFileString = (k_teamsFile)
  teamsFile = open(teamsFileString, 'w')
  newData = {'teams' : teamData}
  newTeamsData = json.dumps(newData,sort_keys=True, indent=2, separators=(",", ":"))
  teamsFile.write(newTeamsData)
  teamsFile.close()

# class to parse the k_baseUrl for teams
class rosterHTMLParser(HTMLParser):
  # parse and return the updated team data
  def start_parse(self, html, teamData):
    self.teamData = teamData
    self.players = []
    self.tag_stack = []
    self.feed(html)
    return self.teamData

  # handles the starting tags
  # if the tag is A then we have a new team and we call setCurrentTeam
  # if the tag is PRE then we append it to our tag stack and will collect data
  def handle_starttag(self, tag, attrs):
    if (tag == "a" and attrs and attrs[0][0] == "name"):
      self.setCurrentTeam(attrs[0][1])
    elif (tag == "pre"):
      self.tag_stack.append(tag)

  # handles the end tags
  # we only care about PRE, as its the only thing that will be in our tag stack
  def handle_endtag(self, tag):
    if self.tag_stack:
      self.tag_stack.pop()

  # if the tag stack has an element, its PRE, and we need to parse the data
  def handle_data(self, data):
    if self.tag_stack:
      self.currentTeamData['roster'] = self.parseData(data)

  # handle a data string
  # for each line i throw it through some ugly regex
  # if it passes we have a player and we create a dict for that player
  # return a list of thoes player dicts
  def parseData(self, data):
    lines = data.split('\n')
    players = []
    for line in lines:
      match = re.match(r"^\s?((?P<number>\d{1,2})|\?\?)(\s|\?|\*)*(?P<first_name>(\w|')*)\s?(?P<last_name>(\w|')*)\s*\.*\s*(?P<position>\w-?\w?)\s*(?P<height>\d-\d{1,2})\s*(?P<weight>\d{3})\s*(?P<birthday>\d{1,2}/\d{1,2}/\d{2})\s*(?P<the_rest>.*)", line)
      if match:
        player = {}
        player['number'] = match.group('number')
        player['first_name'] =  match.group('first_name')
        player['last_name'] =match.group('last_name')
        player['position'] = match.group('position')
        player['height'] = match.group('height')
        player['weight'] = match.group('weight')
        player['birthday'] = match.group('birthday')

        the_rest = match.group('the_rest').split()
        player['experience'] = the_rest.pop()
        college = ''
        for word in the_rest:
          college = college + word + ' '
        player['college'] = college.rstrip()
        players.append(player)

    return players

  # takes a team abbreviation from the website
  # fixes the abbr for the four teams that have weird abbrevs
  # searches through team list for the right abbrev
  # set the current team data to that team
  def setCurrentTeam(self, teamAbbr):
    # fix for bad abbrs
    if teamAbbr == 'pho':
      teamAbbr = 'phx'
    elif teamAbbr == 'uta':
      teamAbbr = 'utah'
    elif teamAbbr == 'bro':
      teamAbbr = 'bkn'
    elif teamAbbr == 'was':
      teamAbbr = 'wsh'
    for team in self.teamData:
      if teamAbbr == team['abbr']:
        self.currentTeamData = team
        return

# get the html from the roster url
def getRosterHtml():
  roster_page = urllib2.urlopen(k_baseUrl)
  roster_page_html = roster_page.read()
  roster_page.close()
  # have to get rid of '&' symbols as it fucks things up
  roster_page_clean = ''
  for line in roster_page_html:
    if line != "&":
      roster_page_clean = roster_page_clean + line
  return roster_page_html

def saveData(dataAsList):
  jsonRoster = json.dumps(dataAsList, sort_keys=True, indent=2)
  jsonFile = open(dataDir.k_rosterDir + 'leagueRoster.json', 'w')
  jsonFile.write(jsonRoster)
  jsonFile.close()

# setup the parser, get the html, parse it, and save the new stuff
parser = rosterHTMLParser()
teamData = dataDir.getTeamData()
newData =  parser.start_parse(getRosterHtml(), teamData)
saveTeamData(newData)
