
import struct
from datetime import datetime, timedelta
import urllib2

import numpy as np

import sys

import matplotlib
matplotlib.use('agg')
import pylab
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox
from matplotlib.transforms import TransformedBbox

"""
plot_vad.py
Author:     Tim Supinie (tsupinie@ou.edu)
Completed:  May 2012
Modified:   26 April 2015
                Fixed SRH calculations.
Usage:
            plot_vad.py RADAR_ID STORM_MOTION [ RADAR_ID STORM_MOTION ... ]

RADAR_ID is the 4-character identifier for the radar (e.g. KTLX, KFWS, etc.). 
STORM_MOTION takes the form DDD/SS, where DDD is the direction the storm is coming from, and SS is the speed in knots (e.g. 240/25)."
"""

class VADFile(object):
    def __init__(self, file):
        self._rpg = file

        self._readHeaders()
        has_symbology_block, has_graphic_block, has_tabular_block = self._readProductDescriptionBlock()

        if has_symbology_block:
            self._readProductSymbologyBlock()

        if has_graphic_block:
            pass

        if has_tabular_block:
            self._readTabularBlock()
        return

    def _readHeaders(self):
        wmo_header = self._read('s30')

        message_code = self._read('h')
        message_date = self._read('h')
        message_time = self._read('i')
        message_length = self._read('i')
        source_id = self._read('h')
        dest_id = self._read('h')
        num_blocks = self._read('h')

        return

    def _readProductDescriptionBlock(self):
        self._read('h') # Block separator
        self._radar_latitude  = self._read('i') / 1000.
        self._radar_longiutde = self._read('i') / 1000.
        self._radar_elevation = self._read('h')

        product_code = self._read('h')
        if product_code != 48:
            print "This isn't a VAD file."

        operational_mode    = self._read('h')
        self._vcp           = self._read('h')
        req_sequence_number = self._read('h')
        vol_sequence_number = self._read('h')

        scan_date    = self._read('h')
        scan_time    = self._read('i')
        product_date = self._read('h')
        product_time = self._read('i')

        self._read('h')      # Product-dependent variable 1 (unused)
        self._read('h')      # Product-dependent variable 2 (unused)
        self._read('h')      # Elevation (unused)
        self._read('h')      # Product-dependent variable 3 (unused)
        self._read('h' * 16) # Product-dependent thresholds (how do I interpret these?)
        self._read('h' * 7)  # Product-dependent variables 4-10 (mostly unused ... do I need the max?)

        version    = self._read('b')
        spot_blank = self._read('b')

        offset_symbology = self._read('i')
        offset_graphic   = self._read('i')
        offset_tabular   = self._read('i')

        self._time = datetime(1969, 12, 31, 0, 0, 0) + timedelta(days=scan_date, seconds=scan_time)
        print "Valid time:", self._time

        return offset_symbology > 0, offset_graphic > 0, offset_tabular > 0

    def _readProductSymbologyBlock(self):
        self._read('h') # Block separator
        block_id = self._read('h')

        if block_id != 1:
            print "This isn't the product symbology block."

        block_length    = self._read('i')
        num_layers      = self._read('h')
        layer_separator = self._read('h')
        layer_num_bytes = self._read('i')
        block_data      = self._read('h' * (layer_num_bytes / struct.calcsize('h')))

        packet_code = -1
        packet_size = -1
        packet_counter = -1
        packet_value = -1
        packet = []
        for item in block_data:
            if packet_code == -1:
                packet_code = item
            elif packet_size == -1:
                packet_size = item
                packet_counter = 0
            elif packet_value == -1:
                packet_value = item
                packet_counter += struct.calcsize('h')
            else:
                packet.append(item)
                packet_counter += struct.calcsize('h')

                if packet_counter == packet_size:
                    if packet_code == 8:
                        str_data = struct.pack('>' + 'h' * (packet_size / struct.calcsize('h') - 3), *packet[2:])
                    elif packet_code == 4:
                        pass

                    packet = []
                    packet_code = -1
                    packet_size = -1
                    packet_counter = -1
                    packet_value = -1

        return

    def _readTabularBlock(self):
        self._read('h')
        block_id = self._read('h')
        if block_id != 3:
            print "This is not the tabular block."

        block_size = self._read('i')

        self._read('h')
        self._read('h')
        self._read('i')
        self._read('i')
        self._read('h')
        self._read('h')
        self._read('h')

        self._read('h')
        self._read('i')
        self._read('i')
        self._read('h')
        product_code = self._read('h')

        operational_mode    = self._read('h')
        vcp                 = self._read('h')
        req_sequence_number = self._read('h')
        vol_sequence_number = self._read('h')

        scan_date    = self._read('h')
        scan_time    = self._read('i')
        product_date = self._read('h')
        product_time = self._read('i')

        self._read('h')      # Product-dependent variable 1 (unused)
        self._read('h')      # Product-dependent variable 2 (unused)
        self._read('h')      # Elevation (unused)
        self._read('h')      # Product-dependent variable 3 (unused)
        self._read('h' * 16) # Product-dependent thresholds (how do I interpret these?)
        self._read('h' * 7)  # Product-dependent variables 4-10 (mostly unused ... do I need the max?)

        version    = self._read('b')
        spot_blank = self._read('b')

        offset_symbology = self._read('i')
        offset_graphic   = self._read('i')
        offset_tabular   = self._read('i')

        self._read('h') # Block separator
        num_pages = self._read('h')
        self._text_message = []
        for idx in range(num_pages):
            num_chars = self._read('h')
            self._text_message.append([])
            while num_chars != -1:
                self._text_message[-1].append(self._read("s%d" % num_chars))
#               print self._text_message[-1][-1]
                num_chars = self._read('h')

        return

    def _read(self, type_string):
        if type_string[0] != 's':
            size = struct.calcsize(type_string)
            data = struct.unpack(">%s" % type_string, self._rpg.read(size))
        else:
            size = int(type_string[1:])
            data = tuple([ self._rpg.read(size).strip("\0") ])

        if len(data) == 1:
            return data[0]
        else:
            return list(data)

def compute_parameters(wind_dir, wind_spd, altitude, storm_dir, storm_spd):
    def compute_shear(u1, v1, u2, v2):
        return u2 - u1, v2 - v1

    def clip_profile(prof, alt, clip_alt, intrp_prof):
        try:
            idx_clip = np.where((altitude[:-1] <= clip_alt) & (altitude[1:] > clip_alt))[0][0]
        except IndexError:
            return np.nan * np.ones(prof.size)

        prof_clip = prof[:(idx_clip + 1)]
        prof_clip = np.append(prof_clip, intrp_prof)

        return np.array(prof_clip)

    params = {}

    wind_dir = np.pi * wind_dir / 180
    storm_dir = np.pi * storm_dir / 180    

    u = -wind_spd * np.sin(wind_dir)
    v = -wind_spd * np.cos(wind_dir)

    storm_u = -storm_spd * np.sin(storm_dir)
    storm_v = -storm_spd * np.cos(storm_dir)

    u_1km, u_3km, u_6km = np.interp([ 1., 3., 6. ], altitude, u, left=np.nan, right=np.nan)
    v_1km, v_3km, v_6km = np.interp([ 1., 3., 6. ], altitude, v, left=np.nan, right=np.nan)

    u_shear_1km, v_shear_1km = compute_shear(u[0], v[0], u_1km, v_1km)
    u_shear_3km, v_shear_3km = compute_shear(u[0], v[0], u_3km, v_3km)
    u_shear_6km, v_shear_6km = compute_shear(u[0], v[0], u_6km, v_6km)

    params['shear_mag_1km'] = np.hypot(u_shear_1km, v_shear_1km)
    params['shear_mag_3km'] = np.hypot(u_shear_3km, v_shear_3km)
    params['shear_mag_6km'] = np.hypot(u_shear_6km, v_shear_6km)

    sr_u = u - storm_u
    sr_v = v - storm_v

    sru_0_1km = clip_profile(sr_u, altitude, 1, u_1km) / 1.94
    srv_0_1km = clip_profile(sr_v, altitude, 1, v_1km) / 1.94
    alt_0_1km = clip_profile(altitude, altitude, 1, lambda x: x)

    layers = (sru_0_1km[1:] * srv_0_1km[:-1]) - (sru_0_1km[:-1] * srv_0_1km[1:])
    params['srh_1km'] = layers.sum()

    sru_0_3km = clip_profile(sr_u, altitude, 3, u_3km) / 1.94
    srv_0_3km = clip_profile(sr_v, altitude, 3, v_3km) / 1.94
    alt_0_3km = clip_profile(altitude, altitude, 3, lambda x: x)

    layers = (sru_0_3km[1:] * srv_0_3km[:-1]) - (sru_0_3km[:-1] * srv_0_3km[1:])
    params['srh_3km'] = layers.sum()

    return params

def plot_hodograph(wind_dir, wind_spd, altitude, rms_error, img_title, img_file_name, parameters={}, storm_motion=()):
    param_names = {
        'shear_mag_1km':"0-1 km Bulk Shear",
        'shear_mag_3km':"0-3 km Bulk Shear",
        'shear_mag_6km':"0-6 km Bulk Shear",
        'srh_1km':"0-1 km Storm-Relative Helicity",
        'srh_3km':"0-3 km Storm-Relative Helicity",
    }

    param_units = {
        'shear_mag_1km':"kt",
        'shear_mag_3km':"kt",
        'shear_mag_6km':"kt",
        'srh_1km':"m$^2$ s$^{-2}$",
        'srh_3km':"m$^2$ s$^{-2}$",
    }

    pylab.clf()
    pylab.axes((0.05, 0.05, 0.65, 0.85), polar=True)

    rms_error_colors = ['c', 'g', 'y', 'r', 'm']
    rms_error_thresh = [0, 2, 6, 10, 14, 999]
    wind_dir = np.pi * wind_dir / 180

    u = -wind_spd * np.sin(wind_dir)
    v = -wind_spd * np.cos(wind_dir)

    u_marker = np.interp(np.arange(16, dtype=float), altitude, u, left=np.nan, right=np.nan)
    v_marker = np.interp(np.arange(16, dtype=float), altitude, v, left=np.nan, right=np.nan)
    ws_marker = np.hypot(u_marker, v_marker)
    wd_marker = np.arctan2(-u_marker, -v_marker)

    u_avg = (u[1:] + u[:-1]) / 2
    v_avg = (v[1:] + v[:-1]) / 2

    wind_spd_avg = np.hypot(u_avg, v_avg)
    wind_dir_avg = np.arctan2(-u_avg, -v_avg)

    color_index = np.where((rms_error[0] >= rms_error_thresh[:-1]) & (rms_error[0] < rms_error_thresh[1:]))[0][0]
    pylab.polar([ wind_dir[0], wind_dir_avg[0] ], [ wind_spd[0], wind_spd_avg[0] ], color=rms_error_colors[color_index], lw=1.5)

    for idx in range(1, len(wind_dir) - 1):
        color_index = np.where((rms_error[idx] >= rms_error_thresh[:-1]) & (rms_error[idx] < rms_error_thresh[1:]))[0][0]
        pylab.polar([ wind_dir_avg[idx - 1], wind_dir[idx], wind_dir_avg[idx] ], [ wind_spd_avg[idx - 1], wind_spd[idx], wind_spd_avg[idx] ], color=rms_error_colors[color_index], lw=1.5)

    color_index = np.where((rms_error[-1] >= rms_error_thresh[:-1]) & (rms_error[-1] < rms_error_thresh[1:]))[0][0]
    pylab.polar([ wind_dir_avg[-1], wind_dir[-1] ], [ wind_spd_avg[-1], wind_spd[-1] ], color=rms_error_colors[color_index], lw=1.5)

    u_500_marker = np.interp(0.5, altitude, u, left=np.nan, right=np.nan)
    v_500_marker = np.interp(0.5, altitude, v, left=np.nan, right=np.nan)

    ws_500_marker = np.hypot(u_500_marker, v_500_marker)
    wd_500_marker = np.arctan2(-u_500_marker, -v_500_marker)

    pylab.polar(wd_500_marker, ws_500_marker, ls='None', mec='k', mfc='k', marker='o', ms=3)
    pylab.polar(wd_marker, ws_marker, ls='None', mec='k', mfc='k', marker='o', ms=4)

    if storm_motion != ():
        storm_direction, storm_speed = storm_motion
        pylab.plot(np.pi * storm_direction / 180., storm_speed, 'k+')

    pylab.gca().set_theta_direction(-1)
    pylab.gca().set_theta_zero_location('S')
    pylab.gca().set_thetagrids(np.arange(0, 360, 30), labels=np.arange(0, 360, 30), frac=1.05)
    pylab.gca().set_rgrids(np.arange(10, 80, 10), labels=np.arange(10, 70, 10), angle=15)
    pylab.ylim((0, 70))

    pylab.text(wind_dir[0], wind_spd[0], "%3.1f" % altitude[0], size='small', weight='bold')
    pylab.text(wind_dir[-1], wind_spd[-1], "%3.1f" % altitude[-1], size='small', weight='bold')

    start_x = 1.07
    start_y = 0.62

    for idx, param_key in enumerate(sorted(parameters.keys())):
        if np.isnan(parameters[param_key]):
            param_text = "%s\n  %f" % (param_names[param_key], parameters[param_key])
        else:
            param_text = "%s\n  %.1f %s" % (param_names[param_key], parameters[param_key], param_units[param_key])

        pylab.text(start_x, start_y - idx * 0.075, param_text, transform=pylab.gca().transAxes, size='x-small', weight='bold')

    start_y = 0.25

    pylab.text(start_x, start_y, "RMS Errors:", transform=pylab.gca().transAxes, size='x-small', weight='bold')

    for idx, color in enumerate(rms_error_colors):
        line = Line2D([start_x, start_x + 0.05], [start_y + 0.012 - (idx + 1) * 0.0375, start_y + 0.012 - (idx + 1) * 0.0375], color=color, clip_on=False, lw=1.5, transform=pylab.gca().transAxes)
        pylab.gca().add_line(line)
        if rms_error_thresh[idx + 1] == 999:
            legend_text = "%d kt+" % rms_error_thresh[idx]
        else:
            legend_text = "%d-%d kt" % (rms_error_thresh[idx], rms_error_thresh[idx + 1])
        pylab.text(start_x + 0.075, start_y - (idx + 1) * 0.0375, legend_text, transform=pylab.gca().transAxes, size='x-small', weight='bold')

    pylab.suptitle(img_title)
    pylab.savefig(img_file_name)
    return

def main():
    usage = """
Usage:
            plot_vad.py RADAR_ID STORM_MOTION [ RADAR_ID STORM_MOTION ... ]

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

        url = "ftp://tgftp.nws.noaa.gov/SL.us008001/DF.of/DC.radar/DS.48vwp/SI.%s/sn.last" % rid.lower()
        try:
            vad = VADFile(urllib2.urlopen(url))
        except urllib2.URLError:
            print "Could not find radar site '%s'" % rid.upper()
            continue

        vad_list = []
        for page in vad._text_message:
            if (page[0].strip())[:20] == "VAD Algorithm Output":
                vad_list.extend(page[3:])

        altitude = []
        wind_dir = []
        wind_spd = []
        rms_error = []
        slant_range = []
        elev_angle = []

        for line in vad_list:
            values = line.strip().split()
            wind_dir.append(int(values[4]))
            wind_spd.append(int(values[5]))
            rms_error.append(float(values[6]))
            slant_range.append(float(values[8]))
            elev_angle.append(float(values[9]))

        wind_dir = np.array(wind_dir)
        wind_spd = np.array(wind_spd)
        rms_error = np.array(rms_error)
        slant_range = np.array(slant_range) * 6067.1 / 3281.
        elev_angle = np.array(elev_angle)

        r_e = 4. / 3. * 6371
        altitude_agl = np.sqrt(r_e ** 2 + slant_range ** 2 + 2 * r_e * slant_range * np.sin(np.pi * elev_angle / 180.)) - r_e

        params = compute_parameters(wind_dir, wind_spd, altitude_agl, sd, ss)

        plot_hodograph(wind_dir, wind_spd, altitude_agl, rms_error, "%s VWP valid %s" % (rid, vad._time.strftime("%d %b %Y %H%M UTC")), "%s_vad.png" % rid, parameters=params, storm_motion=(sd, ss))

if __name__ == "__main__":
    main()
