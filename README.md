## seestar_run.md

**Version:** 1.0a1

**Tested Firmware:** 2.25

**Overview:**

This document details `seestar_run`, a companion application for the Seestar mobile app, written on python to be used in most modern OS. It showcases programmatic control of the Seestar S50, enabling tasks like:

* Mosaic captures
* Night session planning
* Custom target capture
* Spectral image capture over extended frames

**Requirements:**

* Seestar with completed calibration steps (horizontal, dark frame, leveling)
* computer/laptop with Python installed (e.g. [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/))

**Usage:**

1. **Setup:** Ensure Seestar calibration is complete.
2. **Install Python:** Follow the link above if not already installed.
3. **Run Commands:** Use PowerShell for Windows or python in other OS and run the following command:

```
python seestar_run.py <ip_address> <target_name> <ra> <dec> <is_use_LP_filter> <session_time> <RA panel size> <Dec panel size> <RA offset factor> <Dec offset factor>
```

**Parameters:**

* **ip_address:** Seestar's IP address (found in "Advanced Feature -> RTSP Address").
* **target_name:** Target name. During mosaics, saved format is `<target_name>_<RA_panel_num>_<Dec_panel_num>`.
* **ra:** Target's RA value. If negative, uses current Sky Atlas location.
* **dec:** Target's Dec value.
* **is_use_LP_filter:** Set to 1 for light pollution filter usage.
* **session_time:** Capture session duration per panel in seconds (not integration time).
* **RA and Dec panel size:** Number of panels in a mosaic.
* **RA and Dec offset factors:** Distance between mosaic panels, lower values will have more overlaps

**Examples:**

* **Custom target capture:**

```
python seestar_run.py 192.168.110.30 'Castor_Kai' 7.602 31.83 0 60 1 1 1 1
```

* **Mosaic capture:**

```
python seestar_run.py 192.168.110.30 'Castor_Kai' 7.602 31.83 0 60 2 3 1.2 1.1
```

* **Multiple target capture:** Create a batch file with multiple command lines using the above format.
* **Night session planning:** Use sleep commands in a batch file to schedule captures.
* **External target setting:**

    1. Set the target using Seestar App, Stellarium, or other tools.
    2. Use a negative value for `<ra>` in the `seestar_run` command:

```
python seestar_run.py 192.168.110.30 'Castor' -1.0 -1.0 0 60 1 1 1 1
```

**Feedback:**

Please report bugs and share feedback on the this github repo or in the Discord channel:

[https://discord.com/channels/1204838310841815040/1207422275960176650](https://discord.com/channels/1204838310841815040/1207422275960176650)

**Enjoy and good luck!**
