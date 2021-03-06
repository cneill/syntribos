# Copyright 2016 Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from syntribos.issue import Issue
from syntribos.tests.fuzz import base_fuzz


class CommandInjectionBody(base_fuzz.BaseFuzzTestCase):
    test_name = "COMMAND_INJECTION_BODY"
    test_type = "data"
    data_key = "command_injection.txt"
    failure_keys = [
        'uid=',
        'root:',
        'default=',
        '[boot loader]']

    def test_case(self):
        self.test_default_issues()
        failed_strings = self.data_driven_failure_cases()
        if failed_strings:
            self.register_issue(
                Issue(test="command_injection",
                      severity="High",
                      confidence="Medium",
                      text=("A string known to be commonly returned after a "
                            "successful command injection attack was "
                            "included in the response. This could indicate "
                            "a vulnerability to command injection "
                            "attacks.").format(failed_strings)
                      )
            )
        elif self.resp.elapsed.total_seconds() >= 10:
            self.register_issue(
                Issue(test="command_injection",
                      severity="High",
                      confidence="Medium",
                      text=("The time elapsed between the sending of "
                            "the request and the arrival of the res"
                            "ponse exceeds the expected amount of time, "
                            "suggesting a vulnerability to command "
                            "injection attacks.").format(self.resp.elapsed)
                      )
            )


class CommandInjectionParams(CommandInjectionBody):
    test_name = "COMMAND_INJECTION_PARAMS"
    test_type = "params"


class CommandInjectionHeaders(CommandInjectionBody):
    test_name = "COMMAND_INJECTION_HEADERS"
    test_type = "headers"


class CommandInjectionURL(CommandInjectionBody):
    test_name = "COMMAND_INJECTION_URL"
    test_type = "url"
    url_var = "FUZZ"
