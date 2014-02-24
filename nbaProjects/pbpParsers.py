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


# returns a list of all the play by play xml files
def getPBPFiles():
  playByPlayFiles = [ f for f in listdir(dataDir.k_pbpDir) if isfile(join(dataDir.k_pbpDir ,f)) ]
  return playByPlayFiles

# returns a list of the first ten games in the play by play xml files
# used for testing
def getTenPBPFiles():
  playByPlayFiles = [ f for f in listdir(dataDir.k_pbpDir) if isfile(join(dataDir.k_pbpDir ,f)) ]
  return playByPlayFiles[:10]

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


# accepts a teams nickname
# returns the teams city in all capitals
# TODO - find a solution for Los Angeles
def nickToCity(nickname, teams):
  '''
  teamsFileString = (k_teamsFile)
  teamsFile = open(teamsFileString)
  teamData = json.load(teamsFile)
  teamsFile.close()

  teams = teamData['teams']
  '''
  for team in teams:
    if nickname == team['nickname']:
      city = team['location']

  return city.upper()

# creates a list that will hold play by play data for units
# takes the teamsData list from json
# returns a list of all the teams and a blank list for units
def createUnitPBPArray(teams):
  unitPBPData = {}
  for team in teams:
    unitPBPData[team['nickname']] = []
  return unitPBPData

# finds or creates a list for a units data in the unitData
# takes oUnit_str - a string listing the players on offense
# takes a list of all the units on a team
# if the unit already exists, returns that units list of pbpData
# if the unid dne, creates a new list to return
#
# TODO - make sure the units are always in the same order
# if they aren't, then comparison needs to be beefed up
def findOrAddUnit(unit_str, teamData):
  players = unit_str.split(', ')
  for unit in teamData:
    if unit[0] == players:
      return unit
  teamData.append([players, []])
  return teamData[-1]

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


# takes a unitPBPData list and fills it out while parsing out a play by play data file
def unitPlayByPlayParser(file, unitData, teamData):
  try:
    gameTree = ET.parse(dataDir.k_pbpDir + file)
    game = gameTree.getroot()

    homeTeam = game.findtext('home-team')
    homeCity = nickToCity(homeTeam, teamData)
    awayTeam = game.findtext('away-team')
    awayCity = nickToCity(awayTeam, teamData)
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
        oUnit = findOrAddUnit(oUnit_str, unitData[oTeam])

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
          oUnit[1].append([category, player, totalTime, scoreDiff, value])

  except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
  except ET.ParseError as e:
    errorStr = expat.ErrorString(e.code)
    print "Parser Error({0}) in file {1}, position {2}".format(errorStr, file, e.position)

# parse all of the shot data from a single game into an array
# accepts a file to parse and the playerDataArray to fill out
# retruns the filled out playerDataArray
def playerShotsParser(file, playerDataArray):
  try:
    gameTree = ET.parse(dataDir.k_pbpDir + file)
    game = gameTree.getroot()

    homeTeam = game.findtext('home-team')
    homeCity = nickToCity(homeTeam)
    awayTeam = game.findtext('away-team')
    awayCity = nickToCity(awayTeam)

    print "parsing {0} at {1}".format(awayCity, homeCity)

    periodCount = int(0)
    # parse through each period
    for period in game.iter('period'):
      periodCount += 1

      # parse through each possesion
      for possession in period.iter('possession'):
        team = possession.findtext('team')

        # TODO(zap) - parse through all offensive players and
        # log the diff for them.  we'll use this to weight things
        # in a little bit

        # parse through each event
        for event in possession.iter('event'):
          category = event.findtext('category')

          # if we have a 'made shot' then log it
          if category == 'Made Shot':
            # get the time, shot type, player, and score diff
            time = event.findtext('time')
            totalTime = calculateTotalTime(time, periodCount)
            shotType = int(event.findtext('shottype'))
            player = event.findtext('player')
            score = event.findtext('score')
            if team == homeCity:
              scoreDiff = calculateScoreDiff(score)
            else:
              scoreDiff = -calculateScoreDiff(score)

            # rotate through the players and add data to the one who shot
            for playerData in playerDataArray:
              if playerData[0] == player:
                playerData[1].append([periodCount, totalTime, shotType, shotType, scoreDiff])

          # if we have a 'missed shot' then log that
          if category == 'Missed Shot':
            #get the time, shot type, player, and score diff
            time = event.findtext('time')
            totalTime = calculateTotalTime(time, periodCount)
            shotType = int(event.findtext('shottype'))
            player = event.findtext('player', '')
            score = event.findtext('score')
            if team == homeCity:
              scoreDiff = calculateScoreDiff(score)
            else:
              scoreDiff = -calculateScoreDiff(score)

            # rotate through players and add data to the one who shot
            for playerData in playerDataArray:
              if playerData[0] == player:
                playerData[1].append([periodCount, totalTime, shotType, 0, scoreDiff])

          # if we have a 'made free throw' then log that
          if category == 'Made Free Throw':
            #get the time, shot type, player, and score diff
            time = event.findtext('time')
            totalTime = calculateTotalTime(time, periodCount)
            player = event.findtext('player', '')
            score = event.findtext('score')
            if team == homeCity:
              scoreDiff = calculateScoreDiff(score)
            else:
              scoreDiff = -calculateScoreDiff(score)

            # rotate through players and add data to the one who shot
            for playerData in playerDataArray:
              if playerData[0] == player:
                playerData[1].append([periodCount, totalTime, 1, 1, scoreDiff])

          # if we have a 'missed free throw' then log that
          if category == 'Missed Free Throw':
            #get the time, shot type, player, and score diff
            time = event.findtext('time')
            totalTime = calculateTotalTime(time, periodCount)
            player = event.findtext('player', '')
            score = event.findtext('score')
            if team == homeCity and score:
              scoreDiff = calculateScoreDiff(score)
            elif team == awayCity and score:
              scoreDiff = -calculateScoreDiff(score)
            else:
              scoreDiff = 0

            # rotate through players and add data to the one who shot
            for playerData in playerDataArray:
              if playerData[0] == player:
                playerData[1].append([periodCount, totalTime, 1, 0, scoreDiff])

  except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
  except ET.ParseError as e:
    errorStr = expat.ErrorString(e.code)
    print "Parser Error({0}) in file {1}, position {2}".format(errorStr, file, e.position)

# setup a list that has each player in it.
# first element is player name (full)
# second element is a blank list
def setupPlayerDataArray():
  print "setting up player data array."
  playersFileString = (k_playersFile)
  playersFile = open(playersFileString)
  playerData = json.load(playersFile)
  playersFile.close()

  playerDataArray = []
  players = playerData['players']
  for player in players:
    playerName = player['firstName'] + ' ' + player['lastName']
    playerDataArray.append([playerName, [], []])

  return playerDataArray

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

# returns all shot data in a list, numpyPlayerDataArray
# numpyPlayerDataArray[0] = players name
# numpyPlayerDataArray[1] = players data as numpy array
# numpyPlayerDataArray[2] = point diffs when on court
# numpyArray[0] = period
# numpyArray[1] = totalTime
# numpyArray[2] = shotType (1, 2, 3)
# numpyArray[3] = points scored
# numpyArray[4] = scoreDiff
def getShotData():
  games = getPBPFiles()
  playerDataArray = setupPlayerDataArray()
  for game in games:
    playerShotsParser(game, playerDataArray)
  return numpyPlayerDataArray(playerDataArray)

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

# firstHistogram(getShotData())
k_teamsData = dataDir.getTeamData()
unitDataList = createUnitPBPArray(k_teamsData)
for pbpFile in getTenPBPFiles():
  unitPlayByPlayParser(pbpFile, unitDataList, k_teamsData)
