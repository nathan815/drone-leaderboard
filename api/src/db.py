import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime

from dse.auth import PlainTextAuthProvider
from dse.cluster import Cluster

logger = logging.getLogger(__name__)


@dataclass
class Pilot:
    name: str
    org: str
    major: str
    group: str


@dataclass
class Flight:
    id: uuid.UUID
    station_id: uuid.UUID
    pilot: Pilot
    start_time: datetime
    end_time: datetime


def get_cluster(cluster_ips_file: str = 'ips.txt') -> Cluster:
    auth = PlainTextAuthProvider(username=os.environ['DSE_USER'], password=os.environ['DSE_PASS'])
    with open(cluster_ips_file) as ips_file:
        ips = list(map(lambda ele: ele.strip(), ips_file.read().split(",")))
    logger.info(f'Read cluster nodes IPs from {cluster_ips_file}: {ips}')
    return Cluster(contact_points=ips, auth_provider=auth)


class CompetitionDatabase:
    def __init__(self, cluster: Cluster):
        self.session = cluster.connect('competition')

    def get_flights_sorted_by_time(self, limit: int = None) -> list:
        cql = "select flight_id, toTimestamp(flight_id) as start_ts, latest_ts, " \
              "       valid, station_id, name, org_college, major, group " \
              "from competition.positional " \
              "group by flight_id"
        rows = self.session.execute(cql)
        rows = sorted(rows, key=lambda a: a.latest_ts - a.start_ts)
        if limit:
            rows = rows[:limit]
        flights = []
        for row in rows:
            if row.valid:
                flights.append(Flight(
                    id=row.flight_id,
                    station_id=row.station_id,
                    start_time=row.start_ts,
                    end_time=row.latest_ts,
                    pilot=Pilot(row.name, row.org_college, row.major, row.group),
                ))
        return flights

    def get_groups(self) -> set:
        rows = self.session.execute("select group from competition.positional group by flight_id")
        groups = set()
        for row in rows:
            groups.add(row.group)
        return groups


if __name__ == "__main__":
    db = CompetitionDatabase(get_cluster())
    print('All flights:')
    rs = db.get_flights()
    for r in rs:
        print(r)
