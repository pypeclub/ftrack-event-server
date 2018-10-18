import types
import sys
import os
import importlib
import ftrack_api


def run_server():
    path_to_events_folder = os.path.join(
        os.path.dirname(__file__), 'server_events')

    # add to python path
    sys.path.append(path_to_events_folder)

    session = ftrack_api.Session()

    # iterate all available event scripts
    for m in os.listdir(path_to_events_folder):
        if '.pyc' in m:
            continue
        mod = importlib.import_module(os.path.splitext(m)[0])
        all_functions = dict([(name, function)
                              for name, function in mod.__dict__.items()
                              if isinstance(function, types.FunctionType)])
        for f in all_functions:
            session.event_hub.subscribe('topic=ftrack.update',
                                        all_functions[f])

    # keep event_hub on session running
    session.event_hub.wait()


if __name__ == '__main__':
    run_server()
