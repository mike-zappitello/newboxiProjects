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

<b> structure of directory </b>
-- data directory
** holds all data files
* teams, players, schedules at the moment.
* only one version of each.  should look into ways to keep it current
** holds .py that holds the absolute path to each dir in data dir

-- scrapers directory
** one for teams
* found on github from [@ddw17](http://www.twitter.com/ddw17).
* creates json manifest of teams and season schedules for each team
* I left his lisence and read me in tact with the scraper.
* I probably broke it in moving it.  Its a todo to fix.
** one for play by play
* pulls play by play xml data from [EventFlow](http://www.cs.umd.edu/hcil/eventflow/NBA/nbaData.shtml)
* needs work that will allow it to auto update games as they are played
** one for players
* i inherited this one from old work.
* modified it to store data into league wide json manifest
* pulls data from [eskimo](http://www.eskimo.com/~pbender/rosters.html)
** on for twitter
* i planned on doing an analysis of who's following who on twitter
* this stuff is from that and it didn't make sense to delete it
* i have no idea how good it is

-- the rest
** i'm not sure at this point
* i think the ideal thing to have is a set of parsers for each data type
* each parser would massage the data into the right form
* then i could just make things from there i suppose

-- pbpParsers.py
* its a bunch of methods that get data into an array to be analized
* currently grabs all play by play xmls and parses them by player
* parses for shots both made and missed
* creates a hitogram of points vs score diff by shot type for each player
* its going to be important to structure this correctly and keep things modular

-- TODO in the rest of the stats directory
* scripts that analize numpy arrays / prepare it for analysis in python interpretur using pandas
  - parsing all shots by player (done)
  - parse events based on lineups ()
* scripts for converting numpy arrays into plots using matplotlib
  - a 2d histogram that colors shot percentage with time remaining on the y and point diff on the x
  - start normalizing things
* start looking into how units fit in with everything
* look at better way to keep json of players and teams they play on
* add team colors and logos for styling
* maybe add player number .jpg's and faces for styling

