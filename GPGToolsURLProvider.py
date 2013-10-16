#!/usr/bin/env python
#
# Copyright 2010 Per Olofsson, 2013 Greg Neagle, 2013 Jeremy Leggat
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re
import urllib2
import urlparse
from urllib import unquote, quote
from autopkglib import Processor, ProcessorError


__all__ = ["GPGToolsURLProvider"]


GPG_BASE_URL = "https://gpgtools.org"
re_dmg = re.compile(r'a[^>]* href="(?P<filename>[^"]+\.dmg)"')


class GPGToolsURLProvider(Processor):
    description = "Provides URL to the latest GPGSuite release."
    input_variables = {
        "base_url": {
            "required": False,
            "description": "Default is '%s." % GPG_BASE_URL,
        },
        "download_page": {
            "required": False,
            "description":
                    "page to find download on, default is 'index.html'.",
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest GPGTools product release.",
        },
    }

    __doc__ = description

    def get_GPGTools_dmg_url(self, base_url, download_page):

        index_url = "/".join((base_url, download_page))
        #print >>sys.stderr, index_url

        # Read HTML index.
        try:
            f = urllib2.urlopen(index_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't parse download from %s: %s" % (index_url, e))

        # Search for download link.
        m = re_dmg.search(html)
        if not m:
            raise ProcessorError(
                "Couldn't finddownload URL in %s"
                % (index_url))


        url = unquote(m.group("filename"))
        print "The scanned URL is: ", url
        parse_object = urlparse(url)
        dmg_path = parse_object.path
        print "The file path is: ", dmg_path
        # Create the Request.
        request = urllib2.Request(url)
        # Add your headers
        request.add_header('User-agent', 'Mozilla 5.10')
        # Read real url.
        try:
            # Getting the response
            response = urllib2.urlopen(request)
            print "Response:", response
            # Get the URL. This gets the real URL.
            real_url = response.geturl()
            response.close()
        except BaseException as e:
            raise ProcessorError("Can't read from %s: %s" % (url, e))

        print "The URL is: ", real_url

        # Return URL.
        return real_url

    def main(self):
        # Determine download_page and base_url.
        download_page = self.env.get("download_page", "index.html")
        base_url = self.env.get("base_url", GPG_BASE_URL)

        self.env["url"] = self.get_GPGTools_dmg_url(base_url, download_page)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = GPGToolsURLProvider()
    processor.execute_shell()
