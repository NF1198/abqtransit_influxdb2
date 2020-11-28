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

import sys
from unittest import TestCase

from .. import Coordinate, LatLonCoord, localize_line, localize_points

class TestCoordinate(TestCase):
    def test_coordinate(self):
        coord = Coordinate(100, 200)
        self.assertAlmostEqual(100, coord.x, 6)
        self.assertAlmostEqual(200, coord.y, 6)

    def test_latloncoord(self):
        coord = LatLonCoord(30.5, -100.5)
        self.assertAlmostEqual(30.5, coord.lat, 6)
        self.assertAlmostEqual(-100.5, coord.lon, 6)

    def test_localize_points(self):
        a = Coordinate(0, 0)
        b = Coordinate(10, 10)
        c = Coordinate(1, 1)
        c_low = Coordinate(1, 0.9)
        c_high = Coordinate(1, 1.1)
        self.assertAlmostEqual(0.1, localize_points(a, b, c).t, 6)
        self.assertAlmostEqual(0.0, localize_points(a, b, c).d, 6)
        self.assertGreater(0, localize_points(a, b, c_high).d, 6)
        self.assertLess(0, localize_points(a, b, c_low).d, 6)

    def test_localize_line(self):
        line = [Coordinate(0, 0), Coordinate(5, 5), Coordinate(10, 10)]
        c = Coordinate(6, 6)
        self.assertAlmostEqual(1.2, localize_line(c, line).t, 6)

from ..projections.utm import getInstance as getUTMInstance, findUTMZone, getInverseInstance as getUTMInverseInstance

class TestUTMProjection(TestCase):

    def test_utm_forward(self):
        loc = LatLonCoord(35, -106)
        zone = findUTMZone(loc)
        self.assertEqual(13, zone)
        coord_expect = Coordinate(408746.75, 3873499.85) 
        utm = getUTMInstance(zone)
        coord = utm(loc)
        self.assertAlmostEqual(coord_expect.x, coord.x, 2)
        self.assertAlmostEqual(coord_expect.y, coord.y, 2)

    def test_utm_inverse(self):
        coord = Coordinate(408746.75, 3873499.85)
        zone = 13
    
        loc_expect = LatLonCoord(35, -106) 
        utm_inv = getUTMInverseInstance(zone, False)
        loc = utm_inv(coord)
        self.assertAlmostEqual(loc_expect.lat, loc.lat, 2)
        self.assertAlmostEqual(loc_expect.lon, loc.lon, 2)
        