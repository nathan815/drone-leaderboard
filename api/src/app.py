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
    - majors: comma separated list of pilot majors to include
    - orgs: comma separated list of pilot orgs to include
    Note: If any of the filters above are not included or empty, the filter will be ignored
    Note: Pass 'none' to a filter to include those rows with unspecified value for given field
    Example:
    /leaderboard?limit=20&groups=faculty,students&orgs=EMU
    """
    default_limit = 10
    min_limit = 1
    max_limit = 50
    limit_input: int = int(request.args.get('limit', default_limit))
    limit = max(min(limit_input, max_limit), min_limit)

    def field_filter(name):
        filter_text = request.args.get(name, None)
        filter_values = filter_text.split(',') if filter_text else None
        if not filter_values:
            return None

        filter_values_set = set()
        for value in filter_values:
            if value == 'none':
                filter_values_set.add('')
                filter_values_set.add(None)
            else:
                filter_values_set.add(value)
        return filter_values_set

    return jsonify(db.get_flights_sorted_by_duration(limit, field_filter('groups'), field_filter('majors'), field_filter('orgs')))


@app.route('/filter_values')
def get_filter_options():
    """
    Outputs JSON object containing all the filter values for groups, majors, and organizations
    """
    filter_options = {
        'groups': sorted(list(db.get_groups())),
        'majors': sorted(list(db.get_majors())),
        'orgs': sorted(list(db.get_orgs())),
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
