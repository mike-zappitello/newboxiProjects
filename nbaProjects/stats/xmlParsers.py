'''
functions to grab the data from all of the games and parse them into
data sets that fit the analysis that i'm trying to run
'''

import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join, exists
import re
import json

k_pbpDir = ('/usr/home/mzappitello/infographs/nbaProjects/stats/dataFiles/2013-2014-nba-schedule/data/playByPlay/')
k_teamsFile = ('/usr/home/mzappitello/infographs/nbaProjects/stats/dataFiles/2013-2014-nba-schedule/data/json/teams.json')


def getPBPFiles():
  schedulefiles = [ f for f in listdir(k_pbpDir) if isfile(join(k_pbpDir ,f)) ]
  return schedulefiles

# accepts a score as a string <int>-<int>
# returns the difference as home minus away
def calculateScoreDiff(scoreString):
  scores = re.match(r"(?P<away>\d{1,3})-(?P<home>\d{1,3})", scoreString)
  away = int(scores.group('away'))
  home = int(scores.group('home'))
  diff = home - away
  return diff

# accepts a teams nickname
# returns the teams city in all capitals
# TODO - find a solution for Los Angeles
def nickToCity(nickname):
  teamsFileString = (k_teamsFile)
  teamsFile = open(teamsFileString)
  teamData = json.load(teamsFile)
  teamsFile.close()

  teams = teamData['teams']
  for team in teams:
    if nickname == team['nickname']:
      city = team['location']

  return city.upper()

# parse all of the data from a single game into bins
# each bin is based on when the player made shots wrt score differential
# accepts a file to parse
# accepts bins to add them to?
# returns nothing?
def playerPointsHistParser(file):
  file = (k_pbpDir + '76ers-Bobcats-011514.xml')
  gameTree = ET.parse(file)
  game = gameTree.getroot()

  homeTeam = game.find('home-team').text
  homeCity = nickToCity(homeTeam)
  awayTeam = game.find('away-team').text
  awayCity = nickToCity(awayTeam)

  for period in game.iter('period'):
    for possession in period.iter('possession'):
      team = possession.find('team').text
      for event in possession.iter('event'):
        category = event.find('category')
        if category.text == 'Made Shot':
          # time = event.find('gametime')
          shotType = int(event.find('shottype').text)
          player = event.find('player').text
          score = event.find('score').text
          if team == homeCity:
            scoreDiff = calculateScoreDiff(score)
          else:
            scoreDiff = -calculateScoreDiff(score)

          print "{0} scored {1} points at diff {2}".format(player, shotType, scoreDiff)

games = getPBPFiles()
for game in games:
  playerPointsHistParser(game)
