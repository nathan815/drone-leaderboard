import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from dse.auth import PlainTextAuthProvider
from dse.cluster import Cluster

logger = logging.getLogger(__name__)


@dataclass(eq=True, frozen=True)
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
    duration_ms: int = 0

    def __post_init__(self):
        delta: timedelta = self.end_time - self.start_time
        self.duration_ms = int(delta.total_seconds() * 1000)


def get_cluster(cluster_ips_file: str = 'ips.txt') -> Cluster:
    auth = PlainTextAuthProvider(username=os.environ['DSE_USER'], password=os.environ['DSE_PASS'])
    with open(cluster_ips_file) as ips_file:
        ips = list(map(lambda ele: ele.strip(), ips_file.read().split(",")))
    logger.info(f'Read cluster nodes IPs from {cluster_ips_file}: {ips}')
    return Cluster(contact_points=ips, auth_provider=auth)


class CompetitionDatabase:
    def __init__(self, cluster: Cluster):
        self.session = cluster.connect('competition')

    def get_flights_sorted_by_duration(self, limit: int = None) -> list:
        cql = "select flight_id, toTimestamp(flight_id) as start_ts, latest_ts, " \
              "       valid, station_id, name, org_college, major, group " \
              "from competition.positional " \
              "group by flight_id"
        rows = self.session.execute(cql)
        rows = sorted(rows, key=lambda row: row.latest_ts - row.start_ts, reverse=True)
        flights = []
        pilots = set()
        for row in rows:
            if not row.valid:
                continue
            pilot = Pilot(row.name, row.org_college, row.major, row.group)
            # ensure each pilot is represented only once
            if pilot not in pilots:
                flights.append(Flight(
                    id=row.flight_id,
                    pilot=pilot,
                    station_id=row.station_id,
                    start_time=row.start_ts,
                    end_time=row.latest_ts
                ))
                pilots.add(pilot)
        if limit:
            flights = flights[:limit]
        return flights

    def get_flights(self):
        return self.session.execute("select * from competition.positional group by flight_id")

    def get_groups(self) -> set:
        rows = self.get_flights()
        groups = set()
        for row in rows:
            groups.add(row.group)
        return groups

    def get_pilots(self) -> set:
        rows = self.get_flights()
        pilots = set()
        for row in rows:
            pilots.add(Pilot(row.name, row.org_college, row.major, row.group))
        return pilots
