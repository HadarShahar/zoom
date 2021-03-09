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


def get_saved_values(names: list) -> list:
    """
    Reads and returns the values associated with given names at
    the path HKEY_LOCAL_MACHINE\\{REG_PATH} (where they were saved).
    """
    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY)  # access the 64-bit registry view from 32-bit python
        values = []
        for name in names:
            value, regtype = winreg.QueryValueEx(registry_key, name)
            values.append(value)
        winreg.CloseKey(registry_key)
        return values
    except WindowsError as e:
        print('get_saved_values:', e)


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
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                      REG_PATH, 0, winreg.KEY_WRITE)
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


def generate_reg_file(output_file='registry\\reg_constants.reg'):
    """
    Generates a .reg file ready to be double clicked
    to save all the values in the registry at HKEY_LOCAL_MACHINE\\{REG_PATH}.
    These values are all the global variables
    in the file registry_constants.py.
    """
    with open(output_file, 'w') as file:
        file.write('Windows Registry Editor Version 5.00\n\n')
        file.write(f'[HKEY_LOCAL_MACHINE\\{REG_PATH}]\n')

        global_vars = vars(registry_constants)
        for name, value in global_vars.items():
            # skip special variables like __doc__
            if name.startswith('__'):
                continue

            print(name, value)
            reg_value = ''
            if type(value) == str:
                reg_value = f'"{value}"'
            elif type(value) == int:
                reg_value = f'dword:{hex(value)[2:].zfill(8)}'
            else:
                print('Unsupported value type:', type(value))
                continue

            file.write(f'"{name}"={reg_value}\n')
        file.write('\n')


if __name__ == '__main__':
    # set_reg_values()
    generate_reg_file()
