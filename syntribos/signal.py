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


class Signal(object):

    def __init__(self, *args, **kwargs):
        self.text = kwargs.pop("text", "")
        self.signal_type = kwargs.pop("signal_type", "")
        self.slug = kwargs.pop("slug", "")
        self.data = kwargs.pop("data", None)
        self.strength = kwargs.pop("strength", 0.0)
        self.tags = kwargs.pop("tags", [])

        if not self.tags:
            self.tags = []

    def __repr__(self):
        return float(self.strength)
        # return "[{0}]: {1}".format(self.slug, self.text)

    def __str__(self):
        return "[{0}]: {1}".format(self.slug, self.text)

    @classmethod
    def get_slugs(cls):
        """Return all slugs that might be used by this signal"""
        pass

    @classmethod
    def get_tags(cls):
        """Return all tags that might be used by this signal"""
        pass

    def matches_tag(self, tag):
        """Checks if a Signal has a given tag"""
        for t in self.tags:
            if tag in t:
                return True
        return False

    def matches_slug(self, slug):
        """Checks if a Signal has the given slug"""
        slug = str(slug).upper()
        if slug in self.slug:
            return True
        return False

    def get_highest_match(self, bad_tags=None, bad_slugs=None):
        """Return the slug or tag that gives the most points."""
        if type(bad_tags) != list or type(bad_slugs) != list:
            raise Exception("Must supply lists")

        match = None

        for bad_slug in bad_slugs:
            if bad_slug["slug"] in self.slug:
                sys.stdout.write(bad_slug["slug"])
                if not match or bad_slug["points"] > match["points"]:
                    match = bad_slug

        for bad_tag in bad_tags:
            for tag in self.tags:
                if bad_tag["tag"] in tag:
                    if not match or bad_tag["points"] > match["points"]:
                        match = bad_slug

        return match


class GenericException(Signal):

    signal_type = "GENERIC_EXCEPTION"
    strength = 1

    @classmethod
    def from_exception(cls, exception):
        slug = "{type}_{name}".format(
            cls.signal_type, exception.__class__.__name__)
        return cls(text=str(exception), slug=slug)
