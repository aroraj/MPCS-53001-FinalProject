import re
import csv
import random
import mysql.connector
import config
from randate import generate_date

random.seed(0)

# Connect to the database
myConnection = mysql.connector.connect(
    user=config.user,
    password=config.password,
    host='localhost',
    database='soccerdb'
)
# Create a cursor
myCursor = myConnection.cursor()

# Insert data into Country table
countryIDs = []
countryValues = []
with open('data/Country.csv') as csvfile:
    countryReader = csv.reader(csvfile, delimiter = ',' )
    next(countryReader)
    for row in countryReader:
        countryID = row[0]
        countryName = row[1]

        countryValues.append((countryID, countryName))
        countryIDs.append(countryID)
    
myCursor.executemany('INSERT IGNORE INTO Country values (%s, %s)', countryValues)
myConnection.commit()

# Insert data into League table
leagueValues = []
leagueIDs = []
with open('data/League.csv') as csvfile:
    leagueReader = csv.reader(csvfile, delimiter = ',' )
    next(leagueReader)
    for row in leagueReader:
        leagueID = row[0]
        countryID = row[1]
        leagueName = row[2]

        leagueIDs.append(leagueID)
        leagueValues.append((leagueID, leagueName, countryID))
    
myCursor.executemany('insert into League values (%s, %s, %s)', leagueValues)
myConnection.commit()

# Insert data into Team table
teamValues = []
teamIDs = []
with open('data/TeamNew.csv', encoding='utf-8') as csvfile:
    teamReader = csv.reader(csvfile, delimiter = ',' )
    next(teamReader)
    for row in teamReader:
        teamID = row[1]
        teamLongName = row[2]
        teamShortName = row[3]
        leagueID = leagueIDs[random.randint(0, len(leagueIDs)-1)]

        teamValues.append((teamID, teamLongName, teamShortName, leagueID))
        teamIDs.append(teamID)
    
myCursor.executemany('insert into Team values (%s, %s, %s, %s)', teamValues)
myConnection.commit()

# Insert data into Player table

playerValues = []
playerIDs = []
with open('data/PlayerNew.csv') as csvfile:
    playerReader = csv.reader(csvfile, delimiter = ',' )
    next(playerReader)
    for row in playerReader:
        playerID = row[0]
        playerName = row[2]
        playerHeight = row[4]
        playerBDay = row[3].split(' ')[0]
        playerBornIn = countryIDs[random.randint(0, len(countryIDs)-1)]

        playerValues.append((playerID, playerName, playerHeight, playerBDay, playerBornIn))
        playerIDs.append(playerID)
    
myCursor.executemany('insert into Player values (%s, %s, %s, %s, %s)', playerValues)
myConnection.commit()

# Insert data into PlayedFor table

playedForValues = []
for playerID in playerIDs:
    # Randomly choose either played for one or two teams
    num_teams = random.randint(1, 2)
    ran_nums = []
    # Generate random numbers for starting and ending dates
    for _ in range(num_teams * 2):
        ran_nums.append(random.random())
    ran_nums.sort()
    for i in range(num_teams):
        # Randomly generate teamID, if it conflicts with previous team then add 1
        teamIDidx = random.randint(0, len(teamIDs)-1)
        teamID = teamIDs[teamIDidx]
        if playedForValues and teamID == playedForValues[-1][1]:
            if teamIDidx == len(teamIDs) - 1:
                teamID = teamIDs[0]
            else:
              teamID = teamIDs[teamIDidx + 1]
        # Generate start and end dates  
        startDate = generate_date("2008-1-1", "2016-12-31", ran_nums[2*i])
        endDate = generate_date("2008-1-1", "2016-12-31", ran_nums[2*i + 1])
        playedForValues.append((playerID, teamID, startDate, endDate))
    
myCursor.executemany('insert into PlayedFor values (%s, %s, %s, %s)', playedForValues)
myConnection.commit()


# Insert data into Match table

matchValues = []
with open('data/MatchNew.csv') as csvfile:
    matchReader = csv.reader(csvfile, delimiter = ',' )
    next(matchReader)
    for row in matchReader:
        matchID = row[0]
        homeGoals = row[6]
        awayGoals = row[7]
        # Only want starting year of season, so take first 4 characters
        season = row[2][:4]
        homeTeamID = row[4]
        awayTeamID = row[5]

        matchValues.append((matchID, homeGoals, awayGoals, season, homeTeamID, awayTeamID))
    
myCursor.executemany('insert into Matches values (%s, %s, %s, %s, %s, %s)', matchValues)
myConnection.commit()

# Close the database connection
myCursor.close()
myConnection.close()