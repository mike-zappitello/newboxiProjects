# script to grap all of the colors for each team and add it to our
# json manifest for those teams
import urllib2
from HTMLParser import HTMLParser
import dataDirs as dataDir
import json
import dataDirs as dataDir

# url containing color info for all teams
k_colorUrl = "http://teamcolors.arc90.com/"
# teams file
k_teamsFile = (dataDir.k_teamsDir + 'teams.json')

# open up the team json file
# create a json string with our new team data
# save and close the file
def saveTeamData(teamData):
  teamsFileString = (k_teamsFile)
  teamsFile = open(teamsFileString, 'w')
  newData = {'teams' : teamData}
  newTeamsData = json.dumps(newData,sort_keys=True, indent=2, separators=(",", ":"))
  teamsFile.write(newTeamsData)
  teamsFile.close()

# class that will take parse our color url
class colorHTMLParser(HTMLParser):
  # function to start the parser taking in the url and old team data
  def start_parse(self, html, teamData):
    self.teamData = teamData
    self.tag_stack = []
    self.feed(html)
    return self.teamData

  # checks to see if an attribute is a new nba team
  # if true, returns true and resets the colors dict, color count
  # and current team data
  # if false returns false
  def attrIsTeam(self, attr):
    if attr[0] == "id":
      for team in self.teamData:
        if attr[1] == team['full_name']:
          self.currentTeamData = team
          self.colors = {}
          self.colorCount = 0
          return True

    return False

  # when we have a new starting tag, compares it against the thigns we care about
  #
  # depending on the tag and elements in the tag stack, calls attrIsTeam and 
  # edits tag stack
  def handle_starttag(self, tag, attrs):
    if (tag == "li" and
      attrs and
      attrs[0][0] == "class" and
      attrs[0][1] == "team"):
        self.tag_stack.append(tag)
    if tag == "h3":
      if self.attrIsTeam(attrs[0]):
        self.tag_stack.append(tag)
      else:
        if self.tag_stack and self.tag_stack[-1] == "li":
          self.tag_stack.pop()
    elif (tag == "ul" and
      attrs and
      self.tag_stack and
      self.tag_stack[-1] == "li" and
      attrs[0][0] == "class" and
      attrs[0][1] == "colors"):
        self.tag_stack.append(tag)
    elif (tag == "li" and
      attrs and
      self.tag_stack and
      self.tag_stack[-1] == "ul" and
      attrs[0][0] == "style"):
        self.tag_stack.append(tag)
    elif (tag == "span" and
      attrs and
      self.tag_stack and
      self.tag_stack[-1] == "li" and
      attrs[0][0] == "class" and
      attrs[0][1] == "hex"):
        self.tag_stack.append(tag)

  # when we reach an end tag, checks with tag stack
  #
  # if we reached the end of a teams colors, saves that data
  # if we match the top of the tag stack, pop it off
  def handle_endtag(self, tag):
    if self.tag_stack and tag == self.tag_stack[-1]:
      if tag == "ul":
        self.currentTeamData['colors'] = self.colors

      self.tag_stack.pop()

  # handle data
  #
  # if our top of our tag stack is "span" we are on a color
  # add that color to the colors dict to be added to the team later
  def handle_data(self, data):
    if len(self.tag_stack) > 0 and  self.tag_stack[-1] == 'span':
      self.colors[str(self.colorCount)] = data
      self.colorCount = self.colorCount + 1

# get the html from the color url
# return the html as a string
def getColorHtml():
  color_page = urllib2.urlopen(k_colorUrl)
  color_page_html = color_page.read()
  color_page.close()

  return color_page_html

# setup the parser, get the html, parse it, and save the new stuff
parser = colorHTMLParser()
teamData = dataDir.getTeamData()
newTeamData =  parser.start_parse(getColorHtml(), teamData)
saveTeamData(newTeamData)
