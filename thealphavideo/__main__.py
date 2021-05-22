from flask import Flask, render_template, request, url_for, flash, redirect, Response
from pygtail import Pygtail
from flask_ask_alphavideo import Ask, question, statement, convert_errors, audio
from youtube_dl import YoutubeDL
from werkzeug.exceptions import abort
import sqlite3
import logging
import datetime
import os
import requests
import sys
import time
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

#versions

version = 1.4

response = requests.get('https://api.andrewstech.me/alpha-video/VERSION/')

if ( version == response.text ):
   print("You are running the latest version")
else:
   print("You have an update")


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def start():
    sentry_sdk.init(
        dsn="https://d781c09d67f34a05b2b2d89193f4f2a0@o575799.ingest.sentry.io/5728581",
        integrations=[FlaskIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )




ip = '0.0.0.0'  # System Ip
host = '0.0.0.0'  # doesn't require anything else since we're using ngrok
port = 5000  # may want to check and make sure this port isn't being used by anything else

LOG_FILE = 'app.log'
log = logging.getLogger('__name__')
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)



ytdl_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': ip
}

ytdl = YoutubeDL(ytdl_options)
app = Flask(__name__)
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", True)
app.config["JSON_AS_ASCII"] = False
app.config['SECRET_KEY'] = 'dev'
app.config.from_mapping(
        BASE_URL="http://localhost:5000",
)



print("By AndrewsTech")

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'),404

@app.errorhandler(405)
def not_found_error(error):
    return render_template('405.html'),405

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/playlist')
def playlist():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('playlist.html', posts=posts)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('playlist'))

    return render_template('create.html')

@app.route('/<int:id>/delete', methods=('GET',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('playlist'))

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('playlist'))

    return render_template('edit.html', post=post)

@app.route('/progress')
def progress():
    def generate():
        x = 0
        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = x + 10
            time.sleep(0.5)
    return Response(generate(), mimetype= 'text/event-stream')

@app.route('/log')
def progress_log():
	def generate():
		for line in Pygtail(LOG_FILE, every_n=1):
			yield "data:" + str(line) + "\n\n"
			time.sleep(0.5)
	return Response(generate(), mimetype= 'text/event-stream')

@app.route('/env')
def show_env():
	log.info("route =>'/env' - hit")
	env = {}
	for k,v in request.environ.items(): 
		env[k] = str(v)
	log.info("route =>'/env' [env]:\n%s" % env)
	return env

@app.route("/logstream", methods=["GET"])
def logstream():
    return render_template('logs.html')


import intents

app.run(host=host, port=port)

# Made by andrewstech https://github.com/unofficial-skills/alpha-video/
