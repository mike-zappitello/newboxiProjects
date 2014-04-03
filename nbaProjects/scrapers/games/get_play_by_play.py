'''
python scrip used to get the play by play for each game from
'http://www.cs.umd.edu/hcil/eventflow/NBA/nbaData.shtml' using the
team schedules.
'''

from os import listdir
from os.path import isfile, join, exists
import json
import re
import urllib2
import dataDirs as dataDir

k_baseUrl = ('http://www.cs.umd.edu/hcil/eventflow/NBA/gameFiles/')

# returns all of the schecdule files is dataDir.k_scheduleDir
def getScheduleFiles():
  schedulefiles = [ f for f in listdir(dataDir.k_scheduleDir) if isfile(join(dataDir.k_scheduleDir ,f)) ]
  return schedulefiles

# takes in a base name for a json dict in dataDir.k_scheduleDir
# takes the a json dict of team data
# returns a dict of all baseUrls for xml data
def getGames(baseName, teamData):
  fileToOpen = (dataDir.k_scheduleDir + baseName)
  f = open(fileToOpen)
  data = json.load(f)
  f.close()

  homeTeam = ''
  homeTeamUgly = re.sub('\.json$', '', baseName)
  teams = teamData['teams']
  for team in teams:
    if homeTeamUgly == team['full_name']:
      homeTeam = team['nickname']

  gameStrings = []
  games = data['schedule']
  homeGames = []
  for game in games:
    if game['isHomeGame']:
      month = str(game['when']['month']).zfill(2)
      day = str(game['when']['day']).zfill(2)
      if game['when']['month'] < 9:
        year = str(14)
      else:
        year = str(13)

      dateString = month + day + year
      awayTeam = game['opponent']['nickname']
      if awayTeam == 'Trail Blazers':
        awayTeam = 'TrailBlazers'
      gameString = homeTeam + '-' + awayTeam + '-' + dateString +  ".xml"
      gameStrings.append(gameString)

  return gameStrings

# returns a dict of all game strings
def getAllGames():
  scheduleFiles = getScheduleFiles()

  teamsFileString = (dataDir.k_teamsDir + 'teams.json')
  teamsFile = open(teamsFileString)
  teamData = json.load(teamsFile)
  teamsFile.close()

  gameStrings = []
  for scheduleFile in scheduleFiles:
    if scheduleFile != 'teams.json':
      games = getGames(scheduleFile, teamData)
      for game in games:
        gameStrings.append(game)

  return gameStrings

# pings all game urls to see whats what
def saveGames():
  gameStrings = getAllGames()

  for gameString in gameStrings:
    gameUrl = k_baseUrl + gameString
    try:
      gameFileString = dataDir.k_pbpDir + gameString
      if not isfile(gameFileString):
        print "saving game {0}".format(gameString)
        print "url: {0}".format(gameUrl)
        gamePage = urllib2.urlopen(gameUrl)
        gameData = gamePage.read()
        gamePage.close()
        gameFile = open(gameFileString, 'w+')
        gameFile.write(gameData)
        gameFile.close()
    except urllib2.URLError as e:
      print "URL Error({0}): {1}".format(e.errno, e.strerror)

saveGames()
