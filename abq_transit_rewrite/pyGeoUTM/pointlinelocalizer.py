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


from .coordinate import Coordinate
from collections import namedtuple
from typing import List
from functools import reduce
from math import pow, sqrt, nan
import sys
DOUBLE_MAX = sys.float_info.max

LocalizerResult = namedtuple('LocalizerResult', ['t', 'd', 'intersection'])

def localize_line(point: Coordinate, line: List[Coordinate]) -> LocalizerResult:
    if len(line) < 2:
        return None
    minDist = DOUBLE_MAX
    bestResult = LocalizerResult(nan, nan, point)
    minIndex = 0
    a = line[0]
    for idx in range(1, len(line)):
        b = line[idx]
        localResult = localize_points(a, b, point)
        if localResult:
            t = localResult.t
            absD = abs(localResult.d)
            if 0.0 <= t and t <= 1.0 and absD < minDist:
                minDist = absD
                minIndex = idx - 1
                bestResult = localResult
            a = b
    return LocalizerResult(bestResult.t + minIndex, bestResult.d, bestResult.intersection)


def localize_points(a: Coordinate, b: Coordinate, w: Coordinate) -> LocalizerResult:
    ax = a.x
    ay = a.y
    bx = b.x
    by = b.y
    wx = w.x
    wy = w.y

    if (ax == bx) and (ay == by):
        if (ax == wx) and (ay == wy):
            return LocalizerResult(1, 0, a)
        else:
            return None
    elif (ax == wx) and (ay == wy):
        return LocalizerResult(0, 0, a)
    elif (bx == wx) and (by == wy):
        return LocalizerResult(1, 0, b)

    denom = pow(bx - ax, 2.0) + pow(by - ay, 2.0)
    t = ((wx - ax) * (bx - ax) + (wy - ay) * (by - ay)) / (denom)
    ix = ax + t * (bx - ax)
    iy = ay + t * (by - ay)

    dist = ((by - ay) * wx - (bx - ax) * wy + bx * ay - by * ax) / (sqrt(denom))

    return LocalizerResult(t, dist, Coordinate(ix, iy))