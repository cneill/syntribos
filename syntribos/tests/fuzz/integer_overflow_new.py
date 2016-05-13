# Copyright 2015 Rackspace
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

from syntribos.issue import Issue
from syntribos.tests.fuzz import base_fuzz
import syntribos.checks.time


class IntOverflowBody(base_fuzz.BaseFuzzTestCase):
    test_name = "INT_OVERFLOW_BODY"
    test_type = "data"
    data_key = "integer-overflow.txt"
    text = ("This request may have triggered a buffer overflow vulnerability."
            " This happens when the application is unable to handle input"
            " from the user, and may result in crashes, or in the worst case,"
            " code execution.")
    bad_slugs = [
        {"slug": "TIME_DIFF_OVER", "points": 5},
        {"slug": "STACK_TRACE", "points": 10},
        {"slug": "HTTP_STATUS_CODE_5XX", "points": 5}
    ]
    bad_tags = [
        {"tag": "SERVER_FAIL", "points": 5},
        {"tag": "CONNECTION_TIMEOUT", "points": 7},
        {"tag": "CONNECTION_FAIL", "points": 10}
    ]

    def test_case(self):
        time_signal = syntribos.checks.time.compare_responses(self.init_response, self.resp)
        if time_signal:
            self.resp_signals.append(time_signal)
        bad_signals = self.check_bad_signals()
        if bad_signals:
            self.register_issue_from_signals(
                Issue(test="int_timing", severity="High",
                      confidence=0, text=self.text), bad_signals)

    @classmethod
    def check_bad_signals(cls):
        bad_signals = []
        for i in cls.resp_signals:
            sys.stdout.write("RESP: " + i)
        for i in cls.init_signals:
            sys.stdout.write("INIT: " + i)

        cls.resp_signals = [x for x in cls.resp_signals if x is not None]
        for signal in cls.resp_signals:
            match = signal.get_highest_match(
                bad_slugs=cls.bad_slugs, bad_tags=cls.bad_tags)
            if match:
                bad_signals.append({"match": match, "signal": signal})
        for b in bad_signals:
            sys.stdout.write(b)
        return bad_signals


class IntOverflowParams(IntOverflowBody):
    test_name = "INT_OVERFLOW_PARAMS"
    test_type = "params"


class IntOverflowHeaders(IntOverflowBody):
    test_name = "INT_OVERFLOW_HEADERS"
    test_type = "headers"


class IntOverflowURL(IntOverflowBody):
    test_name = "INT_OVERFLOW_URL"
    test_type = "url"
    url_var = "FUZZ"
