From Leon Turner:


Hi All, I've been playing around a bit in Python with Astropy etc (with lots of help from ChatGPT). 
I wanted to create a tool for those of us who aren't ready to switch to EQ mode yet, that allows us to get a bit of a clearer idea of what the field rotation for a given object might be (rather than just "good high in east and west"!). 
I've used the maths from here: https://calgary.rasc.ca/field_rotation.htm.
The program comes as a Jupyter notebook (I find VS code is nice to work with them), but would be easy enough to adapt to stand alone Python I guess. You'll need to install Astropy and Astroquery (since we get the data from Simbad for the objects) - this is not tricky though.
The basic idea is that you define your location, the start date of the observation and the object you want to track, e.g. M31 for Andromeda Galaxy. You get back a plot of the object over the next 24 hours shown over a contour plot of the field rotation (note I've taken the magnitude of the field rotation, it's actually positive in the north and negative in the south). 
You also get a table of hourly observation times, with the field rotation given. So, in my example for M31, you can see a good time for this observer is starting around 7pm for a couple of hours, as we're well in the green there.
Next I think I'll do an animation of how the field rotation changes with latitude.
Anyway, not strictly an unconventional use, but maybe interesting for people to learn a bit about the powerful open source astro tools we have, so hopefully useful!


Here are the notebooks for the field rotation.
Here's the animation of field rotation, as we go from the equator to the north pole