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
import requests

import syntribos.signal


def check_http_fail(exception):
    if not isinstance(exception, requests.exceptions.RequestException):
        return syntribos.signal.from_generic_exception(exception)

    data = {
        "response": exception.response,
        "request": exception.request,
        "exception": exception,
        "exception_name": exception.__class__.__name__
    }
    text = "An exception was encountered when sending the request. "
    slug = "HTTP_FAIL_{exc}".format(exc=data["exception_name"].upper())
    tags = ["EXCEPTION_RAISED"]

    if isinstance(exception, requests.exceptions.ConnectionError):
        text += "Error connecting to server."
        tags.append("CONNECTION_FAIL")
    elif isinstance(exception, requests.exceptions.HTTPError):
        text += "An HTTP error occurred."
        tags.append("CONNECTION_FAIL")
    elif isinstance(exception, requests.exceptions.TooManyRedirects):
        text += "Server responded with too many redirects."
        tags.append("SERVER_FAIL")
    elif isinstance(exception, requests.exceptions.Timeout):
        text += "Request timed out."
        tags.append("CONNECTION_TIMEOUT")

    return syntribos.signal.SynSignal(
        text=text, slug=slug, strength=1, tags=tags, data=data)


def check_http_status_code(response):

    codes = {
        "413": "the server rejected the request due to its body size",
        "414": "the server rejected the request due to its URL length",
        "429": "the server is rate limiting your requests",
        "500": "the server encountered an unknown error",
        "501": "the server doesn't implement this method or endpoint",
        "502": "the application server is down",
        "503": "the application server is down",
        "504": "the application server is down"
    }

    data = {
        "response": response,
        "request": response.request,
        "status_code": response.status_code,
        "reason": response.reason,
    }
    if codes.get(str(response.status_code), None):
        data["details"] = codes[str(response.status_code)]
    else:
        data["details"] = "the request was rejected for an unknown reason"

    text = (
        "A {code} HTTP status code was returned by the server, with reason"
        " '{reason}'. This typically indicates that {details}.").format(
        code=data["status_code"], reason=data["reason"],
        details=data["details"])

    slug = "HTTP_STATUS_CODE_{range}"
    tags = []

    if data["status_code"] in range(200, 300):
        slug = slug.format(range="2XX")

    elif data["status_code"] in range(300, 400):
        slug = slug.format(range="3XX")

        # CCNEILL: 304 == use local cache; not really a redirect
        if data["status_code"] != 304:
            tags.append("SERVER_REDIRECT")

    elif data["status_code"] in range(400, 500):
        slug = slug.format(range="4XX")
        tags.append("CLIENT_FAIL")

    elif data["status_code"] in range(500, 600):
        slug = slug.format(range="5XX")
        tags.append("SERVER_FAIL")

    slug = (slug + "_{code}").format(code=data["status_code"])

    return syntribos.signal.SynSignal(
        text=text, slug=slug, strength=1, tags=tags, data=data)
