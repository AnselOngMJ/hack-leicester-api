import json
from flask import Flask, jsonify, request
import sqlite3
import csv

app = Flask(__name__)

def connect_to_db():
    con = sqlite3.connect('database.db')
    return con

def create_db_table():
    try:
        con = connect_to_db()
        con.execute('''
            CREATE TABLE event (
                id INT PRIMARY KEY,
                name TEXT NOT NULL,
                venue TEXT NOT NULL,
                startDate TEXT NOT NULL,
                endDate TEXT NOT NULL
            );
        ''')
        con.commit()
        print('Event table created successfully')
    except:
        print('Event table exists')
    finally:
        con.close()

def format_event(result):
    event = {
        'id': result['id'],
        'name': result['name'],
        'venue': result['venue'],
        'startDate': result['startDate'],
        'endDate': result['endDate'],
    }
    return event

@app.route('/')
def hello_world():
    create_db_table()
    con = connect_to_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    with open('event.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            cur.execute('INSERT INTO event VALUES (?, ?, ?, ?, ?)', list(row.values()))
    
    result = cur.execute('SELECT * FROM event')
    events = [format_event(event) for event in result.fetchall()]
    return jsonify(events)

@app.route('/create')
def create():
    return
