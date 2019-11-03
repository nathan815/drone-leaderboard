import datetime
from flask import Flask, request, jsonify
from flask.json import JSONEncoder
from db import CompetitionDatabase, get_cluster


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        return super().default(obj)


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

print('Connecting to DSE...')
db = CompetitionDatabase(get_cluster())
print('Connected')


@app.route('/flights')
def flights():
    maximum_flights = 50
    limit: int = min(int(request.args.get('limit', 10)), maximum_flights)
    return jsonify(db.get_flights_sorted_by_duration(limit))


@app.route('/groups')
def groups():
    return jsonify(list(db.get_groups()))


@app.route('/pilots')
def pilots():
    return jsonify(list(db.get_pilots()))


def main():
    app.run(port=3001, debug=True)


if __name__ == "__main__":
    main()
