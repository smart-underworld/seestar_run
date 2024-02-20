from astropy.coordinates import SkyCoord, FK5, FK4, Angle, ICRS
from astropy.time import Time
import astropy.units as u
from datetime import datetime
import re
import tkinter as tk

# This program performs coordinate transformations.
# The option is to transform epoch J2000 to epoch on date (JNow) and vice versa
# The window shows both decimal (1.25, 40.5) values as well the HMSDMS (1:15:00 40:30:00) values for both epochs
# Especially useful when the telescope uses JNow and reference data J2000
# 20240221 Jari Backman, 'jabamula', jari@sinijari.fi

def convert_coordinates():
    # Get the input values from the GUI
    #dec_input = dec_entry.get()
    #hmsdms_input = hmsdms_entry.get()
    j2000_decimal = input_entries[0].get()
    j2000_hmsdms = input_entries[1].get()
    jnow_decimal = input_entries[2].get()
    jnow_hmsdms = input_entries[3].get()

    # today
    tm = datetime.now()
    
    # decimal J2000
    if j2000_decimal != "": 
        J2k = 1
        ra, dec = map(float, j2000_decimal.strip('()').split(','))
        coin = ICRS(ra*u.hour, dec*u.degree)
        inCoords = str(coin.ra/15) + ' ' + str(coin.dec)
        inCoords = inCoords.replace('d', ':').replace('m',':').replace('s', '')
        j2000 = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
    # hmsdms J2000    
    elif j2000_hmsdms != "":
        J2k = 1
        inCoords = j2000_hmsdms
        J2000coords = [inCoords, inCoords.replace(":"," ")]
        c = SkyCoord(J2000coords, frame='icrs', unit=(u.hourangle, u.deg))
        ra = c.ra.hour[0]
        dec = c.dec.deg[0]
        j2000 = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
    # decimal JNow
    elif jnow_decimal != "":
        J2k = 0
        ra, dec = map(float, jnow_decimal.strip('()').split(','))
        coin = ICRS(ra*u.hour, dec*u.degree)
        inCoords = str(coin.ra/15) + ' ' + str(coin.dec)
        inCoords = inCoords.replace('d', ':').replace('m',':').replace('s', '')
        jNow = SkyCoord(ra, dec, unit=(u.hourangle, u.deg), frame=FK5(equinox=tm))
    # hmsdms JNow    
    else:
        J2k = 0
        inCoords = jnow_hmsdms
        jNow = [inCoords, inCoords.replace(":"," ")]
        c = SkyCoord(jNow, frame='icrs', unit=(u.hourangle, u.deg))
        ra = c.ra.hour[0]
        dec = c.dec.deg[0]
        jNow = SkyCoord(ra, dec, unit=(u.hourangle, u.deg), frame=FK5(equinox=tm))      

    # The logic (Conversion)
    # J2000 to Jnow
    if J2k == 1:
        jNow = j2000.transform_to(FK5(equinox=tm))  # precess to JNow
    # JNow to J2000
    else:
        j2000 = jNow.transform_to(FK5(equinox="J2000"))
          
    # J2000 output
    if J2k == 1:
        j2000_dec = str("%0.4f" % ra) + ", " + str("%0.4f" % dec)
        j2000_hmsdms = inCoords
    else:
        outCoords = j2000.to_string('hmsdms').replace("h", ":").replace("d", ":").replace("m", ":").replace("s", "")
        outCoords = f"{j2000.ra.hms.h:02.0f}{':'}{j2000.ra.hms.m:02.0f}{':'}{j2000.ra.hms.s:05.2f} {j2000.dec.dms.d:02.0f}{':'}{abs(j2000.dec.dms.m):02.0f}{':'}{abs(j2000.dec.dms.s):05.2f}"
        j2000_hmsdms = outCoords 
        ra_N = j2000.ra.hour
        dec_N = j2000.dec.deg  
        j2000_dec =  str("%0.4f" % ra_N) + ", " + str("%0.4f" % dec_N)

    # JNow output
    if J2k == 1:
        outCoords = jNow.to_string('hmsdms').replace("h", ":").replace("d", ":").replace("m", ":").replace("s", "")
        outCoords = f"{jNow.ra.hms.h:02.0f}{':'}{jNow.ra.hms.m:02.0f}{':'}{jNow.ra.hms.s:05.2f} {jNow.dec.dms.d:02.0f}{':'}{abs(jNow.dec.dms.m):02.0f}{':'}{abs(jNow.dec.dms.s):05.2f}"
        jnow_hmsdms = outCoords 
        ra_N = jNow.ra.hour
        dec_N = jNow.dec.deg  
        jnow_dec =  str("%0.4f" % ra_N) + ", " + str("%0.4f" % dec_N)
    else:
        jnow_dec = str("%0.4f" % ra) + ", " + str("%0.4f" % dec)
        jnow_hmsdms = inCoords
 
    # Update the output labels with the results
    outputs["J2000 Decimal"].config(text=j2000_dec)
    outputs["J2000 HMSDMS"].config(text=j2000_hmsdms)
    outputs["JNow Decimal"].config(text=jnow_dec)
    outputs["JNow HMSDMS"].config(text=jnow_hmsdms)

# Create the main window
root = tk.Tk()
root.title("Coordinate Converter J2000 vs JNow")

def disable_other_entries(event, entry_set):
    for entry in entry_set:
        if entry.get() and entry is not event.widget:
            entry.configure(state='disabled')

def reset_fields():
    # Clear all entries
    for entry in input_entries:
        entry.delete(0, tk.END)
        entry.configure(state='normal')  # Re-enable the entry

    # Clear all outputs
    for label in outputs.values():
        label.config(text="N/A")

# Define the padding
pad_x = 10
pad_y = 5

# Create the input frame
input_frame = tk.LabelFrame(root, text="INPUT", font=('Arial', 16))
input_frame.pack(padx=pad_x, pady=pad_y, fill="x")

# Grid configuration for input frame
labels = ["J2000 Decimal", "J2000 HMSDMS", "JNow Decimal", "JNow HMSDMS"]
for i, label_text in enumerate(labels):
    tk.Label(input_frame, text=label_text).grid(row=0, column=i, padx=pad_x, pady=pad_y)

# Define and place input entry fields
input_entries = []
for i in range(len(labels)):
    entry = tk.Entry(input_frame)
    entry.grid(row=1, column=i, padx=pad_x, pady=pad_y, sticky="ew")
    entry.bind("<FocusOut>", lambda event, e=entry: disable_other_entries(event, input_entries))
    input_entries.append(entry)

# Convert and Reset buttons
convert_button = tk.Button(input_frame, text="Convert", command=convert_coordinates)
convert_button.grid(row=1, column=len(labels), padx=pad_x, pady=pad_y, sticky="ew")
reset_button = tk.Button(input_frame, text="Reset", command=reset_fields)
reset_button.grid(row=1, column=len(labels)+1, padx=pad_x, pady=pad_y, sticky="ew")

# Create the output frame
output_frame = tk.Frame(root)
output_frame.pack(padx=pad_x, pady=pad_y, fill="x")

# Output labels and configuration
output_labels = ["J2000 Decimal", "J2000 HMSDMS", "JNow Decimal", "JNow HMSDMS"]
outputs = {}
for i, label_text in enumerate(output_labels):
    tk.Label(output_frame, text=label_text, font=('Arial', 10)).grid(row=i, column=0, padx=pad_x, pady=0, sticky="ew")
    output = tk.Label(output_frame, text="N/A", relief="sunken")
    output.grid(row=i, column=1, padx=pad_x, pady=pad_y, sticky="ew")
    outputs[label_text] = output

# Make the columns in all grids resizable
for i in range(len(labels)):
    input_frame.columnconfigure(i, weight=1)
    output_frame.columnconfigure(i, weight=1)

# Run the main loop
root.mainloop()
