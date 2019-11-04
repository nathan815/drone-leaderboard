import datetime
from flask import Flask, request, jsonify
from flask.json import JSONEncoder
from flask_cors import CORS

from db import CompetitionDatabase, get_cluster


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        return super().default(obj)


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
CORS(app)

print('Connecting to DSE...')
db = CompetitionDatabase(get_cluster())
print('Connected')


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
    group_filter: str = request.args.get('groups', None)
    groups = set(group_filter.split(',')) if group_filter else None
    return jsonify(db.get_flights_sorted_by_duration(limit, groups))


@app.route('/filter_values')
def get_filter_options():
    """
    Outputs JSON object containing all the filter values for groups, majors, and organizations
    """
    filter_options = {
        'groups': list(db.get_groups()),
        'majors': list(db.get_majors()),
        'organizations': list(db.get_orgs()),
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
