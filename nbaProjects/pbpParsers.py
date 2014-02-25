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
import matplotlib as ml
import matplotlib.pyplot as plt
# import matplotlib.mlab as mlab

k_teamsFile = (dataDir.k_teamsDir + 'teams.json')
k_playersFile = (dataDir.k_rosterDir + 'leagueRoster.json')

# accepts a score as a string <int>-<int>
# returns the difference as home minus away
def calculateScoreDiff(scoreString):
  try:
    scores = re.match(r"(?P<away>\d{1,3})-(?P<home>\d{1,3})", scoreString)
    away = int(scores.group('away'))
    home = int(scores.group('home'))
    diff = home - away
    return diff
  except TypeError as e:
    # if the parse gets a none type insted of a string
    # just return 0 because we don't care anyway
    return 0

# accepts a time string and a period
# returns the total time elapsed in the game
def calculateTotalTime(timeString, period):
  periodTime = re.match(r"00:(?P<minutes>\d{1,3}):(?P<seconds>\d{1,3})\.(?P<microseconds>\d{1,3})", timeString)
  minutes = int(periodTime.group('minutes'))
  seconds = int(periodTime.group('seconds'))
  return (period * 12 + minutes) * 60 + seconds

# takes a category as a string
# returns a category as an int
def categoryToIndex(cat):
  categories = {
    'Jump Ball' : 0,
    'Dead Ball' : 0,
    'End of Period' : 0,
    'End of Game' : 0,
    'Defensive Rebound' : 1,
    'Offensive Rebound' : 2,
    'Made Free Throw' : 3,
    'Missed Free Throw' : 4,
    'Made Shot' : 5,
    'Missed Shot' : 6,
    'Foul' : 7,
    'Turnover' : 8,
    'Steal' : 9,
    'Block' : 10,
    'Timeout' : 11}
  try:
    return categories[cat]
  except KeyError as e:
    print 'Category {0} not found'.format(cat)
    return 0

class playByPlayParser():
  def __init__(self):
    #setup teams dict from teams.json using dataDir
    self.teams = dataDir.getTeamData()

    # setup empty units by team dict
    self.unitsByTeam = {}
    for team in self.teams:
      self.unitsByTeam[team['nickname']] = []

    # setup empty players by team dict
    self.playersByTeam = {}
    for team in self.teams:
      # playerData = []
      players = team['roster']
      self.playersByTeam[team['nickname']] = []
      for player in players:
        playerName = player['first_name'] + ' ' + player['last_name']
        self.playersByTeam[team['nickname']].append([playerName, [], []])

    self.getTenPBPFiles()

# returns a list of all the play by play xml files
  def getPBPFiles(self):
    self.playByPlayFiles = [ f for f in listdir(dataDir.k_pbpDir) if isfile(join(dataDir.k_pbpDir ,f)) ]

  # returns a list of the first ten games in the play by play xml files
  # used for testing
  def getTenPBPFiles(self):
    playByPlayFiles = [ f for f in listdir(dataDir.k_pbpDir) if isfile(join(dataDir.k_pbpDir ,f)) ]
    self.playByPlayFiles = playByPlayFiles[:10]

  # accepts a teams nickname
  # returns the teams city in all capitals
  # TODO - find a solution for Los Angeles
  def nickToCity(self, nickname):
    for team in self.teams:
      if nickname == team['nickname']:
        city = team['location']

    return city.upper()

  # finds or creates a list for a units data in the unitData
  # takes oUnit_str - a string listing the players on offense
  # takes a list of all the units on a team
  # if the unit already exists, returns that units list of pbpData
  # if the unid dne, creates a new list to return
  #
  # TODO - make sure the units are always in the same order
  # if they aren't, then comparison needs to be beefed up
  def findOrAddUnit(self, unit_str, teamData):
    players = unit_str.split(', ')
    for unit in teamData:
      if unit[0] == players:
        return unit
    teamData.append([players, []])
    return teamData[-1]

  # parses all of the play by play data for a unit
  # takes a file that contains play by play data in xml
  # takes a dict with lists for each team for the play by play data
  # takes team data as a dict from teams.json
  # returns the updated unit data
  def parseUnitEvents(self):
    try:
      for file in self.playByPlayFiles:
        gameTree = ET.parse(dataDir.k_pbpDir + file)
        game = gameTree.getroot()

        homeTeam = game.findtext('home-team')
        homeCity = self.nickToCity(homeTeam)
        awayTeam = game.findtext('away-team')
        awayCity = self.nickToCity(awayTeam)
        gameID = game.findtext('id')

        print "parsing {0} at {1}".format(awayCity, homeCity)

        periodCount = int(0)
        # parse through each period
        for period in game.iter('period'):
          periodCount += 1

          #parse through each possession
          for possession in period.iter('possession'):
            # get the team with the ball and their lineup
            team = possession.findtext('team')
            if team == homeCity:
              oTeam = homeTeam
              oUnit_str = possession.findtext('home-players')
            elif team == awayCity:
              oTeam = awayTeam
              oUnit_str = possession.findtext('away-players')
            else:
              print 'team {0} neq to {1} or {2}'.format(team, homeCity, awayCity)
              raise ET.ParseError(0, 'cutsom parse error')

            # find the unit in the data array or add it
            oUnit = findOrAddUnit(oUnit_str, self.unitsByTeam[oTeam])

            # record all the events of the possesion in the oUnit list
            for event in possession.iter('event'):
              # get an index for the category
              category = categoryToIndex(event.findtext('category'))

              # get the player
              player = event.findtext('player')

              # get the time and total time
              time = event.findtext('time')
              totalTime = calculateTotalTime(time, periodCount)

              # get the score diff
              score = event.findtext('score')
              if team == homeCity:
                scoreDiff = calculateScoreDiff(score)
              else:
                scoreDiff = -calculateScoreDiff(score)

              # get the value of the shot on the score
              value = event.findtext('shottype')
              if not value:
                value = 0

              # add the event to the units event list
              oUnit[1].append([category, player, totalTime, scoreDiff, value, inPossession])

    except IOError as e:
      print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except ET.ParseError as e:
      errorStr = expat.ErrorString(e.code)
      print "Parser Error({0}) in file {1}, position {2}".format(errorStr, file, e.position)

  # parse all of the shot data from a single game into an array
  # accepts a file to parse and the playerDataArray to fill out
  # retruns the filled out playerDataArray
  def parsePlayerShots(self):
    try:
      for file in self.playByPlayFiles:
        gameTree = ET.parse(dataDir.k_pbpDir + file)
        game = gameTree.getroot()

        homeTeam = game.findtext('home-team')
        homeCity = self.nickToCity(homeTeam)
        homeRoster = self.playersByTeam[homeTeam]
        awayTeam = game.findtext('away-team')
        awayCity = self.nickToCity(awayTeam)
        awayRoster = self.playersByTeam[awayTeam]

        print "parsing {0} at {1}".format(awayCity, homeCity)

        periodCount = int(0)
        # parse through each period
        for period in game.iter('period'):
          periodCount += 1

          # parse through each possesion
          for possession in period.iter('possession'):
            team = possession.findtext('team')

            # parse through each event
            for event in possession.iter('event'):
              category = categoryToIndex(event.findtext('category'))
    'Made Free Throw' : 3,
    'Missed Free Throw' : 4,
    'Made Shot' : 5,
    'Missed Shot' : 6,

              # if we have a 'made shot' then log it
              if (category == 3 or
                  category == 4 or
                  category == 5 or
                  category == 6):
                isHomeTeam = (team == homeCity)
                time = event.findtext('time')
                totalTime = calculateTotalTime(time, periodCount)
                player = event.findtext('player')
                score = event.findtext('score')
                if isHomeTeam:
                  scoreDiff = calculateScoreDiff(score)
                  players = homeRoster
                else:
                  scoreDiff = -calculateScoreDiff(score)
                  players = awayRoster

                # rotate through the players and add data to the one who shot
                for playerData in players:
                  if playerData[0] == player:
                    if (category == 5):
                      shotType = int(event.findtext('shottype'))
                      playerData[1].append([periodCount, totalTime, shotType, shotType, scoreDiff])
                    if (category == 3):
                      playerData[1].append([periodCount, totalTime, 1, 1, scoreDiff])
                    if (category == 6):
                      shotType = int(event.findtext('shottype'))
                      playerData[1].append([periodCount, totalTime, shotType, 0, scoreDiff])
                    if (category ==  4):
                      playerData[1].append([periodCount, totalTime, 1, 0, scoreDiff])

    except IOError as e:
      print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except ET.ParseError as e:
      errorStr = expat.ErrorString(e.code)
      print "Parser Error({0}) in file {1}, position {2}".format(errorStr, file, e.position)

# change playerDataArray to numpy arrays so we can fuck with them
# takes playerDataArray with python lists
# returns playerDataArray with numpy arrays
def numpyPlayerDataArray(playerDataArray):
  print "converting to numpy array"
  newPlayerDataArray = []
  ''' Structure of our numpy array
  meta = [
    {"name": "Period", "units": "none"}
    {"name": "Time", "units": "sec"},
    {"name": "ShotType", "units": "points"},
    {"name": "PointsScored", "units": "points"},
    {"name": "ScoreDiff", "units": "points"}
  ]
  '''
  for playerData in playerDataArray:
    newPlayerDataArray.append([playerData[0], np.array(playerData[1])])

  return newPlayerDataArray

def firstHistogram(playerDataArray):
  bins = np.arange(-36, 37, 2)
  for playerData in playerDataArray:
    if playerData[1].size == 0:
      # if there is no data for the player, fuck it
      print "No Player Data for {0}".format(playerData[0])
    else :
      print "Createing Histogram for {0}".format(playerData[0])

      # sort into three data sets based on points scored
      # NOT THE SAME AS SHOT TYPE!!!
      threes = playerData[1][playerData[1][ : , 3] == 3]
      twos = playerData[1][playerData[1][ : , 3] == 2]
      ones = playerData[1][playerData[1][ : , 3] == 1]

      # diffs are in 4th column
      threeDiffs = threes[ : , 4]
      twoDiffs = twos[ : , 4]
      oneDiffs = ones[ : , 4]
      diffs = [oneDiffs, twoDiffs, threeDiffs]
      # weights (points scored) are in the 3rd column
      threeWeight = threes[ : , 3]
      twoWeight = twos[ : , 3]
      oneWeight = ones[ : , 3]
      weights = [oneWeight, twoWeight, threeWeight]

      # draw histogram and label it
      plt.hist(diffs,
               bins=bins,
               weights=weights,
               rwidth=0.8,
               stacked=True,
               color=['red', 'blue', 'green'],
               label=["Free Throws", "Twos", "Threes"])
      plt.title(playerData[0])
      plt.xlim(bins[0], bins[-1])
      plt.xlabel('Score Diff')
      plt.ylabel('Points')
      plt.legend()

      # save and clear the plot
      playerName = playerData[0].replace(" ", "")
      saveLocation = (dataDir.k_histDir + playerName + ".png")
      plt.savefig(saveLocation)
      plt.clf()

