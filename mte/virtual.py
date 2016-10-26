# -*- coding: utf-8 -*-
"""@package mte.virtual
Controls Virtual machine execution
"""
import time
from vboxapi import VirtualBoxManager

import commons
import shell


def start_machine():
    """
    Starts the virtual machine. If it was not running before, it waits 50 seconds for the system to boot up.
    """
    mgr = VirtualBoxManager(None, None)
    vbox = mgr.vbox
    print "Running VirtualBox version %s" % vbox.version
    machine = vbox.findMachine(commons.VM_NAME)
    session = mgr.getSessionObject(vbox)
    if machine.state == mgr.constants.all_values('MachineState')['Running']:
        print 'VM is already running'
        pass
    elif machine.state == mgr.constants.all_values('MachineState')['PoweredOff']:
        progress = machine.launchVMProcess(session, 'gui', '')
        progress.waitForCompletion(-1)
        print 'VM succesfully started'
        print 'Waiting for boot'
        # Waiting till virtual machine is ready to accept SSH connection
        time.sleep(50)
    else:
        raise RuntimeError('Unexpected virtual machine state')


def main(*argv):
    """
    Used during normal testing. Afterwards it begins an SSH connection to the running machine.
    @param argv: Tuple of two lists. First list contains names of system calls to be tested and second one contains
     names of the testing suites to be run.
    """
    start_machine()
    print 'Starting SSH conection'
    shell.connect(argv)


def setup_virtual_pc():
    """
    Used during installation of the testing environment to a virtual machine.
    """
    start_machine()
    print 'Starting SSH conection'
    shell.setup_virtual_pc()
