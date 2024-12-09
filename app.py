from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from queries import get_teams, get_seasons, get_leagues, query1, query2, query3, query4, query5, query6, query7, query8, query9, query10, get_countries, insert_country, insert_league, insert_team, insert_player, insert_match, insert_played_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

@app.route('/query2', methods=['GET', 'POST'])
def query2_route():
    try:
        seasons = get_seasons()
        
        if request.method == 'POST':
            season = request.form.get('season')
            limit = request.form.get('limit')
            if season and limit:
                results = query2(int(limit), season)
                return render_template('query2.html', seasons=seasons, results=results)
        
        return render_template('query2.html', seasons=seasons)
    except Exception as e:
        print(f"Error in query2: {e}")
        return f"Error: {e}", 500

@app.route('/query3')
def query3():
    return render_template('query3.html')

@app.route('/query4')
def query4():
    return render_template('query4.html')

@app.route('/query5', methods=['GET', 'POST'])
def query5_route():
    try:
        leagues = get_leagues()
        seasons = get_seasons()
        
        if request.method == 'POST':
            league = request.form.get('league')
            season = request.form.get('season')
            if league and season:
                results = query5(league, season)
                return render_template('query5.html', leagues=leagues, seasons=seasons, results=results, selected_league=league, selected_season=season)
        
        return render_template('query5.html', leagues=leagues, seasons=seasons)
    except Exception as e:
        print(f"Error in query5: {e}")
        return f"Error: {e}", 500

@app.route('/query6', methods=['GET', 'POST'])
def query6_route():
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

@app.route('/query9', methods=['GET', 'POST'])
def query9_route():
    try:
        leagues = get_leagues()
        seasons = get_seasons()
        
        if request.method == 'POST':
            league = request.form.get('league')
            season = request.form.get('season')
            sort_by = request.form.get('sort_by')
            
            if league and season:
                results = query9(league, season)
                
                if sort_by == 'home_team':
                    results = sorted(results, key=lambda x: x[1])
                elif sort_by == 'goals':
                    results = sorted(results, key=lambda x: x[2] + x[4], reverse=True)
                
                return render_template('query9.html', 
                                     leagues=leagues, 
                                     seasons=seasons, 
                                     results=results)
        
        return render_template('query9.html', 
                             leagues=leagues, 
                             seasons=seasons)
    except Exception as e:
        print(f"Error in query9_route: {e}")
        return f"Error: {e}", 500

@app.route('/query10', methods=['GET', 'POST'])
def query10_route():
    try:
        countries = get_countries()
        seasons = get_seasons()
        
        if request.method == 'POST':
            selected_teams = request.form.getlist('countries')
            season = request.form.get('season')
            
            if selected_teams:
                results = query10(selected_teams, season) if season else query10(selected_teams)
                return render_template('query10.html', 
                                    countries=countries,
                                    seasons=seasons,
                                    results=results,
                                    selected_countries=selected_teams,
                                    selected_season=season)
        
        return render_template('query10.html',
                             countries=countries,
                             seasons=seasons)
    except Exception as e:
        print(f"Error in query10_route: {e}")
        return f"Error: {e}", 500

@app.route('/insert', methods=['GET'])
def insert_page():
    countries = get_countries()
    teams = get_teams()
    seasons = get_seasons()
    leagues = get_leagues()
    return render_template('insert.html', 
                         countries=countries,
                         teams=teams,
                         seasons=seasons,
                         leagues=leagues)

@app.route('/insert/country', methods=['POST'])
def insert_country_route():
    try:
        country_name = request.form.get('country_name')
        insert_country(country_name)
        return jsonify({
            'success': True,
            'message': 'Country added successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding country: {str(e)}'
        }), 400

@app.route('/insert/league', methods=['POST'])
def insert_league_route():
    try:
        league_name = request.form.get('league_name')
        country_name = request.form.get('league_country')
        insert_league(league_name, country_name)
        return jsonify({
            'success': True,
            'message': 'League added successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding league: {str(e)}'
        }), 400

@app.route('/insert/team', methods=['POST'])
def insert_team_route():
    try:
        team_full_name = request.form.get('team_full_name')
        team_short_name = request.form.get('team_short_name')
        league_name = request.form.get('team_league')
        insert_team(team_full_name, team_short_name, league_name)
        return jsonify({
            'success': True,
            'message': 'Team added successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding team: {str(e)}'
        }), 400

@app.route('/insert/player', methods=['POST'])
def insert_player_route():
    try:
        player_name = request.form.get('player_name')
        height = request.form.get('height')
        birthday = request.form.get('birthday')
        birth_country = request.form.get('birth_country')
        insert_player(player_name, height, birthday, birth_country)
        return jsonify({
            'success': True,
            'message': 'Player added successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding player: {str(e)}'
        }), 400

@app.route('/insert/match', methods=['POST'])
def insert_match_route():
    try:
        season = request.form.get('season')
        home_team = request.form.get('home_team')
        away_team = request.form.get('away_team')
        home_goals = request.form.get('home_goals')
        away_goals = request.form.get('away_goals')
        insert_match(season, home_team, away_team, home_goals, away_goals)
        return jsonify({
            'success': True,
            'message': 'Match added successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding match: {str(e)}'
        }), 400

@app.route('/insert/played_for', methods=['POST'])
def insert_played_for_route():
    try:
        player_name = request.form.get('player_name')
        team_name = request.form.get('team_name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        insert_played_for(player_name, team_name, start_date, end_date)
        return jsonify({
            'success': True,
            'message': 'Player history added successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding player history: {str(e)}'
        }), 400

@app.route('/get_countries')
def get_countries_json():
    try:
        countries = get_countries()
        print("Fetched countries:", countries)
        return jsonify(countries)
    except Exception as e:
        print("Error fetching countries:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
