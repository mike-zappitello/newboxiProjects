'''
functions to grab the data from all of the games and parse them into
data sets that fit the analysis that i'm trying to run
'''

import xml.etree.ElementTree as ET
import xml.parsers.expat as expat
from os import listdir
from os.path import isfile, join, exists
import re
import json
import numpy as np
import dataDirs as dataDir

k_teamsFile = (dataDir.k_teamsDir + 'teams.json')


def getPBPFiles():
  schedulefiles = [ f for f in listdir(dataDir.k_pbpDir) if isfile(join(dataDir.k_pbpDir ,f)) ]
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
def playerPointsHistParser(file, diffs):
  try:
    gameTree = ET.parse(dataDir.k_pbpDir + file)
    game = gameTree.getroot()

    homeTeam = game.find('home-team').text
    homeCity = nickToCity(homeTeam)
    awayTeam = game.find('away-team').text
    awayCity = nickToCity(awayTeam)

    if homeTeam != 'Thunder' and awayTeam != 'Thunder':
      return

    for period in game.iter('period'):
      for possession in period.iter('possession'):
        team = possession.find('team').text
        for event in possession.iter('event'):
          category = event.find('category').text
          if category == 'Made Shot':
            # time = event.find('gametime')
            shotType = int(event.find('shottype').text)
            player = event.find('player').text
            score = event.find('score').text
            if team == homeCity:
              scoreDiff = calculateScoreDiff(score)
            else:
              scoreDiff = -calculateScoreDiff(score)
            if player == 'Kevin Durant':
              diffs.append([scoreDiff, shotType])

  except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
  except ET.ParseError as e:
    errorStr = expat.ErrorString(e.code)
    print "Parser Error({0}) in file {1}, position {2}".format(errorStr, file, e.position)

games = getPBPFiles()
diffs = []
for game in games:
  playerPointsHistParser(game, diffs)

# diffs is a 2xn array of the score diff and the points made in each row
diffs = np.array(diffs)
print diffs
# print the total number of points
print diffs.sum(axis=0)[1]
