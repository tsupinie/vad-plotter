# vad-plotter
Parser and plotter for NEXRAD VAD retrievals. 

The script downloads the VAD data from the NEXRAD Radar Product Dissemination page, parses the binary file, and plots the VAD retrieval as a hodograph. It also computes and displays some parameters of interest.

## Required Libraries
NumPy and Matplotlib are the only requirements to run this script.

## Usage
```
python vad.py RADAR_ID [ -m STORM_MOTION ] [ -s SFC_WIND ] [ -t TIME ]
```
* `RADAR_ID` is a 4-character radar identifier (e.g. KTLX, KFWS)
* `STORM_MOTION` is the storm motion vector. It can take one of two form. The first is either `BRM` for the Bunkers right-mover vector or `BLM` for the Bunkers left-mover vector. The second form is `DDD/SS`, where `DDD` is the direction the storm is coming from in degrees, and `SS` is the storm speed in knots. An example might be 240/35 (from the WSW at 35 kts).  If the argument is not specified, the default is to use the Bunkers right-mover vector.
* `SFC_WIND` is the surface wind vector. Its form is the same as the `DDD/SS` form of the storm motion vector. A dashed red line will be drawn on the hodograph from the lowest point in the VWP to the surface wind to indicate the approximate wind profile in that layer.
* `TIME` is the plot time. It takes the form `DD/HHMM`, where `DD` is the day, `HH` is the hour, and `MM` is the minute. The script will plot the most recent VAD as of this time.

This will produce an image file called `<RADAR_ID>_vad.png` in the current directory. An example of the output is given below.

![Example VWP Image](http://autumnsky.us/imgs/KINX_vad.png)

## Notes
When computing the parameters, in the absence of a specified surface wind, the "surface" is taken to be the lowest data point in the VWP, which is often ~100 m AGL.

The colored circles are proportional in radius to the RMS error in the VAD retrieval at each level.
