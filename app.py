import json
from flask import Flask, jsonify, send_file
from flask import render_template
from flask_cors import CORS
from mylib.metaflac import MetaFlac


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

CORS(app)


@app.route("/jukebox")
def run_jukebox():

    return render_template("test.html")


@app.route("/getsong")
def get_songs():

    return jsonify(
        {
            "song_lists": [
                "time.flac",
                "one_last_kiss.flac"
            ]
        }
    )


@app.route("/")
def get_hello():

    return "Hello world"


@app.route("/my_song_folder/<song_name>")
def get_song_file(song_name):

    return send_file(
        f"song_folder/{song_name}.flac", mimetype="audio/flac"
    )


@app.route("/metadata/<song_title>")
def get_song_metadata(song_title):

    return jsonify(
        MetaFlac(f"song_folder/{song_title}.flac").get_vorbis_comment()
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8088,
        debug=True,
        threaded=True
    )