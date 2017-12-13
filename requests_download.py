"""Download files using requests and save them to a target path

Usage example::

    import hashlib
    # progressbar is provided by progressbar2 on PYPI.
    from progressbar import DataTransferBar
    from requests_download import download, HashTracker, ProgressTracker

    hasher = HashTracker(hashlib.sha256())
    progress = ProgressTracker(DataTransferBar())

    download('https://github.com/takluyver/requests_download/archive/master.zip',
             'requests_download.zip', trackers=(hasher, progress))

    assert hasher.hashobj.hexdigest() == '...'

"""

import requests

__version__ = '0.1.2'

class TrackerBase(object):
    def on_start(self, response):
        pass

    def on_chunk(self, chunk):
        pass

    def on_finish(self):
        pass

class ProgressTracker(TrackerBase):
    def __init__(self, progressbar):
        self.progressbar = progressbar
        self.recvd = 0

    def on_start(self, response):
        max_value = None
        if 'content-length' in response.headers:
            max_value = int(response.headers['content-length'])
        self.progressbar.start(max_value=max_value)
        self.recvd = 0

    def on_chunk(self, chunk):
        self.recvd += len(chunk)
        try:
            self.progressbar.update(self.recvd)
        except ValueError:
            # Probably the HTTP headers lied.
            pass

    def on_finish(self):
        self.progressbar.finish()


class HashTracker(TrackerBase):
    def __init__(self, hashobj):
        self.hashobj = hashobj

    def on_chunk(self, chunk):
        self.hashobj.update(chunk)

def download(url, target, headers=None, trackers=()):
    """Download a file using requests.

    This is like urllib.request.urlretrieve, but:

    - requests validates SSL certificates by default
    - you can pass tracker objects to e.g. display a progress bar or calculate
      a file hash.
    """
    if headers is None:
        headers = {}
    headers.setdefault('user-agent', 'requests_download/'+__version__)
    r = requests.get(url, headers=headers, stream=True)
    r.raise_for_status()
    for t in trackers:
        t.on_start(r)


    with open(target, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                for t in trackers:
                    t.on_chunk(chunk)

    for t in trackers:
        t.on_finish()
