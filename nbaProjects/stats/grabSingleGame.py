import xml.etree.ElementTree as ET

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
