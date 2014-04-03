'''
opyright mzappitello 2014

methods that take data in form of lists of numpy arrays and runs analysis on it.
'''
import numpy as np
import dataDirs as dataDir
import matplotlib as ml
import matplotlib.pyplot as plt
from playByPlayParser import playByPlayParser as parser

'''
TODO
-- create a class for analysis
* there are some bools to see if we have parsed things already
* methods for analysis
* methods to take numpy arrays and apply analsys methods to them
'''

class analyzer():
  def __init__(self, debug = True):
    self.parser = parser()
    self.debug = debug

    # setup empty players by team dict
    self.players_by_team = {}
    for team in self.parser.teams:
      players = team['roster']
      self.players_by_team[team['nickname']] = {}
      for player in players:
        playerName = player['first_name'] + ' ' + player['last_name']
        self.players_by_team[team['nickname']][playerName] = [[], []]
        # self.players_by_team[team['nickname']].append([playerName, [], []])

  def unitAnalysis(self, method):
    units_by_team_data = self.parser.numpyUnitsData(self.debug)
    for team in self.parser.teams:
      units_data = units_by_team_data[team['nickname']]
      players_data = self.players_by_team[team['nickname']]
      for unit in units_data:
        method(unit, players_data)

  def playerAnalysis(self, method):
    players_by_team_data = self.parser.numpyPlayersData(self.debug)
    for team in self.parser.teams:
      players_data = players_by_team_data[team['nickname']]
      for player in players_data:
        method(player, self.parser.teams)

  def adjustedPointsHistogram(self):
    adjustedHistogrm(self.players_by_team)

def debugAnalysis(player_data, team_data):
  print "data for player {0}".format(player_data[0])

def adjustedPlayerHistograms(unit_data, players_data):
  bins = np.arange(-36, 37, 2)
  try:
    unit = unit_data[0]
    events = unit_data[1]
    initEvents = events[events[ : , 2] == 1]

    # add score diffs to each players data
    for player in unit:
      try:
        for event in initEvents:
          players_data[player][0].append([event[3], event[4]])
      except KeyError as e:
        print "player {0} not on team :|".format(player)

    # get all the made shots and add those to each players stats
    free_throws_made = events[events[ : , 0] == 3]
    shots_made = events[events[ : , 0] == 5]

    for free_throw in free_throws_made:
      try:
        player = free_throw[1]
        players_data[player][1].append([free_throw[4], free_throw[5]])
      except KeyError as e:
        print "plyaer {0} not on team :|".format(player)

    for shot in shots_made:
      try:
        player = shot[1]
        players_data[player][1].append([shot[4], shot[5]])
      except KeyError as e:
        print "plyaer {0} not on team :|".format(player)

  except IndexError  as e:
    print "index error !!!"

def adjustedHistogrm(players_dict):
  bins = np.arange(-36, 37, 2)
  teams = players_dict.keys()
  for team in teams:
    roster = players_dict[team].keys()
    for player in roster:
      on_court = np.array(players_dict[team][player][0])
      shots = np.array(players_dict[team][player][1])

      if shots.size == 0:
        print "{0} has no shots".format(player)
      else:
        print "generating hist for {0}".format(player)
        # sort into three data sets based on points scored
        threes = shots[shots[ : , 1] == 3]
        twos = shots[shots[ : , 1] == 2]
        ones = shots[shots[ : , 1] == 1]

        # get the diffs for each shot type
        threes_hist, unused = np.histogram(threes[ : , 0], bins)
        twos_hist, unused = np.histogram(twos[ : , 0], bins)
        ones_hist, unused = np.histogram(ones[ : , 0], bins)

        # get info about how the point diffs per player
        on_court_hist, unused = np.histogram(on_court, bins)
        on_court_float = np.array(on_court_hist, dtype = np.float64)
        total_possessions = np.sum(on_court_float)
        on_court_adj = np.array(on_court_float / total_possessions, dtype = np.float64)

        # adjust the histogram arrays with the on court adj * points scored
        threes_adj = threes_hist * on_court_adj * 3
        twos_adj = twos_hist * on_court_adj * 2
        ones_adj = ones_hist * on_court_adj * 1

        # draw the graph
        width = 0.7 * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:])
        plt.bar(center,
                on_court_hist,
                align = 'center',
                width = width,
                color = 'red')
        '''
        plt.bar(center,
                threes_adj,
                align = 'center',
                width = width,
                color = 'red')
        plt.bar(center,
                twos_adj,
                align = 'center',
                width = width,
                color = 'green',
                bottom = threes_adj)
        plt.bar(center,
                ones_adj,
                align = 'center',
                width = width,
                color = 'blue',
                bottom = threes_adj + twos_adj)
        '''

        plt.title(player)
        plt.xlim(bins[0], bins[-1])
        plt.xlabel('Score Diff')
        plt.ylabel('Possessions')

        # save and clear the plot
        playerName = player.replace(" ", "")
        saveLocation = (dataDir.k_histDir + playerName + ".png")
        plt.savefig(saveLocation)
        plt.clf()

def firstHistogram(playerDataArray, team_data):
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

a = analyzer(False)
a.unitAnalysis(adjustedPlayerHistograms)
a.adjustedPointsHistogram()
# print a.players_by_team
