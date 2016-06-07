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


class SignalHolder(object):

    def __init__(self, signals=None):
        self.signals = []
        self.all_slugs = []

        if signals is not None:
            self.register(signals)

    """BLOCK - CHOP? CONVERT TO GENERATOR?"""

    def __getitem__(self, key):
        return self.signals[key]

    def __setitem__(self, key, value):
        if not isinstance(value, SynSignal):
            raise TypeError

        if value.strength == 0:
            return

        if value.slug not in self.all_slugs:
            self.signals[key] = value
            self.all_slugs[key] = value.slug

    def __delitem__(self, key):
        del self.signals[key]
        # Indices for self.signals/self.all_slugs should be the same
        del self.all_slugs[key]

    """ENDBLOCK"""

    def __repr__(self):
        return self.signals
        # return '["' + '" ,"'.join([sig.slug for sig in self.signals]) + '"]'
        # return "[" + ",".join(self.all_slugs) + "]"

    def __len__(self):
        return len(self.signals)

    def __contains__(self, item):
        if not isinstance(item, SynSignal) and type(item) is not str:
            raise TypeError

        if type(item) is str:
            # We are searching for either a tag or a slug
            for signal in self.signals:
                if signal.matches_slug(item):
                    return True
                if signal.matches_tag(item):
                    return True
            return False
        else:
            # We are searching for a signal by its slug (unique ID)
            return item.slug in self.all_slugs

    def register(self, signals):
        """Add a signal/list of signals to the SignalHolder

        Maintains a set (i.e. won't add duplicate elements)"""
        if signals is None:
            return

        if isinstance(signals, SynSignal) and signals.strength != 0:
            self.signals.append(signals)

        elif type(signals) is list or isinstance(signals, SignalHolder):
            for signal in signals:
                # If strength == 0, this signal was not triggered
                if signal.strength == 0:
                    continue
                if signal.slug in self.all_slugs:
                    continue
                self.signals.append(signal)
                self.all_slugs.append(signal.slug)
        else:
            raise TypeError

    def get_matching_signals(self, slugs=None, tags=None):
        """Get the signals that are matched by `slugs` and/or `tags`"""
        bad_slugs = []
        bad_signals = SignalHolder()

        for signal in self.signals:
            for bad_slug in slugs:
                if signal.matches_slug(bad_slug):
                    bad_signals.append(signal)
                    bad_slugs.append(signal.slug)
            for bad_tag in tags:
                if signal.matches_tag(bad_tag):
                    bad_signals.append(signal)
                    bad_slugs.append(signal.slug)
        return bad_signals


class SynSignal(object):

    signal_type = "GENERIC_SIGNAL"

    def __init__(self, text="", slug="", strength=0, tags=None, data=None):
        self.text = text if text else "Generic signal!"
        self.slug = slug if text else "GENERIC_SIGNAL_NONE"
        if self.__dict__.get("strength", None):
            self.strength = self.strength
        else:
            self.strength = strength
        self.tags = tags if tags else []
        self.data = data if data else {}

    def __repr__(self):
        return self.slug

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


def from_generic_exception(exception):
    if not isinstance(exception, Exception):
        raise Exception("UGH. NOT AN EXCEPTION.")

    text = str(exception)
    data = {
        "exception_name": exception.__class__.__name__,
        "exception_text": str(exception),
        "exception": exception
    }
    slug = "GENERIC_EXCEPTION_{name}".format(data["exception_name"].upper())
    tags = ["EXCEPTION_RAISED"]

    return SynSignal(text=text, slug=slug, strength=1, tags=tags, data=data)
