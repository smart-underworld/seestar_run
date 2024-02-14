seestar_run
version 1.0a1

Tested with Seestar Firmware version: 2.25

-------------

This is an example app that will serve as a companion app with the Seestar mobile app. It is compiled for Windows OS.

The goal is to demostrate how one can control the Seestar S50 programmatically. Example of its uses are:

1) Mosaic Capture
2) Night Session Capture Planning
3) Custom Target Capture
4) Spectral Image Capture over Extended Frames

-----------------------------

How to use it:

0) Setup your Seestar normally, with Horizontal Calbration, Dark Frame Calbraion and/or Leveling completed
1) With your Windows computer/laptop, install Python for Windows: https://www.python.org/downloads/windows/
2) in Powershell, run the following

python seestar_run.py <ip_address> <target_name> <ra> <dec> <is_use_LP_filter> <session_time> <RA panel size> <Dec panel size> <RA offset factor> <Dec offset factor>

ip_address:
    The ip address of your seestar. Find it under Advanced Feature -> RTSP Address
target_name:
    Name of your target. If doing mosaic, the name will be saved in format <target_name>_<RA_panel_num>_<Dec_panel_num>
ra: 
    RA value of the target. if RA is < 0, then the app will use the current location of the Sky Atlas
dec:
    Dec value of the target
is_use_LP_filter:
    1 if you want to use the Light Pollution Filter for your captures
session_time: 
    how long a capture session will last for each panel. Note this is not integration time because there will be rejected frames.
RA and Dec panel size: 
    determines how many panels in a mosaic
RA and Dec offset factors:
    determine how far apart are each panel in a mosaic

-----------------------------

Examples:

To catpure a custom target with specific target name and location:
python seestar_run.py 192.168.110.30 'Castor_Kai' 7.602 31.83 0 60 1 1 1 1

To capture a mosaic of a target:
python seestar_run.py 192.168.110.30 'Castor_Kai' 7.602 31.83 0 60 2 3 1.2 1.1

To capture multiple targets in sequence:
create a batch file and enter multiple lines of the commands described above

To do night session planning:
you can add a sleep command in the batch file to wait for specific amount of time before/between captures

To use external tool to set target:
    1) Use Seestar App, Stellarium, or other apps to move the Seestar to the desired target
    2) With the seestar_run command, enter a negative number for <ra>
       example: python seestar_run.py 192.168.110.30 'Castor' -1.0 -1.0 0 60 1 1 1 1


Enjoy, and good luck.

Please give bug reports and feedback in the Discord Channel:

https://discord.com/channels/1204838310841815040/1207422275960176650




