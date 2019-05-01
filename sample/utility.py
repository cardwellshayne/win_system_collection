#! /usr/bin/python3
"""
Description: Provide common features used across multiple files in the project.

Title: utility.py

Author: Shayne Cardwell
"""
import ast
import json
import os
from datetime import datetime
from traceback import format_exc


def _clean_win32_obj(instance):
    item = instance[instance.find('{') + 1:instance.rfind('}')].replace(';', ',')
    item = item.replace('{', '[').replace('}', ']')
    item = ''.join([k.replace('\t', '"') for k in item.splitlines()])
    item = item.rstrip(',')
    item = ''.join(['{', item, '}']).replace('TRUE', 'True').replace('FALSE', 'False').replace(
        'NULL', 'None')
    os_dict = ast.literal_eval(item.replace(' = ', '" : '))
    for k in os_dict.keys():
        if isinstance(os_dict[k], str):
            os_dict[k.rstrip()] = os_dict[k].lstrip().rstrip()
        os_dict[k.rstrip()] = os_dict[k]
    return os_dict


def clean_win32_obj(str_obj):
    """Return a dictionary of the Win_32 class specified.

    This function will take the string representation of a Win32
    class and will return a dictionary or the representing string.

    >>> str_obj = '''instance of Win32_Processor
    ... {
    ... 	AddressWidth = 64;
    ... 	Architecture = 9;
    ... 	Availability = 3;
    ... 	Caption = "Intel64 Family 6 Model 15 Stepping 6";
    ... 	CpuStatus = 1;
    ... 	CreationClassName = "Win32_Processor";
    ... 	CurrentClockSpeed = 2667;
    ... 	CurrentVoltage = 17;
    ... 	DataWidth = 64;
    ... 	Description = "Intel64 Family 6 Model 15 Stepping 6";
    ... 	DeviceID = "CPU0";
    ... 	ExtClock = 266;
    ... 	Family = 1;
    ... 	L2CacheSize = 4096;
    ... 	L3CacheSize = 0;
    ... 	L3CacheSpeed = 0;
    ... 	Level = 6;
    ... 	LoadPercentage = 67;
    ... 	Manufacturer = "GenuineIntel";
    ... 	MaxClockSpeed = 2667;
    ... 	Name = "Intel(R) Core(TM)2 CPU          6700  @ 2.66GHz";
    ... 	NumberOfCores = 2;
    ... 	NumberOfLogicalProcessors = 2;
    ... 	PowerManagementSupported = FALSE;
    ... 	ProcessorId = "BFEBFBFF000006F6";
    ... 	ProcessorType = 3;
    ... 	Revision = 3846;
    ... 	Role = "CPU";
    ... 	SocketDesignation = "Socket 775";
    ... 	Status = "OK";
    ... 	StatusInfo = 3;
    ... 	Stepping = "6";
    ... 	SystemCreationClassName = "Win32_ComputerSystem";
    ... 	SystemName = "LUDRAC-PC";
    ... 	UpgradeMethod = 4;
    ... 	Version = "Model 15, Stepping 6";
    ... };'''
    {'L2CacheSize': 4096, 'PowerManagementSupported': False, 'LoadPercentage': 60,
    'Architecture': 9, 'Version':
    'Model 15, Stepping 6', 'MaxClockSpeed': 2667, 'CpuStatus': 1, 'Revision': 3846, 'Status':
    'OK', 'Description':
    'Intel64 Family 6 Model 15 Stepping 6', 'AddressWidth': 64, 'ProcessorId':
    'BFEBFBFF000006F6', 'ProcessorType':
    3, 'SocketDesignation': 'Socket 775', 'CurrentClockSpeed': 2667, 'Role': 'CPU',
    'Manufacturer': 'GenuineIntel',
    'Name': 'Intel(R) Core(TM)2 CPU          6700  @ 2.66GHz', 'Level': 6, 'CurrentVoltage': 17,
    'NumberOfCores': 2,
    'Caption': 'Intel64 Family 6 Model 15 Stepping 6', 'StatusInfo': 3, 'DeviceID': 'CPU0',
    'NumberOfLogicalProcessors': 2, 'Family': 1, 'UpgradeMethod': 4, 'SystemName': 'LUDRAC-PC',
    'ExtClock': 266,
    'Stepping': '6', 'CreationClassName': 'Win32_Processor', 'L3CacheSize': 0, 'L3CacheSpeed': 0,
    'Availability': 3,
    'SystemCreationClassName': 'Win32_ComputerSystem', 'DataWidth': 64}

    pretty sample output:
        "CPU0": {
            "L2CacheSize": 4096,
            "PowerManagementSupported": false,
            "LoadPercentage": 51,
            "Architecture": 9,
            "Version": "Model 15, Stepping 6",
            "MaxClockSpeed": 2667,
            "CpuStatus": 1,
            "Revision": 3846,
            "Status": "OK",
            "Description": "Intel64 Family 6 Model 15 Stepping 6",
            "AddressWidth": 64,
            "ProcessorId": "BFEBFBFF000006F6",
            "ProcessorType": 3,
            "SocketDesignation": "Socket 775",
            "CurrentClockSpeed": 2667,
            "Role": "CPU",
            "Manufacturer": "GenuineIntel",
            "Name": "Intel(R) Core(TM)2 CPU          6700  @ 2.66GHz",
            "Level": 6,
            "CurrentVoltage": 17,
            "NumberOfCores": 2,
            "Caption": "Intel64 Family 6 Model 15 Stepping 6",
            "StatusInfo": 3,
            "DeviceID": "CPU0",
            "NumberOfLogicalProcessors": 2,
            "Family": 1,
            "UpgradeMethod": 4,
            "SystemName": "LUDRAC-PC",
            "ExtClock": 266,
            "Stepping": "6",
            "CreationClassName": "Win32_Processor",
            "L3CacheSize": 0,
            "L3CacheSpeed": 0,
            "Availability": 3,
            "SystemCreationClassName": "Win32_ComputerSystem",
            "DataWidth": 64
        }

    Args:
        str_obj(string): The string represenstation of the win32 object

    Returns:
        item_dict(dict): A key value object representing the win32
            object

    """
    return _clean_win32_obj(str_obj)


def reporting(reports):
    """Report duties performed.

    This function is used to finalize information

    Args:
        reports(dict): Reporting key, value object used to store basic
            reporting about the module

    Returns:
        return_body(dict): A key, value object that contains the
            response that is sent to the requester

    """
    os.chdir(reports['project_dir'])
    os.makedirs(reports['log_path'], exist_ok=True)
    reports['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reports['return_body']['outcome'] = reports['outcome']
    reports['return_body']['messages'] = reports['messages']
    reports['return_body']['content'] = reports['content']

    try:
        with open('{0}/{1}_report'.format(reports['log_path'], reports['capability_name']),
                  'a') as file_object:
            json.dump(reports, file_object)
            file_object.write('\n')
    except IOError as error:
        reports['return_body']['messages'].append('Error with logging procedure')
        reports['return_body']['exception'] = format_exc()
        reports['return_body']['messages'].append(str(error))
    return reports['return_body']


def error_exception_handling(reports, error, message=None):
    """Set error settings to be reported.

    This function sets the specific error settings required when
    exceptions are caught.

    Args:
        reports(dict): Reporting key, value object used to store basic
            reporting about the module
        error(exception): The exception that is raised.
        message(string): Optional, personal message

    Returns:
        return_body(dict): A key, value object that contains the
            response that is sent to the requester

    """
    reports['outcome'] = 'Failed'
    reports['exception'] = format_exc()
    reports['messages'].append(str(error))
    if message:
        reports['messages'].append(message)
    return reporting(reports)
