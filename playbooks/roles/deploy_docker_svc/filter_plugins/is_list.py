class FilterModule(object):
  def filters(self):
    return {
      'is_list': is_list,
    }

def is_list(value):
    ''' Test if data type is a list '''
    return isinstance(value, list)
