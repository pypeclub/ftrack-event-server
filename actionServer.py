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

# Required - Needed for import included modules
PYTHONPATH # Path to ftrack_api and paths to all modules used in actions e.g. path to ftrack_action_handler
"""

class FtrackActionServer():
    def __init__(self):
        # Separate all paths
        self.actionsPaths = os.environ["FTRACK_ACTIONS_PATH"].split(os.pathsep)

    def stop_action_session(self):
        self.actionSession.event_hub.disconnect()
        self.actionSession.close()
        self.actionSession = None

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

    def run_action_server(self):
        self.actionSession = ftrack_api.Session(auto_connect_event_hub=True,)
        self.set_actions()
        # keep event_hub on session running
        self.actionSession.event_hub.wait()
