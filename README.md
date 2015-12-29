# vad-plotter
Parser and plotter for NEXRAD VAD retrievals. 

The script downloads the VAD data from the NEXRAD Radar Product Dissemination page, parses the binary file, and plots the VAD retrieval as a hodograph. It also computes and displays some parameters of interest.

## Usage
```
python vad.py RADAR_ID STORM_MOTION [RADAR_ID STORM_MOTION ...]
```
* `RADAR_ID` is a 4-character radar identifier (e.g. KTLX, KFWS)
* `STORM_MOTION` is the storm motion vector. It takes the form `DDD/SS`, where `DDD` is the direction the storm is coming from in degrees, and `SS` is the storm speed in knots.

This will produce an image file called `<RADAR_ID>_vad.png` in the current directory.

## Required Libraries
NumPy and Matplotlib are the only requirements to run this script.

## Notes
When computing the parameters, the "surface" is taken to be the lowest data point in the VAD retrieval, which is often ~100 m AGL.

The colored circles are proportional in radius to the RMS error in the VAD retrieval at each level.
