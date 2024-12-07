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

# Query 6: 

# Query 7: 

# Query 8: 

# Query 9: 

# Query 10: 
def query10():
  query = "SELECT ... FROM ..."
  cursorObject.execute(query)
  return cursorObject.fetchall()

# Close the database connection
cursorObject.close()
myConnection.close()