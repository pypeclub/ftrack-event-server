import types
import sys
import os
import importlib
import ftrack_api

"""
# Required - Path to folder with events
os.environ['FTRACK_EVENTS_PATH'] = "" # Path to folder where are located events e.g. "M:/FtrackApi/../events/"

# Required - Needed for connection to Ftrack
os.environ['FTRACK_SERVER'] = "" # Ftrack server e.g. "https://myFtrack.ftrackapp.com"
os.environ['FTRACK_API_KEY'] = "" # Ftrack API key of user e.g. "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
os.environ['FTRACK_API_USER'] = "" # Ftrack username e.g. "user.name"

# Required - Needed for modules included in events
os.environ['PYTHONPATH ']="" # PYTHONPATH needs path to all modules (also modules used in events) e.g. path to ftrack_api module
"""

def run_server():
    # Separate all paths
    eventsPaths = os.environ["FTRACK_EVENTS_PATH"].split(os.pathsep)

    # Create session to Ftrack ( auto_connect_event_hub - multitask
    session = ftrack_api.Session(auto_connect_event_hub=True,)

    # Iterate all paths
    for path in eventsPaths:
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
                session.event_hub.subscribe('topic=ftrack.update',allEventFunctions[f])


    # Keep event_hub on session running
    session.event_hub.wait()


if __name__ == '__main__':
    run_server()
