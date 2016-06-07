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
import syntribos.signal
import syntribos.tests.fuzz.config

config = syntribos.tests.fuzz.config.BaseFuzzConfig()


def percentage_difference(resp1, resp2):
    """Validates time taken for two responses

    Compares the elapsed time of a fuzzed response with a response to the
    baseline request. If the response takes longer than expected, returns
    a `TimePercentageDiffSignal`

    :returns: LengthPercentageDiffSignal
    """
    data = {
        "req1": resp1.request,
        "req2": resp2.request,
        "resp1": resp1,
        "resp2": resp2,
        "resp1_time": resp1.elapsed.total_seconds(),
        "resp2_time": resp2.elapsed.total_seconds()
    }
    data["time_diff"] = data["resp2_time"] - data["resp1_time"]
    # CCNEILL: This is hacky. Exact match != 100% (due to +1)
    data["percent_diff"] = abs(
        float(data["time_diff"]) / (data["resp1_time"] + 1)) * 100
    data["dir"] = "UNDER" if data["resp1_time"] > data["resp2_time"] else "OVER"

    if data["percent_diff"] < config.time_difference_percent:
        # Difference not larger than configured percentage
        return None
    return TimePercentageDiffSignal.from_data_obj(data)


def absolute_time(resp):
    """Checks response takes less than `config.max_time` seconds"""
    if resp.elapsed.total_seconds() > config.absolute_time:
        data = {
            "request": resp.request,
            "response": resp,
            "elapsed": resp.elapsed.total_seconds(),
            "max_time": config.absolute_time
        }
        return TimeAbsoluteSignal.from_data_obj(data)
    return None


class TimePercentageDiffSignal(syntribos.signal.SynSignal):

    signal_type = "TIME_DIFF"

    @classmethod
    def from_data_obj(cls, data):
        text = (
            "Validate Time Differential:\n"
            "\tResponse 1 elapsed time: {0}\n"
            "\tResponse 2 elapsed time: {1}\n"
            "\tResponse difference: {2}\n"
            "\tPercent difference: {3}%\n"
            "\tDifference direction: {4}"
            "\tConfig percent: {5}\n").format(
            data["resp1_time"], data["resp2_time"], data["time_diff"],
            data["percent_diff"], data["dir"], config.percent)

        slug = "{type}_{dir}".format(type=cls.signal_type, dir=data["dir"])

        return cls(text=text, slug=slug, strength=1, data=data)


class TimeAbsoluteSignal(syntribos.signal.SynSignal):

    signal_type = "TIME_ABSOLUTE"

    @classmethod
    def from_data_obj(cls, data):
        text = (
            "Check that response time doesn't exceed config.max_time:\n"
            "\tMax time: {0}\n"
            "\tElapsed time: {1}\n").format(data["elapsed"], data["max_time"])
        slug = "{type}_{max}".format(type=cls.type, max=data["max_time"])
        tags = ["CONNECTION_TIMEOUT"]
        return cls(text=text, slug=slug, strength=1, tags=tags, data=data)
