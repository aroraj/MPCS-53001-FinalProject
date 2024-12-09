from flask import Flask, render_template, request
from queries import get_teams, get_seasons, query1, query2, query3, query4, query5, query6, query7, query8

app = Flask(__name__)

# load all the csv files into a database

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/query1', methods=['GET', 'POST'])
def query1_route():
    try:
        teams = get_teams()
        seasons = get_seasons()
        
        if request.method == 'POST':
            team = request.form.get('team')
            season = request.form.get('season')
            if team and season:
                results = query1(team, season)
                return render_template('query1.html', teams=teams, seasons=seasons, results=results)
        
        return render_template('query1.html', teams=teams, seasons=seasons)
    except Exception as e:
        print(f"Error in query1: {e}")
        return f"Error: {e}", 500

@app.route('/query2')
def query2():
    return render_template('query2.html')

@app.route('/query3')
def query3():
    return render_template('query3.html')

@app.route('/query4')
def query4():
    return render_template('query4.html')

@app.route('/query5')
def query5():
    return render_template('query5.html')

@app.route('/query6', methods=['GET', 'POST'])
def query6():
    try:
        teams = get_teams()
        print(f"Found {len(teams)} teams")
        seasons = get_seasons()
        print(f"Found {len(seasons)} seasons")
        return render_template('query6.html', teams=teams, seasons=seasons)
    except Exception as e:
        print(f"Error in query6: {e}")
        return f"Error: {e}", 500

@app.route('/query7', methods=['GET', 'POST'])
def query7_route():
    try:
        if request.method == 'POST':
            month = request.form.get('month')
            day = request.form.get('day')
            if month and day:
                month = int(month)
                day = int(day)
            results = query7(month, day)
            return render_template('query7.html', results=results)
        return render_template('query7.html')
    except Exception as e:
        print(f"Error in query7: {e}")
        return f"Error: {e}", 500

@app.route('/query8', methods=['GET', 'POST'])
def query8_route():
    try:
        if request.method == 'POST':
            player_name = request.form.get('player_name')
            comparison = request.form.get('comparison')
            if player_name and comparison:
                results = query8(player_name, comparison)
                return render_template('query8.html', results=results)
        return render_template('query8.html')
    except Exception as e:
        print(f"Error in query8: {e}")
        return f"Error: {e}", 500

@app.route('/query9')
def query9():
    return render_template('query9.html')

@app.route('/query10')
def query10():
    return render_template('query10.html')

if __name__ == '__main__':
    app.run(debug=True)
