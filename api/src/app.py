import os
import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask.json import JSONEncoder
from flask_cors import CORS

from db import CompetitionDatabase, get_cluster


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        return super().default(obj)


app = Flask(__name__, static_folder='../../frontend/build')
app.json_encoder = CustomJSONEncoder
CORS(app)

print('Connecting to DSE...')
db = CompetitionDatabase(get_cluster())
print('Connected')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/leaderboard')
def leaderboard():
    """
    Outputs JSON array of best flights by duration
    URL query params:
    - limit: int 1-50, default=10
    - groups: comma separated list of pilot groups to include
    example:
    /leaderboard?limit=20&groups=faculty,students
    """
    default_limit = 10
    min_limit = 1
    max_limit = 50
    limit_input: int = int(request.args.get('limit', default_limit))
    limit = max(min(limit_input, max_limit), min_limit)

    def filter(name):
        filter_text = request.args.get(name, None)
        return set(filter_text.split(',')) if filter_text else None

    return jsonify(db.get_flights_sorted_by_duration(limit, filter('groups'), filter('majors'), filter('orgs')))


@app.route('/filter_values')
def get_filter_options():
    """
    Outputs JSON object containing all the filter values for groups, majors, and organizations
    """
    filter_options = {
        'groups': list(db.get_groups()),
        'majors': list(db.get_majors()),
        'orgs': list(db.get_orgs()),
    }
    return jsonify(filter_options)


@app.route('/pilots')
def all_pilots():
    """
    Outputs JSON array of all pilots present in flight data
    """
    return jsonify(list(db.get_pilots()))


def main():
    app.run(port=3001, debug=True)


if __name__ == "__main__":
    main()
