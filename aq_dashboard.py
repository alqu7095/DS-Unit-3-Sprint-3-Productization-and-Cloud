from flask import Flask
import requests
import openaq
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask import render_template
from .models import DB, Record

api = openaq.OpenAQ()

def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    DB.init_app(app)

    @app.route('/')

    def root():
        status, body = api.measurements(city='Los Angeles', parameter = 'pm25')
        LA_25 = []
        for i in range(0,len(body['results'])):
            LA_25.append((body['results'][i]['date']['utc'], body['results'][i]['value']))

        risk = DB.session.query(Record).filter(Record.value>10).all()
        record = Record.query.all()
        return render_template("root.html", risk=risk, record=record, LA_25=LA_25)

    @app.route('/refresh', methods = ['POST', 'GET'])
    def refresh():
        DB.drop_all()
        DB.create_all()
        status, body = api.measurements(city="Los Angeles", parameter = 'pm25')

        if request.method == 'GET':
            for i in range(0, len(body['results'])):
                DB.session.add(
                    Record(
                        datetime = body['results'][i]['date']['utc'],
                        value = body ['results'][i]['value']))

        DB.session.commit()
        record = Record.query.all()
        return render_template('refresh.html', records = records)
 
    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        risk = DB.session.query(Record).filter(Record.value>10).all()
        record = Record.query.all()
        return render_template("dashboard.html", risk=risk, record=record)

    return app


DB = SQLAlchemy()

class Record(DB.Model):
    id= DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return 'Record{}, {}'.format(self.datetime, self.value)
        


