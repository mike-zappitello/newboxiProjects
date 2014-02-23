# script to grap all of the datas for each team and add it to our
# json manifest for those teams
import urllib2
from HTMLParser import HTMLParser
import dataDirs as dataDir
import json
from os.path import isfile, join, exists

# url containing data info for all teams
k_logoUrl = ('http://www.sportslogos.net/teams/list_by_league/6/National_Basketball_Association/N/logos/')

# open up the team json file
# create a json string with our new team data
# save and close the file
def saveLogos(logoList):
  for logo in logoList:
    logoFile = "{0}{1}.gif".format(dataDir.k_logosDir, logo[0])
    if not isfile(logoFile):
      print "saving {0}".format(logoFile)
      u = urllib2.urlopen(logo[1])
      localFile = open(logoFile, 'w+')
      localFile.write(u.read())
      localFile.close()
      u.close()
    else:
      print "{0} already exists".format(logo[0])

# class that will take parse our logo url
class logoHTMLParser(HTMLParser):
  # function to start the parser taking in the url and old team data
  def start_parse(self, html, teamData):
    self.teamData = teamData
    self.logoList  = []
    self.tag_stack = []
    self.feed(html)
    return self.logoList

  # takes a title attribute and checks to see if it is a logo for one our teams
  # if it is, sets the current team info and returns true
  # if false returns false
  def isTeamLogo(self, title):
    try:
      for team in self.teamData:
        teamNameLogos = "{0} {1} Logos".format(team['city'], team['nickname'])
        if title == teamNameLogos:
          self.currentTeam = "{0}".format(team['full_name'])
          print teamNameLogos
          return True
    except UnicodeEncodeError as e:
      print "couldn't parse"

    return False

  # when we have a new starting tag, compares it against the thigns we care about
  def handle_starttag(self, tag, attrs):
    if (tag == "a"):
      for attr in attrs:
        if attr[0] == "title" and self.isTeamLogo(attr[1]):
          self.tag_stack.append(tag)
    elif (tag == "img" and self.tag_stack):
      logo = [self.currentTeam , attrs[0][1]]
      self.logoList.append(logo)

  # when we reach an end tag, checks with tag stack
  def handle_endtag(self, tag):
    if self.tag_stack and tag == self.tag_stack[-1]:
      self.tag_stack.pop()

# get the html from the logo url
# return the html as a string
def getLogoHtml():
  logo_page = urllib2.urlopen(k_logoUrl)
  logo_page_html = logo_page.read()
  logo_page.close()

  return logo_page_html

# setup the parser, get the html, parse it, and save the new stuff
parser = logoHTMLParser()
teamData = dataDir.getTeamData()
logoList =  parser.start_parse(getLogoHtml(), teamData)
saveLogos(logoList)
