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

LatLonCoord = namedtuple('LatLonCoord', ['lat', 'lon'])