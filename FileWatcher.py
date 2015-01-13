import sys

# FSEvents observer in watchdog cannot have multiple watchers of the same path
# use kqueue instead
if sys.platform == 'darwin':
    from watchdog.observers.kqueue import KqueueObserver as Observer
else:
    from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time


class MyEventHandler(FileSystemEventHandler):

    def __init__(self, filePath, callback):
        super(MyEventHandler, self).__init__()
        self.filePath = filePath
        self.callback = callback
        self.paused = True

    def on_modified(self, event):
        if os.path.normpath(event.src_path) == self.filePath:
            if not self.paused:
                """
                Hold off for half a second
                If the event is from the file being opened to be written this gives
                time for it to be written.
                """
                time.sleep(0.5)
                self.callback()

class LibraryFileWatcher(object):
    def __init__(self, filePath, callback):
        super(LibraryFileWatcher, self).__init__()
        self.filePath = os.path.normpath(filePath)
        self.callback = callback
        self.eventHandler = MyEventHandler(self.filePath, callback)
        self.observer = Observer()
        self.watch = self.observer.schedule(self.eventHandler, path=os.path.dirname(self.filePath))
        self.observer.start()
        self.resume()

    def __del__(self):
        self.observer.stop()
        self.observer.join()

    def pause(self):
        self.eventHandler.paused = True

    def resume(self):
        self.eventHandler.paused = False