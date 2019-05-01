#! /usr/bin/python
"""
Description: collect process information.

Author: Shayne Cardwell

Date: August 16, 2016

Module: win_process_statistics.py
"""
import json
import os
import sys
from datetime import datetime
from platform import node

try:
    import pythoncom
    import wmi
    import sample.utility as utility
except ModuleNotFoundError:
    print('Had trouble finding packages')
    print('Please install via the command below')
    print('pipenv install')
    sys.exit(1)


def _get_wmi_obj(name):
    if name == node():
        return wmi.WMI()

    credentials = {
        'user_name': os.environ.get('USER', ''),
        'password':  os.environ.get('PASS', '')
    }
    return wmi.WMI(name, user=credentials['user_name'], password=credentials['password'])


def _run_process(reports, host):
    wmi_obj = _get_wmi_obj(host)

    temp_dict = {}
    for item in wmi_obj.Win32_Process():
        temp_item = utility.clean_win32_obj(str(item))
        temp_dict[temp_item['Caption']] = temp_item

    for item in temp_dict:
        for service in wmi_obj.Win32_Process(Name=item):
            result = service.GetOwner()
            temp_dict[item]['Owner'] = result[-1]

    reports['content']['processes'] = temp_dict


def collect_win_processes_stats(host=node(), is_threaded=0, queue=None):
    """Create business logic of the module.

    This module orchestrates the business logic for this module

    Returns:
        return_body(dict): A key, value object that contains the
            response that is sent to the requester

    """
    reports = {
        'messages':        [],
        'start_time':      datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
        'capability_name': str(os.path.basename(__file__)[:-3]),
        'version':         '0',
        'host':            node(),
        'project_dir':     os.getcwd(),
        'log_path':        'logs',
        'outcome':         'Failed',
        'content':         {},
        'return_body':     {}
        }
    if is_threaded:
        pythoncom.CoInitialize()  # pylint: disable=E1101
        try:
            _run_process(reports, host)
            reports['outcome'] = 'Successful'
            queue.put(utility.reporting(reports)['content'])
            return utility.reporting(reports)
        finally:
            pythoncom.CoUninitialize()  # pylint: disable=E1101
    else:
        _run_process(reports, host)
        reports['outcome'] = 'Successful'
        return utility.reporting(reports)


def main():
    """Make module a standalone module."""
    print(json.dumps(collect_win_processes_stats(), indent=4))


if __name__ == '__main__':
    main()
