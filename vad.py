

import numpy as np

import sys

from vad_reader import download_vad
from params import compute_parameters
from plot import plot_hodograph

"""
plot_vad.py
Author:     Tim Supinie (tsupinie@ou.edu)
Completed:  May 2012
Modified:   26 April 2015
                Fixed SRH calculations.
Usage:
            vad.py RADAR_ID STORM_MOTION [ RADAR_ID STORM_MOTION ... ]

RADAR_ID is the 4-character identifier for the radar (e.g. KTLX, KFWS, etc.). 
STORM_MOTION takes the form DDD/SS, where DDD is the direction the storm is coming from, and SS is the speed in knots (e.g. 240/25)."
"""

def main():
    usage = """
Usage:
            vad.py RADAR_ID STORM_MOTION [ RADAR_ID STORM_MOTION ... ]

RADAR_ID is the 4-character identifier for the radar (e.g. KTLX, KFWS, etc.). 
STORM_MOTION takes the form DDD/SS, where DDD is the direction the storm is coming from, and SS is the speed in knots (e.g. 240/25)."
"""
    if len(sys.argv) > 1 and len(sys.argv) % 2 == 1:
        try:
            radar_ids = sys.argv[1::2]
            storm_motions = sys.argv[2::2]

            storm_dir, storm_spd = zip(*[ tuple(int(v) for v in m.split("/")) for m in storm_motions ])
        except:
            print usage
            sys.exit()
    else:
        print usage
        sys.exit()

    np.seterr(all='ignore')

    for rid, sd, ss in zip(radar_ids, storm_dir, storm_spd):
        print "Plotting VAD for %s ..." % rid
        vad = download_vad(rid)
        params = compute_parameters(vad, (sd, ss))
        plot_hodograph(vad, params, (sd, ss))

if __name__ == "__main__":
    main()
