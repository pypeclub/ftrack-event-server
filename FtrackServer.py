import os
import sys
import types
import importlib
import ftrack_api
import time
import logging
from app.api import Logger

log = Logger.getLogger(__name__)

"""
# Required - Needed for connection to Ftrack
FTRACK_SERVER # Ftrack server e.g. "https://myFtrack.ftrackapp.com"
FTRACK_API_KEY # Ftrack user's API key "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
FTRACK_API_USER # Ftrack username e.g. "user.name"

# Required - Paths to folder with actions
FTRACK_ACTIONS_PATH # Paths to folders where are located actions
    - EXAMPLE: "M:/FtrackApi/../actions/"
FTRACK_EVENTS_PATH # Paths to folders where are located actions
    - EXAMPLE: "M:/FtrackApi/../events/"

# Required - Needed for import included modules
PYTHONPATH # Path to ftrack_api and paths to all modules used in actions
    - path to ftrack_action_handler, etc.
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
        # set Ftrack logging to Warning only - OPTIONAL
        ftrack_log = Logger.getLogger("ftrack_api")
        ftrack_log.setLevel(logging.WARNING)

        self.type = type
        self.actionsAvailable = True
        self.eventsAvailable = True
        # Separate all paths
        if "FTRACK_ACTIONS_PATH" in os.environ:
            all_action_paths = os.environ["FTRACK_ACTIONS_PATH"]
            self.actionsPaths = all_action_paths.split(os.pathsep)
        else:
            self.actionsAvailable = False

        if "FTRACK_EVENTS_PATH" in os.environ:
            all_event_paths = os.environ["FTRACK_EVENTS_PATH"]
            self.eventsPaths = all_event_paths.split(os.pathsep)
        else:
            self.eventsAvailable = False

    def stop_session(self):
        if self.session.event_hub.connected is True:
            self.session.event_hub.disconnect()
        self.session.close()
        self.session = None

    def set_files(self, paths):
        # Iterate all paths
        functions = []
        for path in paths:
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
                    mod_functions['register'](self.session)

                except KeyError as e:
                    log.warning("'{0}' - not proper {1} (Missing register method)".format(m, self.type))
                except Exception as e:
                    log.warning("'{0}' - not proper {1} ({2})".format(m, self.type, e))

    def run_server(self):
        self.session = ftrack_api.Session(auto_connect_event_hub=True,)

        if self.type.lower() == 'event':
            if self.eventsAvailable is False:
                msg = (
                    'FTRACK_EVENTS_PATH is not set'
                    ', event server won\'t launch'
                )
                log.error(msg)
                return
            self.set_files(self.eventsPaths)
        else:
            if self.actionsAvailable is False:
                msg = (
                    'FTRACK_ACTIONS_PATH is not set'
                    ', action server won\'t launch'
                )
                log.error(msg)
                return
            self.set_files(self.actionsPaths)
        log.info(60*"*")
        log.info('Registration of actions/events has finished!')
        # keep event_hub on session running
        self.session.event_hub.wait()
