import types
import sys
import os
import importlib
import toml
import ftrack_api

from app.api import Logger

log = Logger.getLogger(__name__)

"""
# Required - Needed for connection to Ftrack
FTRACK_SERVER # Ftrack server e.g. "https://myFtrack.ftrackapp.com" FTRACK_API_KEY # Ftrack API key of user e.g. "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
FTRACK_API_USER # Ftrack username e.g. "user.name"

# Required - Paths to folder with events
FTRACK_EVENTS_PATH # Paths to folders where are located actions e.g. "M:/FtrackApi/../events/"

# Required - Needed for import included modules
PYTHONPATH # Path to ftrack_api and paths to all modules used in actions e.g. path to ftrack_action_handler
"""

class FtrackEventServer():
    def __init__(self):
        # Separate all paths
        self.eventsPaths = os.environ["FTRACK_EVENTS_PATH"].split(os.pathsep)

    def set_events(self):
        # Create session to Ftrack ( auto_connect_event_hub - multitask
        self.eventSession = ftrack_api.Session(auto_connect_event_hub=True,)

        # Iterate all paths
        for path in self.eventsPaths:
            # add path to PYTHON PATH
            sys.path.append(path)
            # Get all modules with functions
            for m in os.listdir(path):
                # Get only .py files
                if '.pyc' in m or '.py' not in m:
                    continue
                mod = importlib.import_module(os.path.splitext(m)[0])
                allEventFunctions = dict([(name, function)
                                          for name, function in mod.__dict__.items() if isinstance(function, types.FunctionType)])

                # Register all events
                for f in allEventFunctions:
                    self.eventSession.event_hub.subscribe('topic=ftrack.update', allEventFunctions[f])

    def stop_event_session(self):
        self.eventSession.event_hub.disconnect()
        self.eventSession.close()
        self.eventSession = None

    def run_event_server(self):
        self.eventSession = ftrack_api.Session(auto_connect_event_hub=True,)
        self.set_events()
        # keep event_hub on session running
        self.eventSession.event_hub.wait()
