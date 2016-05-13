# Copyright 2016 Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import syntribos.tests.fuzz.config
import syntribos.checker
import syntribos.signal


class LengthDiff(syntribos.checker):

    config = syntribos.tests.fuzz.config.BaseFuzzConfig()

    def __init__(self, resp1, resp2):
        self.resp1 = resp1
        self.resp2 = resp2

    def check(self):
        resp1_seconds = self.resp1.elapsed.total_seconds()
        resp2_seconds = self.resp2.elapsed.total_seconds()
        factor = self.config.time_difference_percent / 100
        return resp2_seconds > resp1_seconds * factor


class LengthDiffSignal(syntribos.signal):

    signal_type = "LENGTH_DIFF"

    @classmethod
    def from_responses(cls, resp1, resp2):
        return cls()

    @classmethod
    def get_slugs(cls):
        return ["LENGTH_DIFF_OVER", "LENGTH_DIFF_UNDER"]
