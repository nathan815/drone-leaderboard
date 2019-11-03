from flask import Flask, jsonify
from db import CompetitionDatabase, get_cluster

print('Connecting to DSE...')
db = CompetitionDatabase(get_cluster())
print('Connected')

app = Flask(__name__)


@app.route('/flights')
def flights():
    return jsonify(db.get_flights_sorted_by_time(10))


@app.route('/groups')
def groups():
    return jsonify(list(db.get_groups()))


def main():
    app.run(port=3001, debug=True)


if __name__ == "__main__":
    main()
