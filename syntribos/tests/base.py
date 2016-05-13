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
import os
import six
import string as t_string
import sys

import cafe.drivers.unittest.fixtures
from six.moves.urllib.parse import urlparse

import syntribos.signal
from syntribos.clients.http import client, parser


ALLOWED_CHARS = "().-_{0}{1}".format(t_string.ascii_letters, t_string.digits)

"""test_table is the master list of tests to be run by the runner"""
test_table = {}


def replace_invalid_characters(string, new_char="_"):
    """Replace invalid characters in test names

    This function corrects `string` so the following is true.

    Identifiers (also referred to as names) are described by the
    following lexical definitions:

    | ``identifier ::=  (letter|"_") (letter | digit | "_")*``
    | ``letter     ::=  lowercase | uppercase``
    | ``lowercase  ::=  "a"..."z"``
    | ``uppercase  ::=  "A"..."Z"``
    | ``digit      ::=  "0"..."9"``

    :param str string: Test name
    :param str new_char: The character to replace invalid characters with
    :returns: The test name, with invalid characters replaced with `new_char`
    :rtype: str
    """
    if not string:
        return string
    for char in set(string) - set(ALLOWED_CHARS):
        string = string.replace(char, new_char)
    if string[0] in t_string.digits:
        string = string.replace(string[0], new_char, 1)
    return string


class TestType(type):

    """This is the metaclass for each class extending :class:`BaseTestCase`."""

    def __new__(cls, cls_name, cls_parents, cls_attr):
        new_class = super(TestType, cls).__new__(
            cls, cls_name, cls_parents, cls_attr)
        test_name = getattr(new_class, "test_name", None)
        if test_name is not None:
            if test_name not in test_table:
                test_table[test_name] = new_class
        return new_class


@six.add_metaclass(TestType)
class BaseTestCase(cafe.drivers.unittest.fixtures.BaseTestFixture):

    """Base class for building new tests

    :attribute test_name: A name like ``XML_EXTERNAL_ENTITY_BODY``, containing
        the test type and the portion of the request template being tested
    """

    test_name = None
    init_signals = []
    resp_signals = []
    client = client()

    @classmethod
    def get_test_cases(cls, filename, file_content):
        """Returns tests for given TestCase class (overwritten by children)."""
        # CCNEILL: FROM BASE_FUZZ
        # request_obj = syntribos.tests.fuzz.datagen.FuzzParser.create_request(
        #    file_content, os.environ.get("SYNTRIBOS_ENDPOINT"))
        request_obj = parser.create_request(
            file_content, os.environ.get("SYNTRIBOS_ENDPOINT"))
        prepared_copy = request_obj.get_prepared_copy()
        resp, signals = cls.client.send_request(prepared_copy)

        cls.init_response = resp
        cls.init_request = resp.request if resp else prepared_copy
        cls.append_signal(signals, cls.init_signals)

        yield cls

    @classmethod
    def extend_class(cls, new_name, kwargs):
        """Creates an extension for the class

        Each TestCase class created is added to the `test_table`, which is then
        read in by the test runner as the master list of tests to be run.

        :param str new_name: Name of new class to be created
        :param dict kwargs: Keyword arguments to pass to the new class
        :rtype: class
        :returns: A TestCase class extending :class:`BaseTestCase`
        """

        new_name = replace_invalid_characters(new_name)
        if not isinstance(kwargs, dict):
            raise Exception("kwargs must be a dictionary")
        new_cls = type(new_name, (cls, ), kwargs)
        new_cls.__module__ = cls.__module__
        return new_cls

    def run_test(self):
        """This kicks off the test(s) for a given TestCase class

        After running the tests, an `AssertionError` is raised if any tests
        were added to self.failures.

        :raises: :exc:`AssertionError`
        """
        self.test_case()
        if self.failures:
            raise AssertionError

    def test_case(self):
        """This method is overwritten by individual TestCase classes

        It represents the actual test that is called in :func:`run_test`,
        and handles populating `self.failures`
        """
        pass

    def register_issue(self, issue):
        """Adds an issue to the test's list of issues

        Registers a :class:`syntribos.issue.Issue` object as a failure and
        associates the test's metadata to it.

        :param issue: issue object to update
        :type issue: :class:`syntribos.issue.Issue`
        :returns: new issue object with metadata associated
        :rtype: :class:`syntribos.issue.Issue`
        """

        # Still associating request and response objects with issue in event of
        # debug log
        req = self.resp.request
        issue.request = req
        issue.response = self.resp

        issue.defect_type = self.test_name
        url_components = urlparse(self.resp.request.url)
        issue.target = url_components.netloc
        issue.path = url_components.path
        if self.test_type:
            issue.test_type = self.test_type

        self.failures.append(issue)

        return issue

    @classmethod
    def append_signal(cls, signals, bucket):
        if type(bucket) is not list:
            raise Exception("NEED A LIST")
        if type(signals) is list:
            for s in signals:
                if type(s) is list:
                    for s2 in s:
                        if s2:
                            sys.stdout.write(s2.text)
                            bucket.append(s2)
        elif isinstance(signals, syntribos.signal):
            sys.stdout.write(signals.text)
            bucket.append(signals)
        elif type(signals) is str:
            sys.stdout.write("Stupid string. Stupid stupid stupid.\n")
            sys.stdout.write(signals + "\n")
        else:
            sys.stdout.write("WUT\n" + str(type(signals)))

    def register_issue_from_signals(self, issue, bad_signals):
        """Register an issue, using a list of bad signals"""
        issue.signals = bad_signals
        issue.text += "\n\nReasons for suspicion:\n"
        for signal in bad_signals:
            issue.text += signal.text + "\n"
            # CCNEILL: MAGIC
            issue.confidence += signal.strength * signal["points"]
        issue.text = issue.text.strip()

        # CCNEILL: CONVERT FLOATS TO STRINGS
        if issue.confidence >= 10:
            issue.confidence = "High"
        elif issue.confidence >= 5:
            issue.confidence = "Medium"
        elif issue.confidence >= 0:
            issue.confidence = "Low"
        else:
            issue.confidence = "None"

        self.register_issue(issue)
