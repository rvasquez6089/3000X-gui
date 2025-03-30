import sys
import subprocess


def convert(ui_file):
    py_file = ui_file[:-3]
    py_file = 'ui_'+ py_file + '.py'

    py_file = "".join(py_file)
    ui_file = "".join(ui_file)

    subprocess.call(["pyuic5", "-x", ui_file, "-o", py_file])

    print(ui_file, "has been converted to", py_file, "\n")

convert('capturegui.ui')