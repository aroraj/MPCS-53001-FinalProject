import re
import mysql.connector
import config
import random

def get_db_connection():
    return mysql.connector.connect(
        user=config.user,
        password=config.password,
        host='localhost',
        database='soccerdb'
    )

myConnection = mysql.connector.connect(
    user=config.user,
    password=config.password,
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
    query = f"""
    SELECT 
        t.FullName,
        SUM(CASE 
            WHEN m.HomeTeamID = t.TeamID THEN m.HomeGoals
            ELSE m.AwayGoals
        END) as TotalGoals,
        COUNT(*) as MatchesPlayed
    FROM Team t
    JOIN Matches m ON t.TeamID = m.HomeTeamID OR t.TeamID = m.AwayTeamID
    WHERE m.Season = {season}
    GROUP BY t.TeamID, t.FullName
    ORDER BY TotalGoals DESC
    LIMIT {limit}
    """
    
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

# Query 6: Wins, Losses, Draws for a Specific Team Over The Years
def query6(teamName):
  conn = get_db_connection()
  cursor = conn.cursor()
  
  try:
    query = """SELECT m.Season,
    SUM(CASE WHEN (m.HomeTeamID = t.TeamID AND m.HomeGoals > m.AwayGoals) OR (m.AwayTeamID = t.TeamID AND m.AwayGoals > m.HomeGoals)
    THEN 1 ELSE 0 END) AS Wins,
    SUM(CASE WHEN (m.HomeTeamID = t.TeamID AND m.HomeGoals < m.AwayGoals) OR (m.AwayTeamID = t.TeamID AND m.AwayGoals < m.HomeGoals) THEN 1 ELSE 0 END) AS Losses,
    SUM(CASE WHEN m.HomeGoals = m.AwayGoals THEN 1 ELSE 0 END) AS Draws
    FROM Matches m
    JOIN Team t ON t.TeamID = (SELECT TeamID FROM Team WHERE FullName = '%s' LIMIT 1)
    WHERE (m.HomeTeamID = t.TeamID OR m.AwayTeamID = t.TeamID)
    GROUP BY m.Season
    ORDER BY m.Season;"""

    cursor.execute(query, (teamName,))
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

# Query 8: Players Taller or Shorter than a Specific Player
def query8(player_name, comparison=None):
  conn = get_db_connection()
  cursor = conn.cursor()

  try:
    if comparison == 'taller':
      operator = '>'
      order = 'ASC'
    else:  # shorter
      operator = '<'
      order = 'DESC'
    
    query = """SELECT PlayerID, PlayerName, Birthday, Height
    FROM Player
    WHERE Height {} (SELECT Height FROM Player WHERE PlayerName = %s)
    ORDER BY Height {};"""
    formatted_query = query.format(operator, order)
    cursor.execute(formatted_query, (player_name,))
    return cursor.fetchall()
  finally:
    cursor.close()
    conn.close()

# Query 9: All Matches in a Specific League and Season
def query9(league_name, season):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            m.MatchID,
            ht.FullName AS HomeTeam,
            m.HomeGoals,
            at.FullName AS AwayTeam,
            m.AwayGoals,
            m.Season
        FROM Matches m
        JOIN Team ht ON m.HomeTeamID = ht.TeamID
        JOIN Team at ON m.AwayTeamID = at.TeamID
        JOIN League l ON ht.LeagueID = l.LeagueID
        WHERE l.LeagueName = %s 
        AND m.Season = %s
        ORDER BY m.MatchID;
        """
        
        cursor.execute(query, (league_name, season))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# Get all countries
def get_countries():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute('SELECT CountryName FROM Country ORDER BY CountryName')
        countries = cur.fetchall()
        cur.close()
        conn.close()
        return countries
    except Exception as e:
        print("Error in get_countries:", str(e))
        if conn:
            conn.close()
        raise e

def query10(countries, season=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        countries_str = ','.join(countries)
        
        base_query = """
        WITH TeamStats AS (
            SELECT 
                t.TeamID,
                t.FullName,
                c.CountryName,
                SUM(CASE 
                    WHEN m.HomeTeamID = t.TeamID THEN m.HomeGoals
                    ELSE m.AwayGoals
                END) as total_goals,
                COUNT(*) as matches_played,
                CAST(SUM(CASE 
                    WHEN m.HomeTeamID = t.TeamID THEN m.HomeGoals
                    ELSE m.AwayGoals
                END) AS FLOAT) / COUNT(*) as goals_per_match
            FROM Team t
            JOIN League l ON t.LeagueID = l.LeagueID
            JOIN Country c ON l.CountryID = c.CountryID
            JOIN Matches m ON t.TeamID = m.HomeTeamID 
                        OR t.TeamID = m.AwayTeamID
            WHERE c.CountryID IN ({countries_str})
            {season_filter}
            GROUP BY t.TeamID, t.FullName, c.CountryName
        )
        SELECT 
            ts.CountryName,
            ts.FullName,
            ts.total_goals,
            ts.matches_played,
            ROUND(ts.goals_per_match, 2) as goals_per_match,
            'N/A' as top_scorer
        FROM TeamStats ts
        ORDER BY ts.goals_per_match DESC
        LIMIT 5;
        """
        
        if season:
            season_filter = "AND m.Season = %s"
            query = base_query.format(countries_str=countries_str, season_filter=season_filter)
            cursor.execute(query, (season,))
        else:
            season_filter = ""
            query = base_query.format(countries_str=countries_str, season_filter=season_filter)
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

# Insert a new Country
# Note: If country is already in the database, the country will not be inserted
def insert_country(country_name):
  conn = get_db_connection()
  cursor = conn.cursor()

  # Check if country is already in the database
  query = "SELECT CountryID FROM Country WHERE CountryName = %s;"
  cursor.execute(query, (country_name,))
  result = cursor.fetchone()
  if result:
    return

  # Generate a random CountryID
  num = random.randint(1, 25000)
  query = "SELECT CountryID FROM Country WHERE CountryID = %s;"
  cursor.execute(query, (num,))
  result = cursor.fetchone()

  while result:
    num = random.randint(1, 25000)
    cursor.execute(query, (num,))
    result = cursor.fetchone()

  # Insert the new country
  try:
    query = "INSERT INTO Country (CountryID, CountryName) VALUES (%s, %s);"
    cursor.execute(query, (num, country_name))
    conn.commit()
  finally:
    cursor.close()
    conn.close()

# Insert a new League
# Note: If country_name does not exist in the database, it will be added into Country table
# If league is already in the database, the league will not be inserted
def insert_league(league_name, country_name):
  conn = get_db_connection()
  cursor = conn.cursor()

  # Check if league is already in the database
  query = "SELECT LeagueID FROM League WHERE LeagueName = %s;"
  cursor.execute(query, (league_name,))
  result = cursor.fetchone()
  if result:
    return

  insert_country(country_name)
  query = "SELECT CountryID FROM Country WHERE CountryName = %s;"
  cursor.execute(query, (country_name,))
  country_id = cursor.fetchone()[0]

  # Generate a random LeagueID
  num = random.randint(1, 25000)
  query = "SELECT LeagueID FROM League WHERE LeagueID = %s;"
  cursor.execute(query, (num,))
  result = cursor.fetchone()

  while result:
    num = random.randint(1, 25000)
    cursor.execute(query, (num,))
    result = cursor.fetchone()
  
  # Insert the new league
  try:
    query = "INSERT INTO League (LeagueID, LeagueName, CountryID) VALUES (%s, %s, %s);"
    cursor.execute(query, (num, league_name, country_id))
    conn.commit()
  finally:
    cursor.close()
    conn.close()

# Insert a new Team
# Note: If league_name does not exist in the database, the team will not be inserted
# If team is already in the database, the team will not be inserted
def insert_team(team_full_name, team_short_name, league_name):
  conn = get_db_connection()
  cursor = conn.cursor()

  # Check if team is already in the database
  query = "SELECT TeamID FROM Team WHERE FullName = %s;"
  cursor.execute(query, (team_name,))
  result = cursor.fetchone()
  if result:
    return

  query = "SELECT LeagueID FROM League WHERE LeagueName = %s;"
  cursor.execute(query, (league_name,))
  league = cursor.fetchone()
  # league name does not exist in DB so can't insert team
  if not league:
    return
  league_id = league[0]

  # Generate a random TeamID
  num = random.randint(1, 25000)
  query = "SELECT TeamID FROM Team WHERE TeamID = %s;"
  cursor.execute(query, (num,))
  result = cursor.fetchone()

  while result:
    num = random.randint(1, 25000)
    cursor.execute(query, (num,))
    result = cursor.fetchone()
  
  # Insert the new team
  try:
    query = "INSERT INTO Team (TeamID, FullName, ShortName, LeagueID) VALUES (%s, %s, %s, %s);"
    cursor.execute(query, (num, team_full_name, team_short_name, league_id))
    conn.commit()
  finally:
    cursor.close()
    conn.close()

# Insert a new Player
# Note: If birth_country does not exist in the database, it will be added into Country table
# If player is already in the database, the player will not be inserted
def insert_player(player_name, height, birthday, birth_country):
  conn = get_db_connection()
  cursor = conn.cursor()

  # Check if player is already in the database
  query = "SELECT PlayerID FROM Player WHERE PlayerName = %s AND birthday = %s;"
  cursor.execute(query, (player_name, birthday))
  result = cursor.fetchone()
  if result:
    return

  insert_country(birth_country)
  query = "SELECT CountryID FROM Country WHERE CountryName = %s;"
  cursor.execute(query, (birth_country,))
  country_id = cursor.fetchone()[0]

  # Generate a random PlayerID
  num = random.randint(1, 25000)
  query = "SELECT PlayerID FROM Player WHERE PlayerID = %s;"
  cursor.execute(query, (num,))
  result = cursor.fetchone()

  while result:
    num = random.randint(1, 25000)
    cursor.execute(query, (num,))
    result = cursor.fetchone()
  
  # Insert the new player
  try:
    query = "INSERT INTO Player (PlayerID, PlayerName, Height, Birthday, BornIn) VALUES (%s, %s, %s, %s, %s);"
    cursor.execute(query, (num, player_name, height, birthday, birth_country))
    conn.commit()
  finally:
    cursor.close()
    conn.close()

# Insert a new Match
# Note: If home_team or away_team does not exist in the database, the match will not be inserted
# If match is already in the database, the match will not be inserted
def insert_match(season, home_team, away_team, home_goals, away_goals):
  conn = get_db_connection()
  cursor = conn.cursor()

  # Get team IDs
  query = "SELECT TeamID FROM Team WHERE FullName = %s;"
  cursor.execute(query, (home_team,))
  
  home_team = cursor.fetchone()
  # home team does not exist in DB so can't insert match
  if not home_team:
    return
  home_team = home_team[0]
  
  cursor.execute(query, (away_team,))
  away_team = cursor.fetchone()
  # away team does not exist in DB so can't insert match
  if not away_team:
    return
  away_team = away_team[0]

  # Check if match is already in the database
  query = "SELECT MatchID FROM Matches WHERE Season = %s AND HomeTeamID = %s AND AwayTeamID = %s;"
  cursor.execute(query, (season, home_team, away_team))
  result = cursor.fetchone()
  if result:
    return

  # Generate a random MatchID
  num = random.randint(25980, 60000)
  query = "SELECT MatchID FROM Matches WHERE MatchID = %s;"
  cursor.execute(query, (num,))
  result = cursor.fetchone()

  while result:
    num = random.randint(25980, 60000)
    cursor.execute(query, (num,))
    result = cursor.fetchone()
  
  # Insert the new match
  try:
    query = "INSERT INTO Matches (MatchID, Season, HomeTeamID, AwayTeamID, HomeGoals, AwayGoals) VALUES (%s, %s, %s, %s, %s, %s);"
    cursor.execute(query, (num, season, home_team, away_team, home_goals, away_goals))
    conn.commit()
  finally:
    cursor.close()
    conn.close()

# Insert a new PlayedFor
# Note: If player or team does not exist in the database, the PlayedFor will not be inserted
# If player has already played for the team or another team during the same time period, the PlayedFor will not be inserted
# If start_date is after end_date, the PlayedFor will not be inserted
def insert_played_for(player_name, team_name, start_date, end_date):
  conn = get_db_connection()
  cursor = conn.cursor()

  # Get player ID and team ID 
  query = "SELECT PlayerID FROM Player WHERE PlayerName = %s;"
  cursor.execute(query, (player_name,))
  player_id = cursor.fetchone()
  # player does not exist in DB so can't insert PlayedFor
  if not player_id:
    return
  player_id = player_id[0]

  query = "SELECT TeamID FROM Team WHERE FullName = %s;"
  cursor.execute(query, (team_name,))
  team_id = cursor.fetchone()
  # team does not exist in DB so can't insert PlayedFor
  if not team_id:
    return
  team_id = team_id[0]

  # Check if player has already played for the team or another team during same time period
  query = "SELECT * FROM PlayedFor WHERE PlayerID = %s;"
  cursor.execute(query, (player_name,))
  result = cursor.fetchall()
  if result:
    for row in result():
      # if player has already played for the team during the same time period
      if row[1] == team_id and (row[2] <= start_date <= row[3] or row[2] <= end_date <= row[3]):
        return
      # if player has already played for another team during the same time period
      elif row[1] != team_id and (row[2] <= start_date <= row[3] or row[2] <= end_date <= row[3]):
        return

  # Insert the new PlayedFor
  try:
    # Validate start_date < end_date
    if start_date >= end_date:
      return
    else:
      query = "INSERT INTO PlayedFor (PlayerID, TeamID, StartDate, EndDate) VALUES (%s, %s, %s, %s);"
      cursor.execute(query, (player_id, team_id, start_date, end_date))
      conn.commit()
  finally:
    cursor.close()
    conn.close()

# Get all leagues
def get_leagues():
    query = "SELECT DISTINCT LeagueName FROM League ORDER BY LeagueName;"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()