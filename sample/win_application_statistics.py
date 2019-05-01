#! /usr/bin/python
"""
Description: collect application information.

Author: Shayne Cardwell

Date: August 16, 2016

Module: win_application_statistics.py
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
    print('Had trouble finding packages000')
    print('Please install via the command below')
    print('pipenv install')
    sys.exit(1)


def _get_secrets(reports):
    try:
        with open('configs/secrets') as file_obj:
            secrets = json.loads(file_obj.read())
    except IOError as error:
        return utility.error_exception_handling(reports=reports, error=error)
    return secrets


def _get_wmi_obj(name):
    if name == node():
        return wmi.WMI()

    credentials = {
        'user_name': os.environ.get('USER', ''),
        'password':  os.environ.get('PASS', '')
    }
    return wmi.WMI(name, user=credentials['user_name'], password=credentials['password'])


def _get_reg_obj(name):
    if name == node():
        return wmi.WMI(name, namespace='root/default').StdRegProv

    credentials = {
        'user_name': os.environ.get('USER', ''),
        'password':  os.environ.get('PASS', '')
    }
    return wmi.WMI(name, namespace='root/default', user=credentials['user_name'],
                   password=credentials['password']).StdRegProv


def _run_process(reports, host):
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa384911(v=vs.85).aspx
    hkey = {
        'HKEY_CLASSES_ROOT':   2147483648,
        'HKEY_CURRENT_USER':   2147483649,
        'HKEY_LOCAL_MACHINE':  2147483650,
        'HKEY_USERS':          2147483651,
        'HKEY_CURRENT_CONFIG': 2147483653
    }
    reg = {}

    reg_paths = [r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
                 r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall']
    wmi_reg_obj = _get_reg_obj(host)

    for reg_path in reg_paths:
        first_layer = wmi_reg_obj.EnumKey(hDefKey=hkey['HKEY_LOCAL_MACHINE'],
                                          sSubKeyName=reg_path)[1]
        for item in first_layer:
            value_path = r'{0}\{1}'.format(reg_path, item)
            reg_paths.append(value_path)
            second_layer = wmi_reg_obj.EnumValues(hDefKey=hkey['HKEY_LOCAL_MACHINE'],
                                                  sSubKeyName=value_path)
            values = second_layer[1]
            if values:
                if 'DisplayName' in values:
                    display_name = wmi_reg_obj.GetStringValue(hDefKey=hkey['HKEY_LOCAL_MACHINE'],
                                                              sSubKeyName=value_path,
                                                              sValueName='DisplayName')[1]
                    reg[display_name] = {}
                    for val in values:
                        reg[display_name]['reg_path'] = r'HKLM\{0}'.format(value_path)
                        result = wmi_reg_obj.GetStringValue(hDefKey=hkey['HKEY_LOCAL_MACHINE'],
                                                            sSubKeyName=value_path, sValueName=val)
                        reg[display_name][val] = result[1]
                else:
                    reg[item] = {}
                    for val in values:
                        reg[item]['reg_path'] = r'HKLM\{0}'.format(value_path)
                        result = wmi_reg_obj.GetStringValue(hDefKey=hkey['HKEY_LOCAL_MACHINE'],
                                                            sSubKeyName=value_path, sValueName=val)
                        reg[item][val] = result[1]
            else:
                reg[item] = {}
                reg[item]['reg_path'] = r'HKLM\{0}'.format(reg_path)
                continue
    reports['content']['software_list'] = sorted(reg.keys())
    reports['content']['software_details'] = reg


def collect_win_application_stats(host=node(), is_threaded=0, queue=None):
    """Create business logic of the module.

    This module orchestrates the business logic for this module.

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
    print(json.dumps(collect_win_application_stats(), indent=4))


if __name__ == '__main__':
    main()
