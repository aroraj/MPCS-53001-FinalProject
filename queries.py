import re
import mysql.connector

# Connect to the database
myConnection = mysql.connector.connect(
    user='root',
    password='...',
    host='localhost',
    database='soccerdb'
)

# Create a cursor
myCursor = myConnection.cursor()

# Query 1: Match Results for a Specific Team
def query1(teamName):
  query = f"""SELECT Season, FullName AS OpponentName, Goals, OpponentGoals
              FROM (SELECT Season, OpponentID, Goals, OpponentGoals
                    FROM (SELECT *
                          FROM Team AS T
                          WHERE T.FullName = "{teamName}") AS T
                    INNER JOIN (SELECT Season, AwayTeamID AS OpponentID, HomeGoals AS Goals, AwayGoals AS OpponentGoals, HomeTeamID AS ID
                                FROM Matches
                                UNION ALL
                                SELECT Season, HomeTeamID AS OpponentID, AwayGoals AS Goals, HomeGoals AS OpponentGoals, AwayTeamID AS ID
                                FROM Matches) AS M ON T.TeamID = M.ID) AS TM
              INNER JOIN Team AS T ON TM.OpponentID = T.TeamID;"""
  
  myCursor.execute(query)
  return myCursor.fetchall() 

# Query 2: Top scoring teams in a season
def query2(limit, season):
  query = f"""SELECT FullName, COUNT(Goals)
              FROM (SELECT HomeTeamID AS TeamID, HomeGoals AS Goals
                  FROM Matches as M
                  WHERE M.Season = {season}
                  UNION ALL
                  SELECT AwayTeamID AS TeamID, AwayGoals AS Goals
                  FROM Matches AS M
                  WHERE M.Season = {season}) AS M
              INNER JOIN Team AS T ON T.TeamID = M.TeamID
              GROUP BY FullName

              ORDER BY COUNT(Goals) DESC
              LIMIT {limit};"""
  
  myCursor.execute(query)
  return myCursor.fetchall()

# Query 3: Players born in a given country between given years
def query3(country, startYear, endYear):
  query = f"""SELECT PlayerName, Birthday
              FROM Player AS P
              INNER JOIN (SELECT *
                          FROM Country AS C
                          WHERE C.CountryName = "{country}") AS C on P.BornIn = C.CountryID
              WHERE Birthday BETWEEN "{startYear}-1-1" AND "{endYear}-12-31";"""
  
  myCursor.execute(query)
  return myCursor.fetchall()

# Query 4: 
def query4(team, year):
  query = f"""SELECT PlayerName
               FROM Player as P
               INNER JOIN (SELECT PlayerID
                           FROM PlayedFor as PF
                           INNER JOIN (SELECT TeamID
                                       FROM Team as T
                                       WHERE T.FullName = "{team}") AS T ON PF.TeamID = T.TeamID
               WHERE PF.StartDate <= "{year}-12-31" AND PF.EndDate >= "{year}-1-1") AS PFT ON P.PlayerID = PFT.PlayerID;"""
  
  myCursor.execute(query)
  return myCursor.fetchall()

# Query 5: 
def query5(league, season):
  query = f"""SELECT 
                FullName,
                SUM(CASE WHEN Goals > OpponentGoals THEN 1 ELSE 0 END) AS Wins,
                SUM(CASE WHEN Goals = OpponentGoals THEN 1 ELSE 0 END) AS Draws,
                SUM(CASE WHEN Goals < OpponentGoals THEN 1 ELSE 0 END) AS Losses
              FROM (SELECT HomeTeamID AS TeamID, HomeGoals AS Goals, AwayGoals AS OpponentGoals
                    FROM Matches as M
                    WHERE M.Season = {season}
                    UNION ALL
                    SELECT AwayTeamID AS TeamID, AwayGoals AS Goals, HomeGoals AS OpponentGoals
                    FROM Matches AS M
                    WHERE M.Season = {season}) AS M
              INNER JOIN (SELECT TeamID, FullName
                          FROM Team AS T
                          INNER JOIN League as L on T.LeagueID = L.LeagueID
                          WHERE L.LeagueName = "{league}") AS T ON T.TeamID = M.TeamID
              GROUP BY FullName
              
              ORDER BY Wins DESC, Draws DESC, Losses DESC;"""
  
  myCursor.execute(query)
  return myCursor.fetchall()

# Query 6: Overall Wins, Losses, Draws for a Specific Team
def query6(teamName):
  query = "SELECT" \
  " SUM(CASE WHEN (m.HomeTeamID = t.TeamID AND m.HomeGoals > m.AwayGoals) OR (m.AwayTeamID = t.TeamID AND m.AwayGoals > m.HomeGoals) " \
  " THEN 1 ELSE 0 END) AS Wins, " \
  " SUM(CASE WHEN (m.HomeTeamID = t.TeamID AND m.HomeGoals < m.AwayGoals) OR (m.AwayTeamID = t.TeamID AND m.AwayGoals < m.HomeGoals) THEN 1 ELSE 0 END) AS Losses, " \
  " SUM(CASE WHEN m.HomeGoals = m.AwayGoals THEN 1 ELSE 0 END) AS Draws " \
  " FROM Matches m " \
  " JOIN Team t ON t.TeamID = (SELECT TeamID FROM Team WHERE FullName = '%s' LIMIT 1) " \
  " WHERE m.HomeTeamID = t.TeamID OR m.AwayTeamID = t.TeamID;", teamName

  myCursor.execute(query)
  return myCursor.fetchall()

# Query 7: Players with the Same Birthday
def query7():
  query = "SELECT p1.PlayerID, p1.PlayerName, p1.Birthday " \
  " FROM Player p1 " \
  " JOIN (SELECT MONTH(Birthday) AS Month, DAY(Birthday) AS Day " \
  " FROM Player  " \
  " GROUP BY MONTH(Birthday), DAY(Birthday) " \
  " HAVING COUNT(*) > 1) p2 " \
  " ON MONTH(p1.Birthday) = p2.Month AND DAY(p1.Birthday) = p2.Day " \
  " ORDER BY MONTH(p1.Birthday), DAY(p1.Birthday);"
  
  myCursor.execute(query)
  return myCursor.fetchall()

# Query 8: Players Taller or Shorter than a Specific Height
def query8(height, shorter):
  if shorter: symbol = "<"
  else : symbol = ">"

  query = "SELECT p.PlayerName, p.Height" \
    " FROM Player p " \
    " WHERE p.Height %s %d " \
    " ORDER BY p.Height;" % symbol, height
  
  myCursor.execute(query)
  return myCursor.fetchall()

# Query 9: All Matches in a Specific League and Season
def query9(teamName, season):
  # Note: not all leagues have matches in all seasons
  query = "SELECT m.MatchID, m.HomeTeamID, ht.FullName AS HomeTeam, m.AwayTeamID, at.FullName AS AwayTeam, m.HomeGoals, m.AwayGoals, m.Season " \
  " FROM Matches m " \
  " JOIN Team ht ON m.HomeTeamID = ht.TeamID " \
  " JOIN Team at ON m.AwayTeamID = at.TeamID " \
  " JOIN League l ON ht.LeagueID = l.LeagueID " \
  " WHERE l.LeagueName = '%s' AND m.Season = %d;" % teamName, season

  myCursor.execute(query)
  return myCursor.fetchall()

# Query 10: Team with most wins for each country
def query10():
  query = "SELECT c.CountryName AS Country, t.FullName AS TeamName, COUNT(*) AS Wins " \
  " FROM Matches m " \
  " JOIN Team t ON m.HomeTeamID = t.TeamID OR m.AwayTeamID = t.TeamID " \
  " JOIN League l ON t.LeagueID = l.LeagueID " \
  " JOIN Country c ON l.CountryID = c.CountryID " \
  " WHERE ((m.HomeGoals > m.AwayGoals AND m.HomeTeamID = t.TeamID) OR " \
  " (m.AwayGoals > m.HomeGoals AND m.AwayTeamID = t.TeamID)) " \
  " GROUP BY c.CountryID, t.TeamID" \
  " ORDER BY c.CountryName, Wins DESC;"
  
  myCursor.execute(query)
  return myCursor.fetchall()

# Get all teams
def get_teams():
    query = "SELECT TeamID, FullName FROM Team ORDER BY FullName;"
    myCursor.execute(query)
    return myCursor.fetchall()

# Get all seasons
def get_seasons():
    query = "SELECT DISTINCT Season FROM Matches ORDER BY Season;"
    myCursor.execute(query)
    return myCursor.fetchall()

def close_db():
    if 'myCursor' in globals() and myCursor is not None:
        myCursor.close()
    if 'myConnection' in globals() and myConnection is not None:
        myConnection.close()