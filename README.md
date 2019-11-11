# Drone Racing Competition Leaderboard

Leaderboard for drone racing competition.

See https://github.com/nathan815/drone-competition

## Installation/Running Locally
Requires: [yarn](https://yarnpkg.com/), [nodejs](https://nodejs.org/), [pipenv](https://pipenv-fork.readthedocs.io/en/latest/)

1. Clone repo
2. Install frontend JS dependencies
   1. `cd frontend`
   2. `yarn install`
   3. `yarn build` (or `yarn start` for development server - auto rebuild & reload) 
3. Install python dependencies and configure backend
   1. `cd api`
   2. `pipenv install`
   3. `cp .env.example .env`. Then fill out Cassandra credentials in .env file.
   4. `touch ips.txt`. Add comma separated list of Cassandra node IP addresses (contact points) in ips.txt file.

Start backend server: `pipenv run python src/app.py`
   
Leaderboard will be accessible at http://localhost:3001/ if you ran `yarn build` because Flask is configured to serve from frontend's build output directory at `/` route. 

If you started the dev server, then you can access the leaderboard at localhost:3000. The python api server, which the frontend will communicate with, will also need to be running.
