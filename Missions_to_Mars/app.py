from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pymongo
import scrape_mars

# Create instance of Flask app
app = Flask(__name__)

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

db = client.mars_db

# Create route which renders index.html template


@app.route('/')
def home_page():
    mars_data_page = db.mars_info.find_one()
    print(mars_data_page)
    return render_template('index.html', mars=mars_data_page)


@app.route('/scrape')
def scrape():

    mars_data = scrape_mars.scrape_info()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
