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
import sys

import syntribos.tests.fuzz.config
import syntribos.signal

config = syntribos.tests.fuzz.config.BaseFuzzConfig()


def compare_responses(resp1, resp2):
    if type(resp1) is str:
        sys.stdout.write(resp1)
    resp1_seconds = resp1.elapsed.total_seconds()
    resp2_seconds = resp2.elapsed.total_seconds()
    factor = config.time_difference_percent / 100.0
    diff = resp2_seconds / resp1_seconds

    if (resp2_seconds >= resp1_seconds * factor or
            resp2_seconds * factor <= resp1_seconds):
        return TimeDiffSignal(resp1=resp1, resp2=resp2, diff=diff)
    return None


class TimeDiffSignal(syntribos.signal):

    signal_type = "TIME_DIFF"

    def __init__(self, *args, **kwargs):
        super(TimeDiffSignal, self).__init__(*args, **kwargs)

        self.resp1 = kwargs.pop("resp1", None)
        self.resp2 = kwargs.pop("resp2", None)
        self.diff = kwargs.pop("diff", 0)
        self.strength = 1

        if self.diff > 1:
            self.slug = "TIME_DIFF_OVER"
        elif self.diff < 1:
            self.slug = "TIME_DIFF_UNDER"

    @classmethod
    def get_slugs(cls):
        return ["TIME_DIFF_OVER", "TIME_DIFF_UNDER"]
