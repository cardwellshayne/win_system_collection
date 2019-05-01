#! /usr/bin/python
"""
Description: collect local group information.

Author: Shayne Cardwell

Date: August 16, 2016

Module: win_local_groups_statistics.py
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
    for item in wmi_obj.Win32_Group():
        temp_item = utility.clean_win32_obj(str(item))
        if temp_item['Name'] not in temp_dict:
            temp_dict[temp_item['Name']] = {}
        temp_dict[temp_item['Name']]['group_information'] = temp_item
    reports['content']['local_groups'] = temp_dict

    temp_dict = {}
    for item in wmi_obj.Win32_GroupUser():
        temp_item = utility.clean_win32_obj(str(item))
        group_name = temp_item['GroupComponent'].split(',')[1].split('=')[1].strip('"')
        if group_name not in temp_dict:
            temp_dict[group_name] = []
        temp_dict[group_name].append(temp_item)

    for name in temp_dict:
        for component in temp_dict[name]:
            user_name = component['PartComponent'].split(',')[1].split('=')[1].strip('"')
            if name in reports['content']['local_groups']:
                if 'group_users' not in reports['content']['local_groups'][name]:
                    reports['content']['local_groups'][name]['group_users'] = []
                reports['content']['local_groups'][name]['group_users'].append(user_name)


def collect_win_local_group_stats(host=node(), is_threaded=0, queue=None):
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
    print(json.dumps(collect_win_local_group_stats(), indent=4))


if __name__ == '__main__':
    main()
