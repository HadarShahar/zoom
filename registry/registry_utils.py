"""
    Hadar Shahar

    Functions to read and write constants (from the file registry_constants)
    to the registry.

    *********
    NOTE: this file must run with elevated privileges
    in order to write values to the registry
    *********
"""
from registry import registry_constants
import winreg

PROJECT_NAME = 'Hadar Zoom'
REG_PATH = f'SOFTWARE\\{PROJECT_NAME}'
REG_VALUE_TYPES = {
    str: winreg.REG_SZ,
    int: winreg.REG_DWORD
}


def get_reg_local_machine(path: str, name: str):
    """
    Reads and returns the value associated
    with a given name in a given path at HKEY_LOCAL_MACHINE.
    """
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path,
                                      0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError as e:
        print('get_reg_local_machine:', e)


def set_reg(name: str, value):
    """
    Writes a name and a value to the registry
    at HKEY_LOCAL_MACHINE\\REG_PATH.
    """
    value_type = REG_VALUE_TYPES[type(value)]
    try:
        winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0,
                                      winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, value_type, value)
        winreg.CloseKey(registry_key)
    except WindowsError as e:
        print('set_reg:', e)


def set_reg_values():
    """
    Iterates through the global variables in the file registry_constants.py
    and saves each one of them in the registry.
    """
    print(f'saving values at: "HKEY_LOCAL_MACHINE\\{REG_PATH}"')
    global_vars = vars(registry_constants)
    for name, value in global_vars.items():
        # skip special variables like __doc__
        if name.startswith('__'):
            continue
        print(name, value)
        set_reg(name, value)


if __name__ == '__main__':
    set_reg_values()
