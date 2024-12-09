import re
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='Wyh20171045!',
        host='localhost',
        database='soccerdb'
    )

myConnection = mysql.connector.connect(
    user='root',
    password='Wyh20171045!',
    host='localhost',
    database='soccerdb'
)
# Query 1: 

# Query 2: 

# Query 3: 

# Create a cursor
myCursor = myConnection.cursor()

# Query 1: Match Results for a Specific Team
def query1(team_name, season):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            M.Season,
            HT.FullName as HomeTeam,
            M.HomeGoals,
            M.AwayGoals,
            AT.FullName as AwayTeam
        FROM `Matches` M
        JOIN `Team` HT ON M.HomeTeamID = HT.TeamID
        JOIN `Team` AT ON M.AwayTeamID = AT.TeamID
        WHERE (HT.FullName = %s OR AT.FullName = %s)
        AND M.Season = %s
        ORDER BY M.MatchID;
        """
        
        cursor.execute(query, (team_name, team_name, season))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

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