import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os
from GetAPInfo import GetBSSIDs


def on_created(event):
    print(GetBSSIDs(os.path.abspath(event.src_path)))


def on_deleted(event):
    print(f"{event.src_path} has been deleted!")


def on_modified(event):
    print(GetBSSIDs(os.path.abspath(event.src_path)))


def on_moved(event):
    print(f"{event.src_path} has been moved to {event.dest_path}")


if __name__ == "__main__":
    patterns = ["*"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(
        patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved

    path = "./logs"  # Move to config file
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
