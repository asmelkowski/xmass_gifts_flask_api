from flask import Flask, g, request
from flask_cors import CORS
import sqlite3
import json

persons = ['Mirosława', 'Tadeusz', 'Paweł', 'Ania', 'Dawid', 'Eliza', 'Sylwia', 'Rudi', 'Piotr', 'Ola', 'Adam']

DATABASE = 'gifts.db'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = dict_factory
    return db


app = Flask(__name__)
CORS(app)

@app.before_first_request
def fill_db():
    db = get_db()
    cur = db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS gifts
            (id integer primary key, name text UNIQUE, taken integer)''')
    for person in persons:
        cur.execute('INSERT OR IGNORE INTO gifts (name, taken) VALUES (?,?)', (person, 0))
        db.commit()

@app.route('/gifts')
def gifts():
    cur = get_db().cursor()
    cur.execute('SELECT * FROM gifts')
    all_gifts = cur.fetchall()
    return json.dumps(all_gifts)

@app.route('/gifts/<id>', methods=['GET', 'POST'])
def gifts_by_id(id):
    if request.method == 'GET':
        cur = get_db().cursor()
        cur.execute('SELECT * FROM gifts WHERE id = ?', (id,))
        all_gifts = cur.fetchall()
        return json.dumps(all_gifts)
    elif request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        cur.execute('UPDATE gifts set taken = 1 WHERE id = (?) ', (id,))
        db.commit()
        return "YEEEEPPP"

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()