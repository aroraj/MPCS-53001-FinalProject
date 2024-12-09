import re
import mysql.connector

myConnection = mysql.connector.connect(
    user='root',
    password='...',
    host='localhost',
    database='soccerdb'
)
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

  conn = get_db_connection()
  cursor = conn.cursor()
  
  try:
    cursor.execute(query)
    return cursor.fetchall()
  finally:
    cursor.close()
    conn.close()

# Query 7: Players with the Same Birthday
def query7(month=None, day=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT PlayerID, PlayerName, Birthday
        FROM Player 
        WHERE MONTH(Birthday) = %s AND DAY(Birthday) = %s
        ORDER BY PlayerName
        """
        cursor.execute(query, (month, day))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# Query 8: Players Taller or Shorter than a Specific Height
def query8(player_name, comparison=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        height_query = """
        SELECT Height
        FROM Player
        WHERE PlayerName LIKE %s
        LIMIT 1
        """
        cursor.execute(height_query, (f"%{player_name}%",))
        result = cursor.fetchone()
        
        if result:
            player_height = result[0]
            query = """
            SELECT PlayerID, PlayerName, Birthday, Height
            FROM Player
            WHERE Height {} %s
            ORDER BY Height {}
            """
            
            if comparison == 'taller':
                operator = '>'
                order = 'ASC'
            else:  # shorter
                operator = '<'
                order = 'DESC'
                
            formatted_query = query.format(operator, order)
            cursor.execute(formatted_query, (player_height,))
            return cursor.fetchall()
        return []
    finally:
        cursor.close()
        conn.close()

# Query 9: All Matches in a Specific League and Season
def query9(teamName, season):
  # Note: not all leagues have matches in all seasons
  query = "SELECT m.MatchID, m.HomeTeamID, ht.FullName AS HomeTeam, m.AwayTeamID, at.FullName AS AwayTeam, m.HomeGoals, m.AwayGoals, m.Season " \
  " FROM Matches m " \
  " JOIN Team ht ON m.HomeTeamID = ht.TeamID " \
  " JOIN Team at ON m.AwayTeamID = at.TeamID " \
  " JOIN League l ON ht.LeagueID = l.LeagueID " \
  " WHERE l.LeagueName = '%s' AND m.Season = %d;" % teamName, season

  conn = get_db_connection()
  cursor = conn.cursor()
  
  try:
    cursor.execute(query)
    return cursor.fetchall()
  finally:
    cursor.close()
    conn.close()

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
  
  conn = get_db_connection()
  cursor = conn.cursor()
  
  try:
    cursor.execute(query)
    return cursor.fetchall()
  finally:
    cursor.close()
    conn.close()

# Get all teams
def get_teams():
    query = "SELECT TeamID, FullName FROM Team ORDER BY FullName;"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# Get all seasons
def get_seasons():
    query = "SELECT DISTINCT Season FROM Matches ORDER BY Season;"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()