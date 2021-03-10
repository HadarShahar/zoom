"""
    Hadar Shahar
    Reads the network constants from the registry and stores them
    in a named tuple for easy access.
"""
import sys
from collections import namedtuple
from registry.registry_utils import get_saved_values

registry_keys = ['SERVER_IP', 'AUTH_SERVER_PORT']
for channel in ('INFO', 'VIDEO', 'AUDIO', 'CHAT', 'SCREEN'):
    registry_keys.append(f'CLIENT_IN_{channel}_PORT')
    registry_keys.append(f'CLIENT_OUT_{channel}_PORT')

registry_values = get_saved_values(registry_keys)
if len(registry_keys) != len(registry_values):
    print(r'Missing constants in the registry, you have to import ' +
          r'the file at "registry\reg_constants.reg" to the registry ' +
          r'(by double clicking on it).')
    sys.exit()

Constants = namedtuple('Constants', registry_keys)._make(registry_values)
