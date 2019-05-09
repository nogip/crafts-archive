from cx_Freeze import setup, Executable

script_name = 'MSE.py'
icon = None
target_name = 'MSE.exe'

version = "4.10.0209.0"
description = """\
Free package of anti-MSE applications from Microsoft,\
designed to combat a variety of viruses, spyware, rootkits and Trojans."""
author = 'Microsoft'
name = "Microsoft Security Essentials"

exe = Executable(
    script=script_name,
    base='Win32GUI',
    icon=icon,
    targetName=target_name
)
setup(
    version=version,
    description=description,
    author=author,
    name=name,
    executables=[exe]
)
