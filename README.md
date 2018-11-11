**Goal**

To ease the usage of Ftracks Actions and events.

**Motivation**

Currently you can write event plugins, and run them individually, which can be difficult to manage.
Along with having to manage the execution of each plugin, feedback are scattering over multiple terminals.

**Usage**

You can write the event plugins exactly how Ftrack documents you to do; http://ftrack-python-api.rtd.ftrack.com/en/latest/handling_events.html

You can test your plugin by just running it individually. When you have collect two or more plugins that you want to run at the same time you can put them in folder. It's neccessary to have separate folders for actions and events!

##EVENTS
- Event should be '.py' file with one method for one event

##ACTIONS
- Action should be '.py' file including action class and method "register" that requires 'session'
```
class MyAction():
  ...
  ...
  def __init__(self, session):
    self.session = session
  ...
  ...
  def register(self):
        self.session.event_hub.subscribe('topic=ftrack.action.discover', self._discover)
        self.session.event_hub.subscribe('topic=ftrack.action.launch and data.actionIdentifier={0}'.format(
                self.identifier), self.launch)
  ...
  ...

def register(session):
  action = MyAction(session)
  action.register()

```
## REQUIRED Environment variables
# Needed for connection to Ftrack
*FTRACK_SERVER*   - Ftrack server           - e.g. https://myFtrack.ftrackapp.com
*FTRACK_API_KEY*  - Ftrack API key of user  - e.g. xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
*FTRACK_API_USER* - Ftrack username         - e.g. user.name

# Paths to folder with actions/events
*FTRACK_ACTIONS_PATH* - Folder paths to actions - e.g. "M:/FtrackApi/../actions/"
*FTRACK_EVENTS_PATH*  - Folder paths to events  - e.g. "M:/FtrackApi/../events/"
- It's possible to have multiple folder paths for both variables
  e.g. in win CMD: set FTRACK_ACTIONS_PATH=M:\FtrackApi\actions;N:\actions
  Server will iterate through all files in the folder open '.py' files and register actions/events
