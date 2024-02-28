# Conversion 4
from astropy.coordinates import SkyCoord, FK5, FK4, Angle, ICRS
from astropy.time import Time
import astropy.units as u
from datetime import datetime
import re
import tkinter as tk

# This program performs coordinate transformations.
# The option is to transform epoch J2000 to epoch on date (JNow) and vice versa
# The window shows both decimal (1.25, 40.5) values as well the HMSDMS (1:15:00 40:30:00) values for both epochs
# Especially useful when the telescope use needs JNow and the reference data is J2000
# 20240221 Jari Backman, 'jabamula', jari@sinijari.fi
# version 1.0.1

version = "1.0.1"

def show_error_popup(invalid_input):
    error_window = tk.Toplevel(root)
    error_window.title("Input Error")
    message = f"Invalid Input: \"{invalid_input}\".\nPlease enter coordinates in Decimal (1.23, 2.34) or HMSDMS (1:14:50.3 2:34:12.3) format."
    tk.Label(error_window, text=message).pack(pady=10, padx=10)
    tk.Button(error_window, text="OK", command=error_window.destroy).pack(pady=5)

def validate_inputs(coords_list):
    # Regex patterns for decimal and HMSDMS formats
    decimal_pattern = re.compile(r'^-?\d+(\.\d+)?, -?\d+(\.\d+)?$')
    hmsdms_pattern = re.compile(r'^-?\d+:\d+:\d+(\.\d+)?\s+-?\d+:\d+:\d+(\.\d+)?$')
    
    for coord in coords_list:
        if coord:  # Check only if the input field is not empty
            if not (decimal_pattern.match(coord) or hmsdms_pattern.match(coord)):
                show_error_popup(coord)
                return False
    return True


def convert_coordinates():
    # Get the input values from the GUI
    j2000_decimal = input_entries[0].get()
    j2000_hmsdms = input_entries[1].get()
    jnow_decimal = input_entries[2].get()
    jnow_hmsdms = input_entries[3].get()
    
    # Validate all inputs
    inputs = [j2000_decimal, j2000_hmsdms, jnow_decimal, jnow_hmsdms]
    if not validate_inputs(inputs):
        return  # Exit the function if any input is invalid

    # today
    tm = datetime.now()
    
    # decimal J2000
    # J2000 coordinates
    if j2000_decimal != "" or j2000_hmsdms != "":
        J2k = 1    
        if j2000_decimal != "":
            radi, decdi = map(float, j2000_decimal.strip('()').split(','))
        elif j2000_hmsdms != "":
            inCoords = j2000_hmsdms
            c = SkyCoord([inCoords, inCoords.replace(":", " ")], frame='icrs', unit=(u.hourangle, u.deg))
            radi = c.ra.hour[0]
            decdi = c.dec.deg[0]

        j2000 = SkyCoord(radi, decdi, unit=(u.hourangle, u.deg))

    # JNow coordinates
    elif jnow_decimal != "" or jnow_hmsdms != "":
        J2k = 0    
        if jnow_decimal != "":
            rani, decni = map(float, jnow_decimal.strip('()').split(','))
        elif jnow_hmsdms != "":
            inCoords = jnow_hmsdms
            c = SkyCoord([inCoords, inCoords.replace(":", " ")], frame='icrs', unit=(u.hourangle, u.deg))
            rani = c.ra.hour[0]
            decni = c.dec.deg[0]

        jNow = SkyCoord(rani, decni, unit=(u.hourangle, u.deg), frame=FK5(equinox=tm))

    # The logic (Conversion)
    # J2000 to Jnow
    if J2k == 1:
        jNow = j2000.transform_to(FK5(equinox=tm))  # precess to JNow
    # JNow to J2000
    else:
        j2000 = jNow.transform_to(FK5(equinox="J2000"))
          
    rado = j2000.ra.hour
    decdo = j2000.dec.deg  
    rano = jNow.ra.hour
    decno = jNow.dec.deg  

            # J2000 output
    if J2k == 1:
        ra = radi
        dec = decdi
        j2000_dec = f"{ra:.4f}, {dec:.4f}"
        j2000_hmsdms = f"{j2000.ra.hms.h:02.0f}:{j2000.ra.hms.m:02.0f}:{j2000.ra.hms.s:02.0f} {j2000.dec.dms.d:02.0f}:{abs(j2000.dec.dms.m):02.0f}:{abs(j2000.dec.dms.s):02.0f}"
    else:
        ra = rado
        dec = decdo
        j2000_dec = f"{ra:.4f}, {dec:.4f}"
        j2000_hmsdms = f"{j2000.ra.hms.h:02.0f}:{j2000.ra.hms.m:02.0f}:{j2000.ra.hms.s:02.0f} {j2000.dec.dms.d:02.0f}:{abs(j2000.dec.dms.m):02.0f}:{abs(j2000.dec.dms.s):02.0f}"

    # JNow output
    if J2k == 1:
        ra = rano
        dec = decno
        outCoords = jNow.to_string('hmsdms').replace("h", ":").replace("d", ":").replace("m", ":").replace("s", "")
        outCoords = f"{jNow.ra.hms.h:02.0f}:{jNow.ra.hms.m:02.0f}:{jNow.ra.hms.s:02.0f} {jNow.dec.dms.d:02.0f}:{abs(jNow.dec.dms.m):02.0f}:{abs(jNow.dec.dms.s):02.0f}"
        jnow_hmsdms = outCoords 
        jnow_dec = f"{ra:.4f}, {dec:.4f}"
    else:
        ra = rani
        dec = decni
        jnow_dec = f"{ra:.4f}, {dec:.4f}"
        jnow_hmsdms = f"{jNow.ra.hms.h:02.0f}:{jNow.ra.hms.m:02.0f}:{jNow.ra.hms.s:02.0f} {jNow.dec.dms.d:02.0f}:{abs(jNow.dec.dms.m):02.0f}:{abs(jNow.dec.dms.s):02.0f}"

    # Update the output labels with the results
    outputs["J2000 Decimal"].config(text=j2000_dec)
    outputs["J2000 HMSDMS"].config(text=j2000_hmsdms)
    outputs["JNow Decimal"].config(text=jnow_dec)
    outputs["JNow HMSDMS"].config(text=jnow_hmsdms)
    
# Create the main window
def disable_other_entries(event, entry_set):
    for entry in entry_set:
        if entry.get() and entry is not event.widget:
            entry.configure(state='disabled')

def reset_fields():
    for entry in input_entries:
        entry.delete(0, tk.END)
        entry.configure(state='normal')

# Initialize the main window
root = tk.Tk()
root.title("Coordinate Converter J2000 vs JNow")

pad_x = 10
pad_y = 5

# Create the input frame
input_frame = tk.LabelFrame(root, text="INPUT", font=('Arial', 16))
input_frame.pack(padx=pad_x, pady=pad_y, fill="x")

# Grid configuration for input frame
labels = ["J2000 Decimal", "J2000 HMSDMS", "JNow Decimal", "JNow HMSDMS"]
for i, label_text in enumerate(labels):
    tk.Label(input_frame, text=label_text).grid(row=0, column=i, padx=pad_x, pady=pad_y)

# Input entry fields
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

# Add version label above the buttons
version_label = tk.Label(input_frame, text="Version 1.0.1")
version_label.grid(row=2, columnspan=len(labels) + 2, pady=pad_y)

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

# Developer info at the bottom right corner
developer_label = tk.Label(root, text="jabamula/2024", anchor="e")
developer_label.pack(side="bottom", fill="x")

# Make the columns in all grids resizable
for i in range(len(labels)):
    input_frame.columnconfigure(i, weight=1)
    output_frame.columnconfigure(i, weight=1)

# Run the main loop
root.mainloop()
