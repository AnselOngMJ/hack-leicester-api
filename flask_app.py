import json
from flask import Flask, jsonify, request
import sqlite3
import csv

app = Flask(__name__)
con = sqlite3.connect('database.db', check_same_thread=False)
con.row_factory = sqlite3.Row
cur = con.cursor()

def create_db_table():
    try:
        con.execute('''
            CREATE TABLE event (
                id INT PRIMARY KEY,
                title TEXT NOT NULL,
                venueId INT NOT NULL,
                startDate TEXT NOT NULL,
                endDate TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (venueId) REFERENCES venue(id)
            );
        ''')
        con.execute('''
            CREATE TABLE venue (
                id INT PRIMARY KEY,
                name TEXT NOT NULL,
                capacity INT NOT NULL
            );
        ''')
        con.commit()
        print('Event table created successfully')
    except Exception as e:
        print(e)

def format_event(result):
    event = {
        'id': result['id'],
        'title': result['title'],
        'venueId': result['venueId'],
        'startDate': result['startDate'],
        'endDate': result['endDate'],
        'description': result['description']
    }
    return event

def format_venue(result):
    venue = {
        'id': result['id'],
        'name': result['name'],
        'capacity': result['capacity']
    }
    return venue

def format_event_venue(result):
    event = {
        'id': result['id'],
        'title': result['title'],
        'venueId': result['venueId'],
        'startDate': result['startDate'],
        'endDate': result['endDate'],
        'description': result['description'],
        'venueName': result['name'],
        'capacity': result['capacity']
    }
    return event

@app.route('/')
def start():
    create_db_table()
    with open('event.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [list(row.values()) for row in reader]
        cur.executemany('INSERT INTO event VALUES (?, ?, ?, ?, ?, ?)', rows)
        con.commit()
    with open('venue.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [list(row.values()) for row in reader]
        cur.executemany('INSERT INTO venue VALUES (?, ?, ?)', rows)
        con.commit()
    return jsonify([])

@app.route('/events')
def events():
    result = cur.execute('SELECT * FROM event')
    events = [format_event(event) for event in result.fetchall()]
    return jsonify(events)

@app.route('/venues')
def venues():
    result = cur.execute('SELECT * FROM venue')
    venues = [format_venue(venue) for venue in result.fetchall()]
    return jsonify(venues)

@app.route('/create', methods=['POST'])
def create():
    event = json.loads(request.data)
    id = cur.execute('SELECT MAX(id) FROM event').fetchone()[0] + 1
    cur.execute('INSERT INTO event VALUES (?, ?, ?, ?, ?, ?)', [id] + list(event.values()))
    event['id'] = id
    return jsonify(event)

@app.route('/filter')
def filter():
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    capacity = request.args.get('capacity')
    if start_date is None:
        start_date = '1970'
    if end_date is None:
        end_date = '3000'
    if capacity is None:
        capacity = 0
    result = cur.execute('SELECT * FROM event, venue WHERE event.venueId == venue.id and startDate >= ? AND endDate <= ? AND capacity >= ?', [start_date, end_date, capacity])
    events = [format_event_venue(event) for event in result.fetchall()]
    return jsonify(events)
