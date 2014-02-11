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

<b> the stas directory </b>
-- submodule dataFiles found on github from [@ddw17](http://www.twitter.com/ddw17).
* creates json manifest of teams and season schedules for each team
* i've added script that pulls play by play xml data from [EventFlow](http://www.cs.umd.edu/hcil/eventflow/NBA/nbaData.shtml)
* i think i'm going to just use this submodule as a way to collect and store various data sets
* the next data set i need to generate is a json array of all of the players on a team.  what fun!

-- TODO in the rest of the stats directory
* scripts that parse data sets and turn them into numpy arrays
* scripts that analize numpy arrays / prepare it for analysis in python interpretur using pandas
* scripts for converting numpy arrays into plots using matplotlib

