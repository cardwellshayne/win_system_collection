#! /usr/bin/python
"""
Description: collect windows system information.

Author: Shayne Cardwell

Date: August 16, 2016

Module: win_system_get_statistics.py
"""
from __future__ import print_function

import json
import os
import sys
from datetime import datetime
from multiprocessing.dummy import Process as _Process
from multiprocessing.dummy import Queue
from platform import node

# This setup was specifically added to stay in compliance with PEP008
sys.path.insert(1, os.path.abspath('required_packages'))
try:
    import sample.utility as utility
    from sample.win_application_statistics import collect_win_application_stats
    from sample.win_bios_statistics import collect_win_bios_stats
    from sample.win_drive_statistics import collect_win_disk_stats
    from sample.win_local_accounts_statistics import collect_win_local_account_stats
    from sample.win_local_groups_statistics import collect_win_local_group_stats
    from sample.win_memory_statistics import collect_win_mem_stats
    from sample.win_network_statistics import collect_win_network_stats
    from sample.win_os_statistics import collect_os_stats
    from sample.win_processes_statistics import collect_win_processes_stats
    from sample.win_processor_statistics import collect_win_cpu_stats
    from sample.win_services_statistics import collect_win_services_stats
except ModuleNotFoundError:
    print('Had trouble finding packages')
    print('Please install via the command below')
    print('pipenv install')
    sys.exit(1)


def _execute_funtion(function, arg):
    function(arg)


def _get_hardware(host):
    hardware_functions = [collect_win_bios_stats, collect_win_disk_stats, collect_win_mem_stats,
                          collect_win_network_stats, collect_win_cpu_stats]
    hardware_info = {}
    for hardware in hardware_functions:
        hardware_info.update(hardware(host)['content'])
    return hardware_info


def _get_hardware_threaded(host):
    hardware_functions = [collect_win_bios_stats, collect_win_disk_stats, collect_win_mem_stats,
                          collect_win_network_stats, collect_win_cpu_stats]
    hardware_info = {}
    queue = Queue()
    list_of_processes = []

    for hardware in hardware_functions:
        process = _Process(target=hardware, args=(host, 1, queue,))
        list_of_processes.append(process)
        process.start()

    for process in list_of_processes:
        process.join()
        hardware_info.update(queue.get())
    return hardware_info


def _get_system_information(host):
    system_information_functions = [collect_win_application_stats, collect_win_bios_stats,
                                    collect_win_disk_stats, collect_win_local_account_stats,
                                    collect_win_local_group_stats, collect_win_mem_stats,
                                    collect_win_network_stats, collect_os_stats,
                                    collect_win_processes_stats, collect_win_cpu_stats,
                                    collect_win_services_stats]
    system_information = {}
    for sys_info in system_information_functions:
        system_information.update(sys_info(host)['content'])
    return system_information


def _get_system_information_threaded(host):
    system_information_functions = [collect_win_application_stats, collect_win_bios_stats,
                                    collect_win_disk_stats, collect_win_local_account_stats,
                                    collect_win_local_group_stats, collect_win_mem_stats,
                                    collect_win_network_stats, collect_os_stats,
                                    collect_win_processes_stats, collect_win_cpu_stats,
                                    collect_win_services_stats]
    system_information = {}
    queue = Queue()
    list_of_processes = []

    for hardware in system_information_functions:
        process = _Process(target=hardware, args=(host, 1, queue,))
        list_of_processes.append(process)
        process.start()

    for process in list_of_processes:
        process.join()
        system_information.update(queue.get())
    return system_information


def get_hardware_information(machine_name):
    """Return Hardware information.

    This functions collects all the hardware information about a host.

    Args:
        machine_name(string): The name of the host

    Returns:
        hardware_info(dict): A key value object that contains the
            hardware information about the machine

    """
    # hardware_info = _get_hardware(machine_name)
    hardware_info = _get_hardware_threaded(machine_name)
    return hardware_info


def get_system_information(machine_name):
    """Return System information.

    This functions collects a lot of system information about a host.

    Args:
        machine_name(string): The name of the host

    Returns:
        system_info(dict): A key value object that contains the
            hardware information about the machine

    """
    # system_info = _get_system_information(machine_name)
    system_info = _get_system_information_threaded(machine_name)
    return system_info


def collect_system_stats(machine_name=node()):
    """Create business logic of the module.

    This module orchestrates the business logic for this module

    Returns:
        return_body(dict): A key, value object that contains the
            response that is sent to the requester

    """
    reports = {
        'messages':        [],
        'start_time':      datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'capability_name': str(os.path.basename(__file__)[:-3]),
        'version':         '0',
        'host':            node(),
        'project_dir':     os.getcwd(),
        'log_path':        'logs/',
        'outcome':         'Failed',
        'content':         {},
        'return_body':     {}
    }
    print(reports['start_time'])
    # reports['content'] = get_hardware_information(machine_name)
    reports['content'] = get_system_information(machine_name)

    utility.reporting(reports)
    print('start time: {0}'.format(reports['start_time']))
    print('end time: {0}'.format(reports['end_time']))
    reports['outcome'] = 'Successful'
    return utility.reporting(reports)


def main():
    """Make module a standalone module."""
    print(json.dumps(collect_system_stats(), indent=4))


if __name__ == '__main__':
    main()
