# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests


class Downloader:
    def __init__(self, source_urls):
        self.source_urls = source_urls

    @staticmethod
    def _make_key(debug_filename, debug_id, filename):
        # ex: libmozglue.dylib 11FB836EE6723C07BFF775900077457B0 libmozglue.dylib.sym
        return "%s/%s/%s" % (debug_filename, debug_id, filename)

    def get(self, debug_filename, debug_id, filename):
        for source_url in self.source_urls:
            key = self._make_key(debug_filename, debug_id, filename)
            url = "%s/%s" % (source_url, key)

            resp = requests.get(url)
            if resp.status_code != 200:
                continue

            return resp.content
