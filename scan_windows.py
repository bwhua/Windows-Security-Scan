import win32com.client
import win32con
import win32api
import pywintypes
import re
import platform
import wmi
import socket
import pythoncom
import uuid
import winreg
import subprocess
import os
import json
from datetime import *

# get_basic_machine_info uses the platform library to retreive
# system info, the machine name, version number, and processor
def last_scanned():
    try:
        with open("computer_info.json", "r") as read_file:
            data = json.load(read_file)
            date = data["Date"]
            last_scanned = datetime(int(date["Year"]), int(date["Month"]), int(date["Day"]))
            if((last_scanned + timedelta(days = 30)) >= datetime.now()):
                print("Machine scanned within last 30 days")
            else:
                make_json()
    except FileNotFoundError:
        make_json()

def get_basic_machine_info():
    my_Sys = wmi.WMI () #Where the Device Information is being stored

    data = {'System Info': my_Sys.Win32_OperatingSystem()[0].Caption,
                           'Machine Name': platform.node(),
                           'Version': platform.version(),
                           'Processor': platform.processor()}
    return data

# This runs 'netsh advfirewall show allprofiles' in the windows terminal
# to gather information on if the firewall is truned on
def get_firewall():
    firewall = subprocess.check_output(['netsh', 'advfirewall', 'show', 'allprofiles']).decode('utf-8')
    #Pruning output to say ON or OFF
    firewall = re.split('\n', firewall)
    firewall = re.sub(r'(State *)', '', firewall[3])
    firewall = re.split('\r', firewall)[0]
    return firewall

# This runs 'powercfg /list' and 'powercfg /query {GUID} 238c9fa8-0aad-41ed-83f4-97be242c8f20'
# to determine the mount of idle time it takes for the computer to sleep
def get_screen_lock():
    GUID = subprocess.check_output(['powercfg', '/list'])
    GUID = GUID.decode('utf-8')
    GUID = re.split('\n', GUID)[3]
    GUID = re.split(' ', GUID)[3]

    minutes = subprocess.check_output(['powercfg', '/query', GUID,  '238c9fa8-0aad-41ed-83f4-97be242c8f20'])
    minutes = minutes.decode('utf-8')
    minutes = re.split('\n', minutes)

    minutes = re.split(' ', minutes[10])
    minutes = re.split('0x', minutes[9])
    minutes = int(minutes[1], 16)//60
    return minutes

# This is checking if our remote login is enabled using the
# 'netsh advfirewall show allprofiles' in tihe windows terminal.
def get_remote_login():
    remote_login = subprocess.check_output(['netsh', 'advfirewall', 'show', 'allprofiles']).decode('utf-8')

    remote_login = re.split('\n', remote_login)
    remote_login = re.sub(r'(RemoteManagement *)', '', remote_login[8])
    remote_login = re.split('\r', remote_login)
    return remote_login[0] + 'd'

# This gets information on visible internet options usind
# The windows terminal command 'wifi scan'
def get_wifi_info():
    wifi_info = subprocess.check_output(['netsh','wlan', 'show', 'networks']).decode('utf-8')
    wifi_info = re.sub(r'((\r\n\r\n\r\n)|(\n\n)|(\r)|(\t)|  )', '', wifi_info)
    wifi_info = re.split('\n', wifi_info)
    return_dict = {}
    while(len(wifi_info) != 0):
        check_ssid = wifi_info.pop(0)
        if(check_ssid[:4] == 'SSID'):
            ssid = re.split(': ', check_ssid)[1]
            return_dict[ssid] = {'Network Type': re.split(': ', wifi_info.pop(0))[1],
                                 'Authentication': re.split(': ', wifi_info.pop(0))[1],
                                 'Encryption': re.split(': ', wifi_info.pop(0))[1]}
    return return_dict

# Gets software list (from 2 places: the local machine
# (32 bit and 64 bit) and the current user)
def get_software_list():
    software_list = getSoftwareListHelper(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)
    software_list += getSoftwareListHelper(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY)
    software_list += getSoftwareListHelper(winreg.HKEY_CURRENT_USER, 0)
    programs = 'List of downloaded software:\n'
    return software_list

# This is a helper function for get software list.
# This looks for programs that can be uninstalled
def getSoftwareListHelper(hive, flag):
    aReg = winreg.ConnectRegistry(None, hive)
    aKey = winreg.OpenKey(aReg, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall', 0, winreg.KEY_READ | flag)
    count_subkey = winreg.QueryInfoKey(aKey)[0]
    software_list = []

    for i in range(count_subkey):
        software = {}
        try:
            asubkey_name = winreg.EnumKey(aKey, i)
            asubkey = winreg.OpenKey(aKey, asubkey_name)
            software['name'] = winreg.QueryValueEx(asubkey, 'DisplayName')[0]
            software_list.append(software['name'])
        except EnvironmentError:
            continue
    return software_list

# Gets a list of startup programs using the windows command 'wmic startup get caption'
# note: all of these programs startup function can be enabled/disabled, this function doesn't convey that
def get_startup_programs():
    startup = subprocess.check_output(['wmic', 'startup', 'get', 'caption'])
    startup = startup.decode('utf-8')
    startup = re.sub('[\r ]', '', startup)
    startup = re.split('\n', startup)
    startup.pop(0)
    return startup

# Get IP address
def get_ip_addr():
    hostname = socket.getfqdn()
    return socket.gethostbyname(hostname)

# Gets MAC address
def get_mac_addr():
    mac = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
    for ele in range(0,8*6,8)][::-1]))
    return mac.upper()

# Gets total and available disk space in GBs
def get_memory():
    my_Sys = wmi.WMI () #Where the Device Information is being stored
    total_memory = (my_Sys.Win32_LogicalDisk()[0].Size) #Total Space in Computer. Calling function
    available_memory = my_Sys.Win32_LogicalDisk()[0].Freespace #Avaliable Space left. Calling Function

    total_memory = int(total_memory)/(1024*1024*1024) #Int Conversion
    available_memory = int (available_memory)/(1024*1024*1024) #Bytes to Gigabytes
    memory = {'Total Memory': total_memory,
            'Available Memory': available_memory}
    return memory

# A function to translate hex values to an address.
def hex2addr(val):
    address = ' ' #Empty Variable
    for ch in val: #For Character in Value

        address += ('%02x '% ord(ch))
        address = address.replace(' ', ':')[0:17]
    return address

# Gets a list of SSIDs that you've connected to/ the computer remembers
def get_wifi_history():
    history = subprocess.check_output(['netsh','wlan', 'show', 'profiles']).decode('utf-8')
    history = re.sub(r'(\r\n)+', '', history)
    history = re.split('    All User Profile     : ', history)
    history.pop(0)

    return history


def get_updates_helper(update_seeker, installed):
    # Search installed/not installed Software Windows Updates
    search_string = "IsInstalled=%d and Type='Software'" % installed
    search_update = update_seeker.Search(search_string)

    updates = {}
    categories = []
    update_dict = {}
    # compiles the regex pattern for finding Windows Update codes
    updates_pattern = re.compile(r'KB+\d+')
    for update in search_update.Updates:
        update_str = str(update)
        # extracts Windows Update code using regex
        update_code = updates_pattern.findall(update_str)
        for category in update.Categories:
            url = "https://support.microsoft.com/en-us/kb/{}".format(
                "".join(update_code).strip("KB"))
            updates.update({update_str : url})
    return updates

def get_updates():
    wua = win32com.client.Dispatch("Microsoft.Update.Session")
    update_seeker = wua.CreateUpdateSearcher()
    available = get_updates_helper(update_seeker, installed=False)

    update = []
    website = []
    total_updates = {'Update': update,
                  'Website': website}
    for i in available:
        update.append(i)
        website.append(available[i])
    return total_updates

#This opens bitlocker in the control panel
def get_disk_encryption():
    subprocess.call(['control', '/name', 'Microsoft.BitLockerDriveEncryption'])

# This compiles a list or TCP and UDP ports and how many processes are using them
def get_open_ports():
    netstat = subprocess.check_output(['netstat','-a', '-n']).decode('utf-8')
    netstat = re.split('\r\n', netstat)
    #getting all the necessary lines
    netstat = netstat[4:]
    netstat = netstat[:len(netstat)-1]
    tcp_port = []
    udp_port = []
    #parsing the data
    for i in netstat:
        data = re.sub(r'( +)',' ' , i)
        data = re.split(' ', data)
        port = re.split(r'(.:)', data[2])
        if(data[1] == 'TCP'):
            tcp_port.append(int(port[len(port)-1]))
        else:
            udp_port.append(int(port[len(port)-1]))
    #remove duplicates and add a counter for each port used
    tcp_dict = {i:tcp_port.count(i) for i in tcp_port}
    udp_dict = {i:udp_port.count(i) for i in udp_port}
    #turn them back into a list
    tcp_port = []
    udp_port = []

    for i in tcp_dict:
        tcp_port.append([i, tcp_dict[i]])

    for i in udp_dict:
        udp_port.append([i,udp_dict[i]])

    open_ports = {
        'TCP': tcp_port,
        'UDP': udp_port,
    }
    return open_ports

# This makes a json with all of the information that was compiled from the functions above
def make_json():
    time = datetime.now()
    date_time = {'Year': time.strftime('%Y'),
                 'Month': time.strftime('%m'),
                 'Day': time.strftime('%d'),
                 'Time': time.strftime('%H:%M:%S')}
    data = {'Date': date_time,
            'Basic Info': get_basic_machine_info(),
            'Firewall': get_firewall(),
            'Screen Lock': get_screen_lock(),
            'Remote Login':get_remote_login(),
            'Wi-Fi Info':get_wifi_info(),
            'Wi-Fi History': get_wifi_history(),
            'Software': get_software_list(),
            'Startup Programs': get_startup_programs(),
            'IP Address': get_ip_addr(),
            'MAC Address': get_mac_addr(),
            'Memory': get_memory(),
            'Updates': get_updates(),
            'Open Ports': get_open_ports()}
    with open("computer_info.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

if __name__ == '__main__':
    # make_json()
    last_scanned();
