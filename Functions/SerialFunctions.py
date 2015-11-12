import winreg
import itertools
import re
__author__ = 'Piotr'


def enumerateSerialPorts():
    """ Uses the Win32 registry to return an
        iterator of serial (COM) ports
        existing on this computer.
    """
    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
    except WindowsError:
        #TODO Check this error, should be IterationError
        raise StopIteration

    for i in itertools.count():
        try:
            val = winreg.EnumValue(key, i)
            yield str(val[1])
        except EnvironmentError:
            break


def fullPortName(portname):
    """ Given a port-name (of the form COM7,
        COM12, CNCA0, etc.) returns a full
        name suitable for opening with the
        Serial class.
    """
    m = re.match('^COM(\d+)$', portname)
    if m and int(m.group(1)) < 10:
        return portname
    return '\\\\.\\' + portname