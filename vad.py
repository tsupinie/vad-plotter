

import numpy as np

import sys

from vad_reader import download_vad
from params import compute_parameters
from plot import plot_hodograph

import re
import argparse

"""
plot_vad.py
Author:     Tim Supinie (tsupinie@ou.edu)
Completed:  May 2012
Modified:   26 April 2015
                Fixed SRH calculations.
            28 December 2015
                Migrated to its own package, ravamped plot, fixed SRH calculations for real this time.
Usage:
            vad.py RADAR_ID -m STORM_MOTION [ -s SFC_WIND ]

RADAR_ID is the 4-character identifier for the radar (e.g. KTLX, KFWS, etc.). 
STORM_MOTION takes the form DDD/SS, where DDD is the direction the storm is coming from, and SS is the speed in knots (e.g. 240/25)."
SFC_WIND takes the form DDD/SS, where DDD is the direction the surface wind is coming from, and SS is the speed in knots (e.g. 160/10)."
"""

def is_vector(vec_str):
    return bool(re.match(r"[\d]{3}/[\d]{2}", vec_str))

def parse_vector(vec_str):
    return tuple(int(v) for v in vec_str.strip().split("/"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('radar_id', help="The 4-character identifier for the radar (e.g. KTLX, KFWS, etc.)")
    ap.add_argument('-m', dest='storm_motion', help="Storm motion vector. It takes the form DDD/SS, where DDD is the direction the storm is coming from, and SS is the speed in knots (e.g. 240/25).", required=True)
    ap.add_argument('-s', dest='sfc_wind', help="Surface wind vector. It takes the form DDD/SS, where DDD is the direction the storm is coming from, and SS is the speed in knots (e.g. 240/25).")
    args = ap.parse_args()

    np.seterr(all='ignore')

    smv = parse_vector(args.storm_motion)
    print "Plotting VAD for %s ..." % args.radar_id
    vad = download_vad(args.radar_id)
    print "Valid time:", vad['time'].strftime("%d %B %Y %H%M:%S UTC")

    if args.sfc_wind:
        sfc_wind = parse_vector(args.sfc_wind)
        vad.add_surface_wind(sfc_wind)

    params = compute_parameters(vad, smv)
    plot_hodograph(vad, params, smv)

if __name__ == "__main__":
    main()
