'''
Program needs: 
1) public directory to mount devices
2) usb-flash card without NTFS filesystem
'''
import os, sys, shutil, subprocess, pyudev, shlex, signal

LIBRE_PATTERN = '#LIBRARY'
LIBRE_PORT = 12345
LIBRE_ACTIVE = {}

EXCLUDED = ['.Trash-1000']      
MOUNT_DIR = '/media/usb'

SERVICE_NAME = 'automount'

DEBUG = True

if not os.path.exists(MOUNT_DIR):
    os.mkdir(MOUNT_DIR)
    os.system('chmod a+rw %s' % MOUNT_DIR)
context = pyudev.Context()

def dprint(*msg):
    if DEBUG: print(*msg)

def mount_device(device_fn, label, path=MOUNT_DIR):
    if label: path = os.path.join(path, label)
    else: dprint('[-] Label for', device_fn, 'was not found.')
    
    if not os.path.exists(path):
        os.mkdir(path)
    if len(device_fn) == 4 and device_fn.startswith('sd'):
        cmd = 'mount /dev/{} {}'.format(device_fn, path)
        os.system(cmd)
        return path
        
def remove_tree(path):
    try: shutil.rmtree(path)
    except OSError as err: dprint(err)
    
def turn_off_libre_server(name):
    proc = LIBRE_ACTIVE.get(name)
    if proc:
        proc.terminate()

def umount_device(label):
    try:
        if not label: return
        turn_off_libre_server(label)
        mounted_dir = os.pa
        th.join(MOUNT_DIR, label)
        cmd = 'umount -R {}'.format(mounted_dir)
        os.system(cmd)
        remove_tree(os.path.join(MOUNT_DIR, label))
    except OSError as err:
        dprint(err)
        
def find_libre(root_dir, target_dir=LIBRE_PATTERN):
    for item in os.listdir(root_dir): 
        itempath = os.path.join(root_dir, item)
        if not os.path.isdir(itempath) or item in EXCLUDED:
            continue
        if item == target_dir:
            return itempath
        else:
            result = find_libre(itempath)
            if result: return result
            
def start_calibre_server(path_mounted_usb, name):
    if 'calibre-server' not in os.listdir('/usr/bin'):
        raise RuntimeError('[!] "calibre-server" is not installed')
    path = find_libre(path_mounted_usb)
    if not path:
        dprint('[-] Library folder was not found')
        return
    dprint('[+] Library was found in', path)
   
    cmd = 'calibre-server -p {port} --with-library {wlib}'.format(
        port=LIBRE_PORT, wlib=path)
    proc = subprocess.Popen(shlex.split(cmd))
    if isinstance(proc, int):
        LIBRE_ACTIVE.update({name:proc})
        
def create_service():
    service_file = os.path.join(os.path.dirname(__file__), ''.join([SERVICE_NAME, '.service']))
    execstart = os.path.abspath(__file__)
    if not os.path.exists(service_file):
        dprint('[@] Creating service ...')
        os.system('touch ' + service_file)
        text = (
        '[Unit]\n'
        'Description=Content-server startup script\n'
        '[Service]\n'
        'User={user}\n'
        'ExecStart=/usr/bin/python3 {execstart}\n'
        '[Install]\n'
        'WantedBy=multi-user.target').format(
        execstart=execstart,
        user='root')
        sf = open(service_file, 'w')
        sf.write(text)
        sf.close()
        dprint('[@] Service created.')
    else:
        dprint('[+] Service exists.')
        
    symlink_path = os.path.join('/etc/systemd/system',''.join([SERVICE_NAME, '.service']))
    if not os.path.exists(symlink_path):
        os.system('ln -rs {} {}'.format(service_file, '/etc/systemd/system'))
        dprint('[@] Symlink to "/etc/systemd/system" created.')
    else:
        dprint('[+] Symlink exists.')

def check_connected_devices():
    devices = context.list_devices(subsystem='block')
    for device in devices:
        devname = device.sys_name
        devlabel = device.label
        if len(device.sysname)==4 and device.startswith('sd'):
            path = mount_device(devname, devlabel)
            start_calibre_server(path, devlabel)
                
def main():
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('block')
    for device in iter(monitor.poll, None):
        devname = device.sys_name
        if len(devname) != 4 and devname.startswith('sd'):
            continue
        devlabel = device.get('ID_FS_LABEL')
        dprint('[?] Found new usb device "%s"' % devlabel)
        if device.action == 'add':
            path = mount_device(devname, devlabel)
            if path:
                dprint('[+] "%s" is mounted' % devlabel)
                start_calibre_server(path, devlabel)
        if device.action == 'remove':
            umount_device(devlabel)
            dprint('[-] "%s" is unmounted' % devlabel)
        dprint('-'*30)
            
if __name__ == '__main__':
    create_service()
    check_connected_devices()
    main()
