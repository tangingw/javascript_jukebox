from flask import Flask, jsonify


app = Flask(__name__)

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


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8088,
        debug=True,
        threaded=True
    )