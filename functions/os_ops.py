import imp
import os
import subprocess as sp

paths = {
    'notepad': "C:\Windows\notepad.exe",
    'calculator': "C:\Windows\System32\calc.exe",

}

def open_camera():
    sp.run('start microsoft.windows.camera:', shell=True)

def open_calculator():
    sp.Popen(paths['calculator'])



