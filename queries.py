import re
import mysql.connector

# Connect to the database
myConnection = mysql.connector.connect(
  user='root',
  password='....', # Enter your password here
  host='localhost',
  database='SoccerDB'
)

# Create a cursor
myCursor = myConnection.cursor()

# Query 1: 

# Query 2: 

# Query 3: 

# Query 4: 

# Query 5: 

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

  cursorObject.execute(query)
  return cursorObject.fetchall()

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
  
  cursorObject.execute(query)
  return cursorObject.fetchall()

# Query 8: Players Taller or Shorter than a Specific Height
def query8(height, shorter):
  if shorter: symbol = "<"
  else : symbol = ">"

  query = "SELECT p.PlayerName, p.Height" \
    " FROM Player p " \
    " WHERE p.Height %s %d " \
    " ORDER BY p.Height;" % symbol, height
  
  cursorObject.execute(query)
  return cursorObject.fetchall()

# Query 9: All Matches in a Specific League and Season
def query9(teamName, season):
  # Note: not all leagues have matches in all seasons
  query = "SELECT m.MatchID, m.HomeTeamID, ht.FullName AS HomeTeam, m.AwayTeamID, at.FullName AS AwayTeam, m.HomeGoals, m.AwayGoals, m.Season " \
  " FROM Matches m " \
  " JOIN Team ht ON m.HomeTeamID = ht.TeamID " \
  " JOIN Team at ON m.AwayTeamID = at.TeamID " \
  " JOIN League l ON ht.LeagueID = l.LeagueID " \
  " WHERE l.LeagueName = '%s' AND m.Season = %d;" % teamName, season

  cursorObject.execute(query)
  return cursorObject.fetchall()

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
  
  cursorObject.execute(query)
  return cursorObject.fetchall()

# Close the database connection
cursorObject.close()
myConnection.close()