from flask import Flask, render_template, request, url_for, flash, redirect, Response
from pygtail import Pygtail
from flask_ask import Ask, question, statement, convert_errors, audio
from youtube_dl import YoutubeDL
from werkzeug.exceptions import abort
import sqlite3
import logging
import datetime
import os
import sys
import time
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress')
def progress():
    def generate():
        for x in range(0, 101, 10):
            yield "data:" + str(x) + "\n\n"
            time.sleep(0.5)
    return Response(generate(), mimetype= 'text/event-stream')

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            content = request.form['content']

            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/delete', methods=('GET',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/log')
def progress_log():
	def generate():
		for line in Pygtail(LOG_FILE, every_n=1):
			yield "data:" + str(line) + "\n\n"
			time.sleep(0.5)
	return Response(generate(), mimetype= 'text/event-stream')

@app.route('/url')
def url_pro():
    with open("/tmp/supervisord.log", "r") as f:
        content = f.read()
    return render_template('url.html', content=content)

@app.route('/env')
def show_env():
    log.info("route =>'/env' - hit")
    env = {k: str(v) for k,v in request.environ.items()}
    log.info("route =>'/env' [env]:\n%s" % env)
    return env

@app.route("/logs", methods=["GET"])
def logstream():
    return render_template('logs.html')


ask = Ask(app, '/api')


@ask.launch
def launch():
    card_title = render_template('card_title')
    question_text = render_template('welcome')
    return question(question_text).simple_card(card_title, question_text)


@ask.session_ended
def session_ended():
    return "{}", 200


@ask.intent('AMAZON.StopIntent')
def handle_stop_intent():
    stop = render_template('stop')
    return statement(stop)


@ask.intent('AMAZON.CancelIntent')
def handle_stop_intent():
    stop = render_template('stop')
    return statement(stop)


@ask.intent('AMAZON.PauseIntent')
def handle_pause_intent():
    pause = render_template('pause')
    return audio(pause).stop()


@ask.intent('AMAZON.ResumeIntent')
def resume():
    resume = render_template('resume')
    return audio(resume).resume()


@ask.intent('AMAZON.FallbackIntent')
def handle_fallback_intent():
    fallback = render_template('fallback')
    return question(fallback)


@ask.intent('AMAZON.HelpIntent')
def handle_help_intent():
    fallback = render_template('fallback')
    return question(fallback)


@ask.intent('QueryIntent', mapping={'query': 'Query'})
def handle_query_intent(query):

    if not query or 'query' in convert_errors:
        return question('no results found, try another search query')

    data = ytdl.extract_info(f"ytsearch:{query}", download=False)
    search_results = data['entries']

    if not search_results:
        noresult = render_template('noresult')
        return question(noresult)

    result = search_results[0]
    song_name = result['title']
    channel_name = result['uploader']

    for format_ in result['formats']:
        if format_['ext'] == 'm4a':
            mp3_url = format_['url']
            playing = render_template('playing', song_name=song_name, channel_name=channel_name)
            return audio(playing).play(mp3_url)

    return question('noresult')


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            content = request.form['content']

            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


app.run(host=host, port=port)

# Made by andrewstech https://github.com/unofficial-skills/alpha-video/
