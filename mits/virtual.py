# -*- coding: utf-8 -*-
"""
@package mits.virtual
Controls Virtual machine execution
"""
import time
import commons
import remote_shell

from vboxapi import VirtualBoxManager
from logger import log_host

def remote_start_guest_machine():
    """
    Starts the virtual machine. If it was not running before, it waits
    50 seconds for the system to boot up.
    """
    mgr = VirtualBoxManager(None, None)
    vbox = mgr.vbox
    log_host(f"Running VirtualBox version {vbox.version}")
    machine = vbox.findMachine(commons.VM_NAME)
    session = mgr.getSessionObject(vbox)
    if machine.state == mgr.constants.all_values('MachineState')['Running']:
        log_host('VM is already running')
    elif machine.state == mgr.constants.all_values('MachineState')['PoweredOff'] or \
         machine.state == mgr.constants.all_values('MachineState')['Saved']:
        # TODO split this condition
        progress = machine.launchVMProcess(session, 'gui', '')
        progress.waitForCompletion(-1)
        log_host('VM succesfully started')
        log_host('Waiting for boot')
        # Waiting till virtual machine is ready to accept SSH connection
        time.sleep(50)
        # TODO try ping
    else:
        machine_state = str(machine.state)
        raise RuntimeError('Unexpected virtual machine state')
        # TODO nicer message for the user


def setup_virtual_pc():
    """
    Used during installation of the testing environment to a virtual machine.
    """
    #start_machine()
    log_host('Starting SSH conection')
    remote_shell.setup_virtual_pc()
