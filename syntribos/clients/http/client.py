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

import requests

from syntribos.clients.http.base_http_client import HTTPClient
from syntribos.clients.http.config import HTTPConfig
from syntribos.clients.http.models import RequestObject
from syntribos.clients.http import signals as http_signal
import syntribos.signal

config = HTTPConfig()


class SynHTTPClient(HTTPClient):

    def send_request(self, r):
        """Send a request based on the provided RequestObject.

        :param r: Request object to be sent
        :type r: :class:`syntribos.client.http.models.RequestObject`
        :returns: Response object from requestslib
        :rtype: :class:`requests.Response`
        """
        response = None
        signals = []
        timeout = int(config.timeout)

        if type(r.kwargs) is not dict:
            r.kwargs = {"timeout": timeout}
        elif not r.kwargs["timeout"]:
            r.kwargs.update({"timeout": timeout})

        try:
            response = super(SynHTTPClient, self).request(
                r.method, r.url, headers=r.headers, params=r.params,
                data=r.data, requestslib_kwargs=r.kwargs)
            if not response:
                sys.stdout.write("STILL NOT GETTING A RESPONSE\n")
        except (requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
                requests.exceptions.TooManyRedirects,
                requests.exceptions.Timeout) as e:
            signal = http_signal.HTTPFailure.from_requests_exception(e)
            if signal:
                signals.append(signal)
        except Exception as e:
            signals.append(syntribos.signal.GenericException.from_exception(e))
        else:
            status_signals = self.check_status_code(response)
            if status_signals:
                signals.extend(status_signals)

        return (response, signals)

    """
    def request(self, method, url, headers=None, params=None, data=None,
                requestslib_kwargs=None):
        sys.stdout.write("NO! NO NO NO NO NO\n")
        r = RequestObject(
            method=method, url=url, headers=headers, params=params, data=data,
            kwargs=requestslib_kwargs)
        return self.send_request(r)
    """

    def check_status_code(self, response):
        """Checks response for HTTP status codes that may indicate issues."""
        signals = []
        codes = http_signal.HTTPStatusCodeSignal.bad_status_codes.keys()
        if str(response.status_code) in codes:
            signal = http_signal.HTTPStatusCodeSignal.from_response_object(
                response)
            if signal:
                sys.stdout.write("WE GOT A SIGNAL!")
                signals.append(signal)
        return signals
