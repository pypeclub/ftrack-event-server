from unidecode import unidecode


def print_entity_head(entity, session):
    ''' this is a utility script for printing edentifying information of the
    the processed event'''

    task = session.get('Task', entity['entityId'])
    user = session.query(
        'select first_name, last_name from User where assignments any (context_id = "{0}")'.
        format(task['id'])).first()
    project = session.get('Project', task['project_id'])
    status = session.get('Status', entity['changes']['statusid']['new'])
    # encode diacritic
    user['first_name'] = unidecode(user['first_name'])
    user['last_name'] = unidecode(user['last_name'])
    project['name'] = unidecode(project['name'])

    print 'Name: {} {}'.format(user['first_name'], user['last_name'])
    print 'Task: {}  id: {}  status: {}'.format(task['name'], task['id'],
                                                status['name'])

    print 'Project: {}'.format(project['name'])
