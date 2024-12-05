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

# Insert data into Country table

# Insert data into League table

# Insert data into Team table

# Insert data into Player table

# Insert data into PlayedFor table

# Insert data into Match table

# Close the database connection
cursorObject.close()
myConnection.close()