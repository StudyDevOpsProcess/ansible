from ansible import errors

class FilterModule(object):
  def filters(self):
    return {
      'docker_service_options': docker_service_options,
    }

'''
docker_service_options(values, service_mode, service_image, service_tag)

values: The options of our docker service command
service_mode: Valid values are 'create' or 'update'
service_image: The name of our image
service_tag: The name of the image tag

This ansible filter takes in a standard service definition as it would be interpreted for
a 'docker service create' command, and modifies the option keys to be used for a
'docker service update' command.

We make no changes if we are running `docker service create`

For 'docker service update', the following table summarizes the nature of the changes
# ------------------------------------------------------------------------------------ #
# `docker service create`           | `docker service update`                          #
# ------------------------------------------------------------------------------------ #
# '--constraint'                    -> '--constraint-add'                              #
# '--container-label'               -> '--container-label-add'                         #
# '--env'                           -> '--env-add'                                     #
# (IMAGE provided as arg, not opt)  -> '--image {{ service.image }}:{{ service.tag }}' #
# '--label'                         -> '--label-add'                                   #
# '--mount'                         -> (removed)                                       #
# '--name'			    -> (removed)				       #
# '--network'                       -> (removed)                                       #
# '--publish'                       -> '--publish-add'                                 #
# ------------------------------------------------------------------------------------ #

It is possible to delete values with 'docker service update', however, we make no attempt to do so.
'''
def docker_service_options(values, service_mode, service_image, service_tag):

  MODIFY_ADD_OPTIONS = ['constraint','container-label','dns','dns-option','dns-search',
			'env','group','host','label','publish','secret']
  REMOVE_OPTIONS = ['env-file','help','network','mode','name','mount','secret']

  ''' Modify option keys if we're doing an update '''
  if service_mode == 'update':
    new_values = list()
    for (k, v) in values:
      if k in REMOVE_OPTIONS:
        continue
      if k in MODIFY_ADD_OPTIONS:
        new_values.append( (u'{0}-add'.format(k), v) )
      else:
        new_values.append((k,v))
    new_values.append( (u'image', '{0}:{1}'.format(service_image, service_tag)) )
    return new_values
  elif service_mode == 'create':
    ''' Return immediately without changing anything if we are doing a create '''
    return values
  else:
    raise errors.AnsibleFilterError(
      "Supported service_mode values: 'update', 'create'")

# Run interactively to execute tests below
if __name__ == '__main__':
  DOCKER_1_13_1_OPTS =[['constraint', None],['container-label', None],['dns', None],['dns-option', None],['dns-search', None],
			['endpoint-mode', None],['env', None],['env-file', None],['group', None],['health-cmd', None],
			['health-interval', None],['health-retries', None],['health-timeout', None],['help', None],['host', None],
			['hostname', None],['label', None],['limit-cpu', None],['limit-memory', None],['log-driver', None],
			['log-opt', None],['mode', None],['mount', None],['name', None],['network', None],
			['no-healthcheck', None],['publish', None],['replicas', None],['reserve-cpu', None],['reserve-memory', None],
			['restart-condition', None],
			['restart-delay', None],['restart-max-attempts', None],['restart-window', None],['secret', None],['stop-grace-period', None],
			['tty', None],['update-delay', None],['update-failure-action', None],['update-max-failure-ratio', None],['update-monitor', None],
			['update-parallelism', None],['user', None],['with-registry-auth', None],['workdir', None]]

  service_image = 'example-service'
  service_tag = 'latest'

  service_mode = 'create'
  print("Testing {} mode output".format(service_mode))
  test_out = docker_service_options(DOCKER_1_13_1_OPTS, service_mode, service_image, service_tag)
  print("Option length, pre-call: {}, Option length, post-call: {}".format(len(DOCKER_1_13_1_OPTS), len(test_out)))
  print("Raw output: {}".format(test_out))
  print
  service_mode = 'update'
  print("Testing {} mode output".format(service_mode))
  test_out = docker_service_options(DOCKER_1_13_1_OPTS, service_mode, service_image, service_tag)
  print("Option length, pre-call: {}, Option length, post-call: {}".format(len(DOCKER_1_13_1_OPTS), len(test_out)))
  print("Raw output: {}".format(test_out))
  print
  service_mode = 'error'
  print("Testing {} mode output - Expect raise error.AnsibleFilterError".format(service_mode))
  test_out = docker_service_options(DOCKER_1_13_1_OPTS, service_mode, service_image, service_tag)
  print("Option length, pre-call: {}, Option length, post-call: {}".format(len(DOCKER_1_13_1_OPTS), len(test_out)))
  print("Raw output: {}".format(test_out))
