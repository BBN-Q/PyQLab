from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os


class MyEventHandler(FileSystemEventHandler):

    def __init__(self, filePath, callback):
        super(MyEventHandler, self).__init__()
        self.filePath = filePath
        self.callback = callback

    def on_modified(self, event):
        if event.src_path == self.filePath:
            self.callback()

class LibraryFileWatcher(object):
    def __init__(self, filePath, callback):
        super(LibraryFileWatcher, self).__init__()
        self.filePath = filePath
        self.callback = callback
        self.eventHandler = MyEventHandler(filePath, callback)
        self.resume()

    def __del__(self):
        self.observer.stop()
        self.observer.join()

    def pause(self):
        self.observer.stop()

    def resume(self):
        self.observer = Observer(timeout=0.001)
        self.watch = self.observer.schedule(self.eventHandler, path=os.path.dirname(self.filePath))
        self.observer.start()