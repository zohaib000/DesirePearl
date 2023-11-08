from flask import Flask, request
from flask import jsonify
import json
from scraper import scrape

app = Flask(__name__, static_url_path='/scraper', static_folder='scraper')


@app.route('/getData', methods=["GET"])
def getData():
    nights = int(request.args.get('nights'))
    adults = int(request.args.get('adults'))
    date = request.args.get('date')
    data = scrape(date, nights, adults)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
