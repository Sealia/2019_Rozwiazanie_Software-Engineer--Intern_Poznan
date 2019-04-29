from io import BytesIO

from flask import Flask, request, render_template, jsonify, send_file
from flask_api import status

import my_module

app = Flask(__name__)

@app.route("/mozaika", methods=["GET"])
def mosaic_maker():
    losowo = request.args.get("losowo")
    rozdzielczosc = request.args.get("rozdzielczosc")
    URLS = request.args.get("zdjecia")
    try:
        images = URLS.split(",")
    except:
        return jsonify({"Error": "404", "message": "Invalid URL"}),404
    if 1>len(images)>8:
    	return jsonify({'Error':'400','message':'Incorrect number of Urls'}),400
    return my_module.body(images, rozdzielczosc, losowo)


if __name__ == "__main__":
    app.run(debug=True)