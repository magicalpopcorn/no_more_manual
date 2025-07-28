Main Capabilities of ADB
## 1. Device Control & Input Simulation
Send taps, swipes, key events, and type text.

    adb shell input tap x y
    adb shell input swipe x1 y1 x2 y2 [duration]
    adb shell input text "Hello"
    adb shell input keyevent 3  # Home button
## 2. File Transfer
Move files between host and Android device.

    adb push localfile /sdcard/
    adb pull /sdcard/remote_file.txt .
## 3. App Management
Install, uninstall, start, or force-stop apps.

    adb install myapp.apk
    adb uninstall com.example.myapp
    adb shell am start -n com.example.myapp/.MainActivity
    adb shell am force-stop com.example.myapp

##  4. Capture Output/Response
Run shell commands and get text/data back.

    adb shell getprop      # Get system properties
    adb shell ls /sdcard/  # List files, will print result
    adb shell dumpsys      # System info dumps
    adb shell settings get system screen_brightness
## 5. Take Screenshots & Record Video
Pull screenshots, images, or screen recordings for use on the host.

    adb exec-out screencap -p > screenshot.png
    adb shell screenrecord /sdcard/demo.mp4
    adb pull /sdcard/demo.mp4 .
## 6. Read Logs
Get logcat output for debugging or detecting in-app messages.

    adb logcat

## 7. Query Package and Activity Info
Find out what’s installed, what’s running, and get metadata.

    adb shell pm list packages
    adb shell dumpsys window windows
    adb shell dumpsys activity top

## 8. Forward Network Ports
Forward ports between device and host for debugging web or API traffic.

    adb forward tcp:8000 tcp:8000

## 9. List all services
    adb devices

## Connect to ADB
    $ netstat -aon | findstr LISTEN
    TCP    0.0.0.0:5555           0.0.0.0:0              LISTENING       20352

    $ adb connect 127.0.0.1:5555


# ldconsole

## Launch
    ldconsole.exe launch --index <index>