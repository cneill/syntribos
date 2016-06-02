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


class HTTPSignal(syntribos.signal.SynSignal):

    request = None
    response = None

    def __init__(self, text="", slug="", strength=0, tags=None, data=None):
        super(HTTPSignal, self).__init__(
            text=text, slug=slug, strength=strength, tags=tags, data=data)

        self.request = data.get("request", None)
        self.response = data.get("response", None)


class HTTPStatusCodeSignal(HTTPSignal):

    bad_status_codes = {
        "413": "the server rejected the request due to its body size",
        "414": "the server rejected the request due to its URL length",
        "429": "the server is rate limiting your requests",
        "500": "the server encountered an unknown error",
        "501": "the server doesn't implement this method or endpoint",
        "502": "the application server is down",
        "503": "the application server is down",
        "504": "the application server is down"}

    signal_type = "HTTP_STATUS_CODE"

    @classmethod
    def from_response_object(cls, response):
        if response is None:
            return None
        if str(response.status_code) not in cls.bad_status_codes.keys():
            return None

        text = (
            "A {code} HTTP status code was returned by the server, with reason"
            " '{reason}'. This typically indicates that {details}.").format(
            code=response.status_code, reason=response.reason,
            details=cls.bad_status_codes[str(response.status_code)])

        slug = cls.slug_from_status_code(response.status_code)
        tags = cls.tags_from_status_code(response.status_code)
        data = {"request": response.request, "response": response}

        return cls(text=text, slug=slug, strength=1, tags=tags, data=data)

    @classmethod
    def slug_from_status_code(cls, status_code):
        """Return a slug based on the response HTTP Status code"""
        status_code = int(status_code)
        if status_code in range(400, 500):
            generic = "4XX"
        elif status_code in range(500, 600):
            generic = "5XX"
        slug = "{type}_{generic}_{status_code}".format(
            type=cls.signal_type, generic=generic, status_code=status_code)
        return slug

    @classmethod
    def tags_from_status_code(cls, status_code):
        """Return tags based on the response HTTP status code"""
        status_code = int(status_code)
        tags = []
        if status_code in range(400, 500):
            tags.append("CLIENT_FAIL")
        elif status_code in range(500, 600):
            tags.append("SERVER_FAIL")
        return tags

    @classmethod
    def get_slugs(cls):
        """Return all possible slugs for this signal"""
        slugs = []
        for code in cls.bad_status_codes.keys():
            slugs.append(cls.slug_from_status_code(code))
        return slugs

    @classmethod
    def get_tags(cls):
        """Return all possible tags for this signal"""
        tags = []
        for code in cls.bad_status_codes.keys():
            temp_tags = cls.tags_from_status_code(code)
            if type(temp_tags) is list:
                for t in temp_tags:
                    tags.append(t)
            elif type(temp_tags) is str:
                tags.append(temp_tags)
        return list(set(tags))


class HTTPFailureSignal(HTTPSignal):

    rex = requests.exceptions
    exceptions = [
        rex.ConnectionError, rex.HTTPError, rex.TooManyRedirects, rex.Timeout]
    signal_type = "HTTP_FAILURE"

    @classmethod
    def from_requests_exception(cls, exception):
        if not isinstance(exception, requests.RequestException):
            return None

        text = "an HTTP error was encountered"
        response = exception.__dict__.get("response", None)
        request = exception.__dict__.get("request", None)
        tags = []

        if isinstance(exception, requests.exceptions.ConnectionError):
            text = "Error connecting to server!"
            tags.append("CONNECTION_FAIL")
        elif isinstance(exception, requests.exceptions.HTTPError):
            text = "An HTTP error occurred?"
            tags.append("CONNECTION_FAIL")
        elif isinstance(exception, requests.exceptions.TooManyRedirects):
            text = "Redirect loop!"
            tags.append("SERVER_FAIL")
        elif isinstance(exception, requests.exceptions.Timeout):
            text = "Request timed out!"
            tags.append("CONNECTION_TIMEOUT")

        slug = "{type}_{exception}".format(
            type=cls.signal_type,
            exception=exception.__class__.__name__.upper())

        data = {"request": request, "response": response}

        return cls(text=text, slug=slug, strength=1, tags=tags, data=data)

    @classmethod
    def is_covered_exception(cls, exception):
        found = False
        for exc in cls.exceptions:
            if isinstance(exception, exc):
                found = True
                break
        return found

    @classmethod
    def slug_from_exception(cls, exception):
        # HANDLE EXCEPTION TYPES
        if type(exception) is type:
            module = exception.__module__
            name = module + "." + exception.__name__

        # HANDLE EXCEPTION INSTANCES
        elif isinstance(exception, Exception):
            name = exception.__class__.__name__

        # UNKNOWN EXCEPTION
        else:
            raise AttributeError("Unknown exception: " + exception)

        return "{type}_{name}".format(cls.signal_type, name.upper())

    @classmethod
    def get_slugs(cls):
        slugs = []
        for exc in cls.exceptions:
            slugs.append(cls.slug_from_exception(exc))
        return slugs

    @classmethod
    def get_tags(cls):
        return ["CONNECTION_FAIL", "TIMEOUT"]
