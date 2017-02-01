# vad-plotter
Parser and plotter for NEXRAD VAD retrievals. 

The script downloads the VAD data from the NEXRAD Radar Product Dissemination page, parses the binary file, and plots the VAD retrieval as a hodograph. It also computes and displays some parameters of interest.

## Required Libraries
NumPy and Matplotlib are the only requirements to run this script.

## Usage
```
python vad.py RADAR_ID [ -m STORM_MOTION ] [ -s SFC_WIND ] [ -t TIME ] [ -f IMG_NAME ] [ -p LOCAL_PATH ]
```
* `RADAR_ID` is a 4-character radar identifier (e.g. KTLX, KFWS)
* `STORM_MOTION` is the storm motion vector. It can take one of two form. The first is either `BRM` for the Bunkers right-mover vector or `BLM` for the Bunkers left-mover vector. The second form is `DDD/SS`, where `DDD` is the direction the storm is coming from in degrees, and `SS` is the storm speed in knots. An example might be 240/35 (from the WSW at 35 kts).  If the argument is not specified, the default is to use the Bunkers right-mover vector.
* `SFC_WIND` is the surface wind vector. Its form is the same as the `DDD/SS` form of the storm motion vector. A dashed red line will be drawn on the hodograph from the lowest point in the VWP to the surface wind to indicate the approximate wind profile in that layer.
* `TIME` is the plot time. It takes the form `[YYYY-mm-]dd/HHMM`, where `YYYY` is the 4-digit year, `mm` is the month, `dd` is the day, `HH` is the hour, and `MM` is the minute. The year and month are optional. The script will plot the most recent VAD as of this time.
* `IMG_NAME` is the name of the image the script produces. If not given, it defaults to `<RADAR_ID>_vad.png`.
* `LOCAL_PATH` is the path to a local file from which to load the VWP data (assumed to have been downloaded from [NCDC's NEXRAD archive](https://www.ncdc.noaa.gov/has/HAS.FileAppRouter?datasetname=7000&subqueryby=STATION&applname=&outdest=FILE)). The name of the file should not be given; the script will construct the file name using the other information.

An example of the output is given below. See the [interpretation](#interpretation) section for more information.

![Example VWP Image](http://autumnsky.us/imgs/KINX_vad.png)

## Interpretation
A "hodograph" is a graph of wind as a function of height. The *u* component of the wind is on the *x* axis and the *v* component of wind is on the *y* axis. Area on the hodograph is proportional to helicity, an important parameter in severe convective storm forecasting.

The colors denote different height layers, and follow the Storm Prediction Center's convention for their hodographs: red denotes the 0-3 km layer, light green denotes the 3-6 km layer, dark green denotes the 6-9 km layer, purple denotes the 9-12 km layer, and cyan denotes the layer from 12 km on up. The colored circles are proportional in radius to the RMS error in the VAD retrieval at each level.

When computing the parameters, in the absence of a specified surface wind, the "surface" is taken to be the lowest data point in the VWP, which is often ~100 m AGL.
