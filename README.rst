Medusa Testing Environment
==========================

Windows Installation Instructions
---------------------------------

Complete commons.py file. Without correct information about virtual machine, the setup procedure won't work.

Install module win32com from http://sourceforge.net/projects/pywin32/

Set environment variables.
Via PowerShell:
    [Environment]::SetEnvironmentVariable("VBOX_INSTALL_PATH", "C:\Program Files\Oracle\VirtualBox", "Machine")
    [Environment]::SetEnvironmentVariable("VBOX_VERSION", "5.0.16", "Machine")

Run py -2 setup.py install


Linux Installation Instructions
-------------------------------
