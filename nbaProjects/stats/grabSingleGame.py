import urllib2
import xml.etree.ElementTree as ET
import MySQLdb as mdb
import db

# take in a players name and team and make sure we have an entry in the players table
# return the index of the player
def playerID(playerName):
  con = db.connect_to_mysql()
  if con:
    try:
      # some expression that checks for a player
		  cur = con.cursor()
      cur.execute('')
      # todo - interpret the results from the mysql to get the ID
    except mdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
    con.close()

# take in a lineup and make sure we have an entry in the lineups table
# retun the index of that lineup
def lineupID(lineup):
  con = db.connect_to_mysql()
  if con:
    try:
      players = lineup.text.split(", ")
      playerIds = []
      for player in players:
        playerIds.append(playerID(player))

      playerIds.sort()

      # some expression that checks for a lineup
		  cur = con.cursor()
      cur.execute('')
      # todo - interpret the results from the mysql to get the ID
    except mdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
    con.close()

#log all of the data from the xml file into the db
def logGame(file):
  #file = 'dataFiles/Raptors-Celtics.xml'
  gameTree = ET.parse(file)
  game = gameTree.getroot()

  homeTeam = game.find('home-team')
  awayTeam = game.find('away-team')
  gameId = game.find('id')

  for period in game.iter('period'):
    for possession in period.iter('possession'):
      team = possession.find('team')
      homePlayers = possession.find('home-players')
      homeLineupId = lineupID(homePlayers)
      awayPlayers = possession.find('away-players')
      awayLineupId = lineupID(awayPlayers)

      for event in possession.iter('event'):
        category = event.find('category')
        time = event.find('gametime')
        shotType = event.find('shottype')
        player = event.find('player')
