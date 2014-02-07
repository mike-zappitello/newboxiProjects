nbaInfoStats
============

collaborative project to create interesting inforgraphs for nba stats

<b>a few ideas for projects that we can try to work out</b>

-- stats for who pulls defenses away and creates open shot for players
* look for pass, pass, shoot and what that shooting percentage is
* go by player, team, unit?

-- most played units on playoff teams
* look at substitutions and get stats on what units are on the floor the most for any team
* find the top two units for each of the 16 playoff teams and work on their stats
* get this as an infographic in time for the first round of the playoffs?

-- shooting percentages
* get each teams shooting percentage and defensive shooting percentage
* compare how teams shoot when playing agains good defenses
* who steps up agains good d's, who gets shut down by bad ones, who tourches bad ones?
* could be an interesting graph of where teams get their buckets

-- buckets graph
* track how many points someone has per season versus minutes played
* get a steadily increasing graph showing how players scored and who scored the most
* could be a sweet fucking gif

-- twitter project
* get all nba players twitter handles
* see who they are following and who they are following in common
* look at how many followers <i>those</i> people have in common
* order them from least followers to most and find some interesting people
* a lot of interesting data do be groomed from twitter.  this is just idea 1

<b>other housekeeping thoughts</b>

* i'm goign to do a directory for each project
* each folder will have a folder for the code, a folder for data, and a folder for images?
* you can update images in git as well

<b>data base structure to impose</b>

* a database of all players and unique ids
  * id | name *
* a database of all player lineups and unique ids
  * id | player 1 id | player 2 id | player 3 id | player 4 id | player 5 id *
* a database of all possessions
  * id | previous possession id | offensive lineup id | defensive lineup id | score after possession | durration of possession | last event id *
* a database of all events
  * id | previous even id | possession id | event category | player involved | shot type *
* a database of all teams and their games
