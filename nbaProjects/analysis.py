'''
copyright mzappitello 2014

methods that take data in form of lists of numpy arrays and runs analysis on it.
'''
import numpy as np
import dataDirs as dataDir
import matplotlib as ml
import matplotlib.pyplot as plt
from playByPlayPasrer import playByPlayParser as parser

'''
TODO
-- create a class for analysis
* it has a parser as a member
* there are some bools to see if we have parsed things already
* methods for analysis
* methods to take numpy arrays and apply analsys methods to them

'''

class analyzer():
  def __init__:
    self.parser = parser()

  def unitAnalysis(method):
    units_by_team_data = parser.numpyUnitsData()
    for team in self.parser.teams:
      units_data = units_by_team[team['nickname']]
      for unit in units_data:
        method(unit)

  def playerAnalysis(method):
    players_by_team_data = parser.numpyPlayersData()
    for team in self.parser.teams:
      players_data = players_by_team[team['nickname']]
      for player in player_data:
        method(player)

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

