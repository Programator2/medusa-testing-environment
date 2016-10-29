Medusa Testing Environment
==========================

Prerequisites
-------------

Medusa Testing Environment works on a VirtualBox virtual machine with a functional Medusa security module.
We recommend the newest version of VirtualBox.
For Medusa testing and development, we recommend the Debian distribution, specifically the Testing distribution that offers a compromise between new versions of packages and stability.

Network settings of the virtual machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Medusa testing environment communicates with the virtual machine using SSH protocol.
Make sure that virtual machine has functional SSH server.
SSH server is provided by the openssh-server package on Debian distribution.

There are many ways to configure network connection between guest and host operating systems.
We recommend using NAT with port forwarding from the guest port 22 to the host port 3022.
Host port can be set to any value, but it has to be correctly set in the testing environment commons.py module.

.. image:: doc/img/network_settings.png

.. image:: doc/img/port_forwarding.png

Installation instructions
-------------------------

Windows Installation Instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complete commons.py.sample file and rename it to commons.py.
Without correct information about virtual machine, the setup procedure won't work.

Install module win32com from http://sourceforge.net/projects/pywin32/

Set environment variables.
Via PowerShell:
    [Environment]::SetEnvironmentVariable("VBOX_INSTALL_PATH", "C:\Program Files\Oracle\VirtualBox", "Machine")
    [Environment]::SetEnvironmentVariable("VBOX_VERSION", "5.1.8", "Machine")

Run py -2 setup.py install


Linux Installation Instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complete commons.py.sample file and rename it to commons.py.
Without correct information about virtual machine, the setup procedure won't work.

Run python setup.py install

Configuration of the testing environment
----------------------------------------

Configuration constants are available in the commons.py module.
