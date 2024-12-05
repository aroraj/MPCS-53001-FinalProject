from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query1')
def query1():
    return render_template('query1.html')

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

@app.route('/query6')
def query6():
    return render_template('query6.html')

@app.route('/query7')
def query7():
    return render_template('query7.html')

@app.route('/query8')
def query8():
    return render_template('query8.html')

@app.route('/query9')
def query9():
    return render_template('query9.html')

@app.route('/query10')
def query10():
    return render_template('query10.html')

if __name__ == '__main__':
    app.run(debug=True)
