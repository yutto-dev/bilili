class Downloader:
    def __init__(self, files, overwrite=False, num_threads=16, use_mirrors=False):
        self.files = files
        self.overwrite = overwrite
        self.num_threads = num_threads
        self.use_mirrors = use_mirrors

    def boot(self):
        for leaf in self.files.leaves:
            leaf.process()

    def check_status(self):
        if self.overwrite
