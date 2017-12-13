A convenient function to download to a file using requests.

Basic usage:

.. code-block:: python

    url = "https://github.com/takluyver/requests_download/archive/master.zip"
    download(url, "requests_download.zip")

An optional ``headers=`` parameter is passed through to requests.

**Trackers** are a lightweight way to monitor the data being downloaded.
Two trackers are included:

- ``ProgressTracker`` - displays a progress bar, using the `progressbar2
  <https://pypi.python.org/pypi/progressbar2>`_ package.
- ``HashTracker`` - wraps a hashlib object to calculate a hash (e.g. sha256 or
  md5) of the file as you download it.

Here's an example of using both of them:

.. code-block:: python

    import hashlib
    # progressbar is provided by progressbar2 on PYPI.
    from progressbar import DataTransferBar
    from requests_download import download, HashTracker, ProgressTracker

    hasher = HashTracker(hashlib.sha256())
    progress = ProgressTracker(DataTransferBar())

    download('https://github.com/takluyver/requests_download/archive/master.zip',
             'requests_download.zip', trackers=(hasher, progress))

    assert hasher.hashobj.hexdigest() == '...'

To make your own tracker, subclass TrackerBase and define any of these methods:

.. code-block:: python

    from requests_download import TrackerBase

    class MyTracker(TrackerBase):
        def on_start(self, response):
            """Called with requests.Response object, which has response headers"""
            pass

        def on_chunk(self, chunk):
            """Called multiple times, with bytestrings of data received"""
            pass

        def on_finish(self):
            """Called when the download has completed"""
            pass
