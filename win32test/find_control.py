from time import sleep
import uiautomation


def address_callback(c, d):
    # st = "Address and search bar"
    st = "שורת חיפוש וכתובות אתרים"
    return isinstance(c, uiautomation.EditControl) and st in c.Name


def get_url():
    control = uiautomation.FindControl(None, address_callback)
    return control.GetValuePattern().Value


def callback(c, d):
    print(c)
    return False
    # return isinstance(c, uiautomation.ButtonControl) and 'התחל' in c.Name


def test():
    control = uiautomation.FindControl(None, callback)


if __name__ == '__main__':
    print(get_url())
    test()
