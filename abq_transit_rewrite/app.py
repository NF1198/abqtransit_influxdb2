# -*- coding: utf-8 -*-
import time
import urllib.request
from os import path
import json
from datetime import datetime, timedelta
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from pyGeoUTM import LatLonCoord
from pyGeoUTM.projections.utm import getInstance as getUTMInstance, findUTMZone

from flask import Flask, make_response

app = Flask(__name__)

#ALL_ROUTES_URL = f'file://{path.abspath("./allroutes_2020_10_19.json")}'
ALL_ROUTES_URL = 'http://data.cabq.gov/transit/realtime/route/allroutes.json'
print (f'ALL_ROUTES_URL: {ALL_ROUTES_URL}')
SOURCE_TIMEZONE_NAME = 'America/Denver'

def now():
    tzinfo = zoneinfo.ZoneInfo(SOURCE_TIMEZONE_NAME)
    return datetime.now(tz=tzinfo)

def fix_time(time_string, reference_time, check_back_in_time=False):
    rt = reference_time
    hh, mm, ss = (int(s) for s in time_string.split(':'))
    fixed_time = datetime(rt.year, rt.month, rt.day, hh, mm, ss, tzinfo=rt.tzinfo)
    if check_back_in_time and fixed_time > reference_time:
        fixed_time -= timedelta(days=1)
    return fixed_time

def mph_to_kph(mph):
    mph = float(mph)
    return 1.60934 * mph

TAGS = sorted(['route_short_name', 'trip_id', 'vehicle_id'])
FIELDS = sorted(['latitude:lat', 'longitude:lon', 'easting', 'northing', 'speed_kph', 'utm_zone'])
# OTHER_FIELDS = ['next_stop_id', 'next_stop_name', 'next_stop_sched_time']

def make_kvp(tag, data, quote=False):
    abbr_idx  = tag.find(':')
    key       = tag if abbr_idx == -1 else tag[abbr_idx+1:]
    value_key = tag if abbr_idx == -1 else tag[:abbr_idx]
    print((key, value_key, abbr_idx != -1))
    value = data[value_key]
    return f'{key}="{value}"' if isinstance(value, str) and quote else f'{key}={value}'

def json_to_influx(vehicle):
    timestamp = int(vehicle['msg_time'].timestamp() * 1e9)
    tags = [make_kvp(k, vehicle, False) for k in TAGS]
    fields = [make_kvp(k, vehicle, True) for k in FIELDS]
    return f'vehicle,{",".join(tags)} {",".join(fields)} {timestamp}'

@app.route('/')
def allroutes():
    current_time = now()
    with urllib.request.urlopen(ALL_ROUTES_URL) as f:
        data = json.loads(f.read().decode('cp1252'))
        utmProjection = None
        zone = None
        for vehicle in data['allroutes']:
            try:
                vehicle['msg_time'] = fix_time(vehicle['msg_time'], current_time, True)
                vehicle['next_stop_sched_time'] = fix_time(vehicle['next_stop_sched_time'], current_time, True)
                vehicle['speed_kph'] = mph_to_kph(vehicle['speed_mph'])
                del vehicle['speed_mph']
                vehicle['heading'] = float(vehicle['heading'])
                latlon = LatLonCoord(vehicle['latitude'], vehicle['longitude'])
                if not utmProjection or not zone:
                    zone = findUTMZone(latlon)
                    utmProjection = getUTMInstance(zone)
                coord = utmProjection(latlon)
                vehicle['easting'] = coord.x
                vehicle['northing'] = coord.y
                vehicle['utm_zone'] = zone
            except:
                pass
        data['allroutes'].sort(key=lambda v: (int(v['route_short_name']), v['easting']))
        resp = make_response("\n".join(list((json_to_influx(v) for v in data['allroutes']))), 200)
        resp.headers['Content-Type'] = 'text/plain'
        return resp