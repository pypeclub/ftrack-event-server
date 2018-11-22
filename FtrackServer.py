import types
import sys
import os
import importlib
import ftrack_api

from app.api import Logger

log = Logger.getLogger(__name__)
"""
# Required - Needed for connection to Ftrack
FTRACK_SERVER # Ftrack server e.g. "https://myFtrack.ftrackapp.com"
FTRACK_API_KEY # Ftrack API key of user e.g. "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
FTRACK_API_USER # Ftrack username e.g. "user.name"

# Required - Paths to folder with actions
FTRACK_ACTIONS_PATH # Paths to folders where are located actions e.g. "M:/FtrackApi/../actions/"
FTRACK_EVENTS_PATH # Paths to folders where are located actions e.g. "M:/FtrackApi/../events/"

# Required - Needed for import included modules
PYTHONPATH # Path to ftrack_api and paths to all modules used in actions e.g. path to ftrack_action_handler
"""

class FtrackServer():
    def __init__(self, type='action'):
        """
            - 'type' is by default set to 'action' - Runs Action server
            - enter 'event' for Event server

            EXAMPLE FOR EVENT SERVER:
                ...
                server = FtrackServer('event')
                server.run_server()
                ...
        """
        self.type = type

        self.actionAvailable = True
        self.eventAvailable = True
        # Separate all paths
        try:
            self.actionsPaths = os.environ["FTRACK_ACTIONS_PATH"].split(os.pathsep)
        except:
            self.actionsAvailable = False
            log.warning("FTRACK_ACTIONS_PATH is not set, action server won't launch")
        try:
            self.eventsPaths = os.environ["FTRACK_EVENTS_PATH"].split(os.pathsep)
        except:
            self.eventsAvailable = False
            log.warning("FTRACK_EVENTS_PATH is not set, event server won't launch")

    def stop_session(self):
        self.session.event_hub.disconnect()
        self.session.close()
        self.session = None

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

    def set_actions(self):
        # Iterate all paths
        for path in self.actionsPaths:
            # add path to PYTHON PATH
            sys.path.append(path)
            # Get all modules with functions
            for m in os.listdir(path):
                # Get only .py files with action functions
                if '.pyc' in m or '.py' not in m:
                    continue
                try:
                    mod = importlib.import_module(os.path.splitext(m)[0])
                    mod_functions = dict([(name, function)
                    for name, function in mod.__dict__.items() if isinstance(
                        function, types.FunctionType)])

                        # Run register on each action
                    mod_functions['register'](self.actionSession)

                except KeyError as e:
                    log.warning("'{0}' - not proper action ({1})".format(m,e))

    def run_server(self):
        self.session = ftrack_api.Session(auto_connect_event_hub=True,)
        if self.type.lower() == 'event':
            self.set_events()
        else:
            self.set_actions()
        # keep event_hub on session running
        self.session.event_hub.wait()
