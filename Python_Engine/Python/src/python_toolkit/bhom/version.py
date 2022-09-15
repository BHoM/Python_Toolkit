from win32api import GetFileVersionInfo, LOWORD, HIWORD

def version(filename):
    """Return the version of a compiled Windows DLL"""
    info = GetFileVersionInfo(filename, "\\")
    ms = info['FileVersionMS']
    ls = info['FileVersionLS']
    return HIWORD (ms), LOWORD (ms), HIWORD (ls), LOWORD (ls)
