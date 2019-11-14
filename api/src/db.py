import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

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
    rank: int = 0

    def __post_init__(self):
        delta: timedelta = self.end_time - self.start_time
        self.duration_ms = int(delta.total_seconds() * 1000)


def get_cluster(cluster_ips_file: str = 'ips.txt') -> Cluster:
    auth = PlainTextAuthProvider(username=os.environ['DSE_USER'], password=os.environ['DSE_PASS'])
    with open(cluster_ips_file) as ips_file:
        ips = [ip.strip() for ip in ips_file.read().split(",")]
    logger.info(f'Read cluster nodes IPs from {cluster_ips_file}: {ips}')
    return Cluster(contact_points=ips, auth_provider=auth)


class CompetitionDatabase:
    def __init__(self, cluster: Cluster):
        self.session = cluster.connect('competition')

    def get_flights_sorted_by_duration(self,
                                       limit: int = None,
                                       groups: set = None,
                                       majors: set = None,
                                       orgs: set = None) -> list:
        cql = "select flight_id, toTimestamp(flight_id) as start_ts, latest_ts, " \
              "       valid, station_id, name, org_college, major, group " \
              "from competition.positional " \
              "group by flight_id"
        rows = self.session.execute(cql)
        rows = sorted(rows, key=lambda row: row.latest_ts - row.start_ts)
        flights = []
        pilots = set()
        rank = 0

        for row in rows:
            if not row.valid:
                continue
            pilot = Pilot(row.name, row.org_college, row.major, row.group)

            # ensure each pilot is represented only once
            if pilot in pilots:
                continue

            pilots.add(pilot)
            rank += 1

            group_excluded = groups and row.group not in groups
            major_excluded = majors and row.major not in majors
            org_excluded = orgs and row.org_college not in orgs

            # now actually add this flight to our flights list if it isn't filtered out
            if not (group_excluded or major_excluded or org_excluded):
                flights.append(Flight(
                    id=row.flight_id,
                    pilot=pilot,
                    station_id=row.station_id,
                    start_time=row.start_ts,
                    end_time=row.latest_ts,
                    rank=rank
                ))

            if len(flights) == limit:
                break

        return flights

    def get_flights(self):
        return self.session.execute("select * from competition.positional group by flight_id")

    def latest_flights(self):
        rows = self.session.execute("select * from competition.positional group by flight_id limit 2")
        print(rows)
        names = []
        for row in rows:
            names.append(row.name)
        return names

    def get_groups(self) -> set:
        return self._get_unique_column_values(lambda row: row.group)

    def get_majors(self) -> set:
        return self._get_unique_column_values(lambda row: row.major)

    def get_orgs(self) -> set:
        return self._get_unique_column_values(lambda row: row.org_college)

    def _get_unique_column_values(self, extract_field: Callable) -> set:
        rows = self.get_flights()
        values = set()
        for row in rows:
            if row.valid:
                field_value = extract_field(row)
                values.add('none' if field_value == '' or field_value is None else field_value)
        return values

    def get_pilots(self) -> set:
        rows = self.get_flights()
        pilots = set()
        for row in rows:
            if row.valid:
                pilots.add(Pilot(row.name, row.org_college, row.major, row.group))
        return pilots
