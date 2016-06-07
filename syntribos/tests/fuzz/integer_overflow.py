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
from syntribos.issue import Issue
from syntribos.tests.fuzz import base_fuzz
from syntribos.checks import time_diff as time_diff


text = ("This request may have triggered a buffer overflow vulnerability."
        " This happens when the application is unable to handle input"
        " from the user, and may result in crashes, or in the worst case,"
        " code execution.")


class IntOverflowBody(base_fuzz.BaseFuzzTestCase):
    test_name = "INT_OVERFLOW_BODY"
    test_type = "data"
    data_key = "integer-overflow.txt"

    """UNUSED AT THIS POINT"""
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
        self.test_default_issues()
        self.diff_signals.register(time_diff(self.init_response, self.resp))

        confidence = "Low"
        """
        time_diff = self.config.time_difference_percent / 100
        if (self.resp.elapsed.total_seconds() >
                time_diff * self.init_response.elapsed.total_seconds()):
        """
        if "TIME_DIFF_OVER" in self.diff_signals:
            if "STATUS_CODE_CHANGE" not in self.diff_signals:
                confidence = "Medium"

            self.register_issue(Issue(test="int_timing", severity="Medium",
                                confidence=confidence, text=text,
                                diff_signals=self.diff_signals))


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
