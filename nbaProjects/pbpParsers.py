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
k_bins = np.arange(-30, 31, 1)


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
            if team == homeCity:
              scoreDiff = calculateScoreDiff(score)
            else:
              scoreDiff = -calculateScoreDiff(score)

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
    playerDataArray.append([playerName, []])

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

# create histogram data for each player
# takes playerDataArray with numpy arrays
# returns list of histogram data
def arrayToHist(playerDataArray):
  histData = []
  for playerDiff in playerDataArray:
    if playerDiff[1].size != 0:
      # diffs are the first column in the array
      diffs = playerDiff[1][ : , 0]
      # weights are the shot types, in the second column
      weights = playerDiff[1][ : , 1]
      playerHistData, edges = np.histogram(diffs, weights = weights, bins = k_bins)
      histData.append([playerDiff[0], playerHistData])

# returns all shot data in a list, numpyPlayerDataArray
# numpyPlayerDataArray[0] = players name
# numpyPlayerDataArray[1] = players data as numpy array
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
  for playerData in playerDataArray:
    print "Createing Histogram for {0}".format(playerData[0])
    if playerData[1].size == 0:
      # if there is no data for the player, fuck it
      break

    # diffs are in 4th column
    diffs = playerData[1][ : , 4]
    # weights (points scored) are in the 2nd column
    weights = playerData[1][ : , 2]

    # playerHistData, edges = np.histogram(diffs, weights = weights, bins = k_bins)

    plt.hist(diffs, bins=k_bins, weights=weights)
    plt.title(playerData[0])
    plt.xlim(k_bins[0], k_bins[-1])
    plt.xlabel('Score Diff')
    plt.ylabel('Points')

    playerName = playerData[0].replace(" ", "")
    saveLocation = (dataDir.k_histDir + playerName + ".png")
    plt.savefig(saveLocation)

firstHistogram(getShotData())
