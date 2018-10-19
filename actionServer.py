import types
import sys
import os
import importlib
import ftrack_api

"""
# Required - Path to folder with actions
os.environ['FTRACK_ACTIONS_PATH'] = "" # Paths to folders where are located actions e.g. "M:/FtrackApi/../actions/"

# Required - Needed for connection to Ftrack
os.environ['FTRACK_SERVER'] = "" # Ftrack server e.g. "https://myFtrack.ftrackapp.com"
os.environ['FTRACK_API_KEY'] = "" # Ftrack API key of user e.g. "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
os.environ['FTRACK_API_USER'] = "" # Ftrack username e.g. "user.name"

# Required - needed if not already set
os.environ['AVALON_PROJECTS']="temp"    #  \
os.environ['AVALON_ASSET']="temp"       #  }    Avalon need to set these env variables to any value.
os.environ['AVALON_SILO']="temp"        # /

# Required - Needed for modules included in actions
os.environ['PYTHONPATH ']="" # PYTHONPATH needs path to all modules (also modules used in actions) e.g. path to ftrack_api module
"""

def run_server():
    # Separate all paths
    actionsPaths = os.environ["FTRACK_ACTIONS_PATH"].split(os.pathsep)

    # Create session to Ftrack
    session = ftrack_api.Session(auto_connect_event_hub=True,)

    # Iterate all paths
    for path in actionsPaths:
        # add path to PYTHON PATH
        sys.path.append(path)
        # Get all modules with functions
        for m in os.listdir(path):
            # Get only .py files with action functions
            if '.pyc' in m or '.py' not in m:
                continue
            mod = importlib.import_module(os.path.splitext(m)[0])
            mod_functions = dict([(name, function)
                for name, function in mod.__dict__.items() if isinstance(function, types.FunctionType)])

            # Run register on each action
            mod_functions['register'](session)


    # keep event_hub on session running
    session.event_hub.wait()


if __name__ == '__main__':
    run_server()
