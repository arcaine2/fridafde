#!/usr/bin/env bash

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
echo -n 0 > bf_status

if [ ! -f frida-server ]; then
    echo "Frida server not found - Downloading"
    # Thanks to @viperbjk =)
    VERSION=`pip3 show frida | grep 'Version: ' | awk '{print $2}'`
    wget https://github.com/frida/frida/releases/download/$VERSION/frida-server-$VERSION-android-arm64.xz
    xz -d frida-server-$VERSION-android-arm64.xz
    mv frida-server-$VERSION-android-arm64 frida-server
fi

CHECKSTATUS=$(frida-ps -U)
if [[ ${CHECKSTATUS} == *"Failed"* ]];then
	echo "FRiDA not running - Starting"
    adb push frida-server /data/local/tmp
	adb shell chmod +x /data/local/tmp/frida-server
	adb shell ./data/local/tmp/frida-server &
	sleep 2
fi  

echo "FRiDA Server running on Device. Do we have Cryptkeeper?"
frida-ps -U | grep Crypt
echo "Starting screen..."
adb shell input keyevent 26    
adb shell input swipe 1240 1000 1240 10
echo "IMPORTANT: Open two terminals. First run 'python3 hooking-vold.py' and then 'python3 hooking-mount.py'"

sleep 1

if [ "$1" == "-r" ]; then
    # Force restart related options, keep as is
    while [ ! -f bf_status ] 
    do sleep 1; done

    while ! grep "1" bf_status
    do sleep 1; done

    echo "> Found restart flag, restarting the script!"

    ./$(basename $0) "$1" && exit 0
fi