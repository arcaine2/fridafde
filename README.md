# FRiDA FDE bruteforce

Here's a small write-up on how to use FRiDA to bruteforce Secure Startup with FDE-encryption on a Samsung G935F running Android 8.

![ExampleImage](/fde_example.png?raw=true "Title")

FRiDA requires a rooted device (or FRiDA injected into a specific process). I won't go into details on how to accomplish this, just google ENG-ROOT or Magisk and you will probably
find a rooting solution that works for you. I've also included a small script to upload and start FRiDA on the connected device: startFrida.sh.

First of all, what are we doing? And why are we doing this? What I wanted to do is find a way of testing codes without hitting the limit of maximum password attempts. If the maximum attempt value is reached, the device will reboot and wipe. So my first step was to find out the processes or functions that managed all this.

From reading Android source and using Objection (another great tool) I soon figured out that  "android.os.storage.IStorageManager::decryptStorage" running in the process "com.android.settings:CryptKeeper" was the target for my FRiDA-script. I also knew from before that Vold is involved in the process of verifying and updating the crypto footer.
After some fiddling with Radare2 and FRiDA, I came to the conclusion that by replacing the "footer_put" function in Vold I could try codes and keep the counter at the original value.

Included are two different Python scripts:

The file "hooking-vold.py" replaces "footer_put" in Vold.
The file "hooking-mount.py" creates the RPC we use from the python script to try the different codes.

We need to run files at the same time, in two different terminals.

How to use it:

1. Run "startFrida.sh" to upload and start FRiDA server on your connected device.
2. Run "python3 hooking-vold.py" in a separate terminal.
3. Run "python3 hooking-mount.py" in main terminal.
4. Sometimes when the correct code is found, the process hangs the device. Just issue "adb reboot" to restart secure startup and then enter the correct code.

# UPDATE:

After some testing it turned out that script crashes after almost 12000 attempts, and slowing down after ~5000, at least on S7 Edge. Rewrote part of the script, adding some new features, like:

* custom PIN option supporting any range, any length. Entering 0000 to 999999 for example will check all 6 digits codes, even though start PIN is 4 digits long. Max range length is always used here!
* auto-restart option to reboot the phone automatically after set tests done, and continue bruteforcing from there. Run startFrida.sh as well as hooking-mount.py with -r flag. It's also possible to set after how many tests phone will reboot. For example, "python3 hooking-mount.py -r 5000" will restart the device after 5000 codes tested (10000 is the default one)
* test if hooking-vold.py is running and/or was restarted along with the phone. It's being done by checking content of bf_status file.
* a bit more graceful exit once the passcode is found, with correct passcode more visible and saved into a FOUND.txt file. Script still crashes, but right after code is found instead of keep going for a longer while as before.

![](/fridafde_updated.png)

How to use it (normal way):

1. Run "startFrida.sh" to upload and start FRiDA server on your connected device.
2. Run "python3 hooking-vold.py" in a separate terminal.
3. Run "python3 hooking-mount.py" in main terminal.
4. Sometimes when the correct code is found, the process hangs the device. Just issue "adb reboot" to restart secure startup and then enter the correct code.

How to use it (with auto-restart enabled):

1. Run "startFrida.sh -r" to upload and start FRiDA server on your connected device and wait for restart signal
2. Run "python3 hooking-vold.py" in a second terminal.
3. Run "python3 hooking-mount.py -r" or "python3 hooking-mount.py -r <number_of_tests_before_restart>" in third terminal.
4. Sometimes when the correct code is found, the process hangs the device. Just issue "adb reboot" to restart secure startup and then enter the correct code.
5. Passcode will be saved in FOUND.txt

##

Modified code from https://github.com/Magpol/fridafde  
Credits to Magpol  
Author: Arcain 
