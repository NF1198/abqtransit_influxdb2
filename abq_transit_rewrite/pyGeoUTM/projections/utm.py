# 
# Copyright 2017-2021 tauTerra, LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# Adapted from : http://www.rcn.montana.edu/resources/converter.aspx
# Ref: http://www.uwgb.edu/dutchs/UsefulData/UTMFormulas.HTM
# 
# A UTM -> Lat/Long (or vice versa) converter adapted from the script used at
#     http://www.uwgb.edu/dutchs/UsefulData/ConvertUTMNoOZ.HTM
# 
# 

from collections import namedtuple
from math import sqrt, pi, floor, sin, cos, tan
from ..latloncoord import LatLonCoord
from ..coordinate import Coordinate
from typing import Callable

Datum = namedtuple('Datum', ['eqRad', 'flat'])
WGS84 = Datum(6378137.0, 298.2572236) # WGS 84
NAD83 = Datum(6378137.0, 298.2572236) # NAD 83
GRS80 = Datum(6378137.0, 298.2572215) # GRS 80
WGS72 = Datum(6378135.0, 298.2597208) # WGS 72
AUS65 = Datum(6378160.0, 298.2497323) # Austrailian 1965
Kras1940 = Datum(6378245.0, 298.2997381) # Krasovsky 1940
NAmer1927 = Datum(6378206.4, 294.9786982) # North American 1927
Intl1924 = Datum(6378388.0, 296.9993621) # International 1924
Hayford1909 = Datum(6378388.0, 296.9993621) # Hayford 1909
Clarke1880 = Datum(6378249.1, 293.4660167) # Clarke 1880
Clarke1866 = Datum(6378206.4, 294.9786982) # Clarke 1866
Airy1830 = Datum(6377563.4, 299.3247788) # Airy 1830
Bessel1841 = Datum(6377397.2, 299.1527052) # Bessel 1841
Everset1830 = Datum(6377276.3, 300.8021499) # Everest 1830

def findUTMZone(latlon: LatLonCoord) -> int:
    lngd = latlon.lon
    utmz = 1 + int(floor((lngd + 180.0) / 6.0))
    return utmz

def getInstance(zone: int, datum: Datum = WGS84) -> Callable[[LatLonCoord], Coordinate]:
    utmz = zone
    zcm = 3 + 6 * (utmz - 1) - 180
    d = datum

    # constants taken from or calculated from the datum
    a = d.eqRad
    f = 1.0 / d.flat
    b = a * (1 - f)               # polar radius
    esq = (1 - pow((b / a), 2.0)) # e-squared for use in expansions
    e = sqrt(esq)                 # eccentricity
    e0sq = e * e / (1.0 - pow(e, 2.0)) # squared - always even powers

    # constants used in calculations
    k0 = 0.9996
    drad = pi / 180.0

    def _instance(latlon: LatLonCoord) -> Coordinate:
        lngd = latlon.lon
        lat = latlon.lat
        phi = lat * drad

        N = a / sqrt(1 - pow(e * sin(phi), 2.0))
        T = pow(tan(phi), 2.0)
        C = e0sq * pow(cos(phi), 2.0)
        A = (lngd - zcm) * drad * cos(phi)
        A2 = A * A
        C2 = C * C
        T2 = T * T

        # calculate M (USGS style)
        M = phi * (1.0 - esq * (0.25 + esq * (3.0 / 64.0 + 5.0 * esq / 256.0)))
        M -= sin(2.0 * phi) * (esq * (3.0 / 8.0 + esq * (3.0 / 32.0 + 45.0 * esq / 1024.0)))
        M += sin(4.0 * phi) * (esq * esq * (15.0 / 256.0 + esq * 45.0 / 1024.0))
        M -= sin(6.0 * phi) * (esq * esq * esq * (35.0 / 3072.0))
        M *= a     #Arc length along standard meridian

        M0 = 0.0        # if another point of origin is used than the equator

        # calculate the UTM values...
        # first the easting
        x = k0 * N * A * (1 + A2 * ((1 - T + C) / 6.0 + A2 * (5 - 18 * T + T2 + 72 * C - 58 * e0sq) / 120.0)) #Easting relative to CM
        x += 500000 # standard easting

        # now the northing
        y = k0 * (M - M0 + N * tan(phi) * (A2 * (0.5 + A2 * ((5 - T + 9 * C + 4 * C2) / 24.0 + A2 * (61 - 58 * T + T2 + 600 * C - 330 * e0sq) / 720.0))))    # first from the equator
        if y < 0:
            y = 10000000 + y   # add in false northing if south of the equator

        return Coordinate(x, y)
    return _instance

def getInverseInstance(zone: int, southern: bool, datum: Datum = WGS84) -> Callable[[Coordinate], LatLonCoord]:
    utmz = zone
    d = datum
    south = southern
    zcm = 3 + 6 * (utmz - 1) - 180

    # constants taken from or calculated from the datum
    a = d.eqRad
    f = 1.0 / d.flat
    b = a * (1 - f)                     # polar radius
    esq = (1 - pow((b / a), 2))    # e-squared for use in expansions
    e = sqrt(esq)                  # eccentricity
    e0sq = e * e / (1.0 - pow(e, 2))     # squared - always even powers
    e1 = (1 - sqrt(1 - pow(e, 2))) / (1 + sqrt(1 - pow(e, 2)))

    # constants used in calculations
    k = 1.0
    k0 = 0.9996
    drad = pi / 180.0

    def _instance(c: Coordinate) -> LatLonCoord:
        x = c.x
        y = c.y

        M0 = 0.0

        if not south:
            M = M0 + y / k0    # Arc length along standard meridian.
        else:
            M = M0 + (y - 10000000) / k
        mu = M / (a * (1 - esq * (0.25 + esq * (3 / 64.0 + 5 * esq / 256.0))))
        phi1 = mu + e1 * (1.5 - 27.0 * e1 * e1 / 32.0) * sin(2 * mu) + e1 * e1 * (21.0 / 16.0 - 55.0 * e1 * e1 / 32.0) * sin(4 * mu)   #Footprint Latitude
        phi1 = phi1 + e1 * e1 * e1 * (sin(6.0 * mu) * 151.0 / 96.0 + e1 * sin(8.0 * mu) * 1097.0 / 512.0)
        C1 = e0sq * pow(cos(phi1), 2)
        T1 = pow(tan(phi1), 2)
        N1 = a / sqrt(1 - pow(e * sin(phi1), 2))
        R1 = N1 * (1 - pow(e, 2)) / (1 - pow(e * sin(phi1), 2))
        D = (x - 500000) / (N1 * k0)
        phi = (D * D) * (0.5 - D * D * (5.0 + 3.0 * T1 + 10 * C1 - 4.0 * C1 * C1 - 9 * e0sq) / 24.0)
        phi = phi + pow(D, 6) * (61.0 + 90.0 * T1 + 298.0 * C1 + 45.0 * T1 * T1 - 252.0 * e0sq - 3.0 * C1 * C1) / 720.0
        phi = phi1 - (N1 * tan(phi1) / R1) * phi

        lat = floor(1000000 * phi / drad) / 1000000.0
        lng = D * (1.0 + D * D * ((-1.0 - 2.0 * T1 - C1) / 6.0 + D * D * (5.0 - 2.0 * C1 + 28.0 * T1 - 3.0 * C1 * C1 + 8.0 * e0sq + 24.0 * T1 * T1) / 120.0)) / cos(phi1)
        lng = zcm + lng / drad

        return LatLonCoord(lat, lng)
    return _instance
