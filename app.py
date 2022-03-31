import os.path
from flask import Flask, jsonify, send_file
from flask import render_template, abort, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from mylib.metaflac import MetaFlac


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config["UPLOAD_FOLDER"] = "song_folder"
app.config.from_object(__name__)

CORS(app)

ALLOWED_EXTENSIONS = {'flac'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(405)
def return_not_found(error):

    return jsonify(
        {
            "status": 405,
            "error_msg": "method not allow"
        }
    ), 405


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


@app.route("/my_song_folder", methods=["GET", "POST"])
@app.route("/my_song_folder/<song_name>")
def get_song_file(song_name=None):

    if song_name:
        return send_file(
            f"song_folder/{song_name}.flac", mimetype="audio/flac"
        )

    if request.method == "POST":

        upload_file = request.files["file"]

        if upload_file and allowed_file(upload_file.filename):

            filename = secure_filename(upload_file.filename)
            filename_with_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if not os.path.exists(filename_with_path):
                upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                return jsonify(
                    {
                        "status": 200,
                        "message": "Upload Successful"
                    }
                )
        
            return jsonify(
                {
                    "status": 514,
                    "message": "Duplicate Filename"
                }
            )
        
        return jsonify(
            {
                    "status": 513,
                    "message": "Incorrect Filetype"
            }
        )

    abort(403)


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