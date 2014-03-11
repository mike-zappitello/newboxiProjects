'''
copyright mzappitello 2014
parser class to grab the data from all of the play by play data for each
game. converts each event into an entry into a numpy array to be used in analysis.
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
    self.unitsByTeamNumpy = {}
    for team in self.teams:
      self.unitsByTeam[team['nickname']] = []
      self.unitsByTeamNumpy[team['nickname']] = []

    # setup empty players by team dict
    self.playersByTeam = {}
    self.playersByTeamNumpy = {}
    for team in self.teams:
      players = team['roster']
      self.playersByTeam[team['nickname']] = []
      self.playersByTeamNumpy[team['nickname']] = []
      for player in players:
        playerName = player['first_name'] + ' ' + player['last_name']
        self.playersByTeam[team['nickname']].append([playerName, []])

    # init bools to keep track of what we've parsed
    # we'll test against this before we parse through everything
    #
    # TODO - seupt a list of games that we've parsed and check against that
    # before we start parsing
    self.players_parsed = False
    self.units_parsed = False

  # helper function for quick debugging
  def debug(self):
    self.getTenPBPFiles()
    self.parseUnitEvents()
    self.numpyUnitsByTeam()
    print self.unitsByTeamNumpy

  # helper function to create, fill and return unitsByTeamNumpy
  # retruns filled out unitsByTeamNumpy
  def numpyUnitsData(self, debug = False):
    if debug:
      self.getTenPBPFiles()
    else:
      self.getPBPFiles()

    # if we haven't parsed units, do it
    if not self.units_parsed:
      self.parseUnitEvents()
      self.numpyUnitsByTeam()

    return self.unitsByTeamNumpy

  # helper function to create, fill and return playersByTeamNumpy
  # retruns filled out unitsByTeamNumpy
  # TODO(me) - create a bool to see test against if we've already parsed
  def numpyPlayersData(self, debug = False):
    if debug:
      self.getTenPBPFiles()
    else:
      self.getPBPFiles()

    # if we haven't parsed players, do it
    if not self.players_parsed:
      self.parsePlayerShots()
      self.numpyPlayersByTeam()

    return self.playersByTeamNumpy

  # loads a list of all the play by play xml files
  def getPBPFiles(self):
    self.playByPlayFiles = [ f for f in listdir(dataDir.k_pbpDir) if isfile(join(dataDir.k_pbpDir ,f)) ]

  # loads a list of the first ten games in the play by play xml files
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
        city = team['location'].upper()

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
            firstEvent = True
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
              raise ET.ParseError()

            # find the unit in the data array or add it
            oUnit = self.findOrAddUnit(oUnit_str, self.unitsByTeam[oTeam])

            # record all the events of the possesion in the oUnit list
            for event in possession.iter('event'):
              # get an index for the category
              category = categoryToIndex(event.findtext('category'))

              # get the player
              player = event.findtext('player')
              if not player:
                player = ""

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
              else:
                value = int(value)

              init = 0
              if firstEvent:
                init = 1

              # add the event to the units event list
              oUnit[1].append([category, player, init, totalTime, scoreDiff, value])
              firstEvent = False

      # note that we parsed the units
      self.units_parsed = True

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

      # note that we parsed for players
      self.players_parsed = True

    except IOError as e:
      print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except ET.ParseError as e:
      errorStr = expat.ErrorString(e.code)
      print "Parser Error({0}) in file {1}, position {2}".format(errorStr, file, e.position)

  # convert unitsByTeam to user numpy arrays so we can fuck with them
  def numpyUnitsByTeam(self):
    print "converting units by team to numpy"
    for team in self.teams:
      unitsData = self.unitsByTeam[team['nickname']]
      for unitData in unitsData:
        self.unitsByTeamNumpy[team['nickname']].append(
          [unitData[0],
          np.array(unitData[1], dtype=np.object)])

  # conver playersByTeam to use numpy arrays so we can fuck with them
  def numpyPlayersByTeam(self):
    print "converting players by team to numpy"
    ''' Structure of our numpy array
    meta = [
      {"name": "Period", "units": "none"}
      {"name": "Time", "units": "sec"},
      {"name": "ShotType", "units": "points"},
      {"name": "PointsScored", "units": "points"},
      {"name": "ScoreDiff", "units": "points"}
    ]
    '''
    for team in self.teams:
      rosterData = self.playersByTeam[team['nickname']]
      rosterDataNumpy = self.playersByTeamNumpy[team['nickname']]
      for playerData in rosterData:
        self.playersByTeamNumpy[team['nickname']].append([playerData[0], np.array(playerData[1])])

