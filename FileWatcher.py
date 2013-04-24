from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os


class MyEventHandler(FileSystemEventHandler):

    def __init__(self, filePath, callback):
        super(MyEventHandler, self).__init__()
        self.filePath = filePath
        self.callback = callback

    def on_modified(self, event):
        if os.path.normpath(event.src_path) == self.filePath:
            self.callback()

class LibraryFileWatcher(object):
    def __init__(self, filePath, callback):
        super(LibraryFileWatcher, self).__init__()
        self.filePath = os.path.normpath(filePath)
        self.callback = callback
        self.eventHandler = MyEventHandler(self.filePath, callback)
        self.resume()

    def __del__(self):
        self.observer.stop()
        self.observer.join()

    def pause(self):
        self.observer.stop()

    def resume(self):
        self.observer = Observer()
        self.watch = self.observer.schedule(self.eventHandler, path=os.path.dirname(self.filePath))
        self.observer.start()