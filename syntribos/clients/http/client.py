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
from syntribos.clients.http.base_http_client import HTTPClient
from syntribos.clients.http.signals import HTTPStatusCodeSignal as http_code


class SynHTTPClient(HTTPClient):

    def request(self, method, url, headers=None, params=None, data=None,
                requestslib_kwargs=None):
        # CCNEILL: ADD 10-SECOND TIMEOUT IF NONE
        if not requestslib_kwargs:
            requestslib_kwargs = {"timeout": 10}
        elif not requestslib_kwargs.get("timeout", None):
            requestslib_kwargs["timeout"] = 10

        response, signals = super(SynHTTPClient, self).request(
            method, url, headers=headers, params=params, data=data,
            requestslib_kwargs=requestslib_kwargs)
        signals.register(self.check_status_code(response))
        return (response, signals)

    def send_request(self, r):
        response, signals = self.request(
            method=r.method, url=r.url, headers=r.headers, params=r.params,
            data=r.data)
        return (response, signals)

    def check_status_code(self, response):
        """Checks response for HTTP status codes that may indicate issues."""
        return http_code.from_response_object(response)
