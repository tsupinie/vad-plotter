
import numpy as np

import matplotlib
matplotlib.use('agg')
import pylab
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox
from matplotlib.transforms import TransformedBbox


def plot_hodograph(data, parameters, storm_motion):
    img_title = "%s VWP valid %s" % (data.rid, data['time'].strftime("%d %b %Y %H%M UTC"))
    img_file_name = "%s_vad.png" % data.rid

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

    wind_dir = np.radians(data['wind_dir'])

    u = -data['wind_spd'] * np.sin(wind_dir)
    v = -data['wind_spd'] * np.cos(wind_dir)

    u_marker = np.interp(np.arange(16, dtype=float), data['altitude'], u, left=np.nan, right=np.nan)
    v_marker = np.interp(np.arange(16, dtype=float), data['altitude'], v, left=np.nan, right=np.nan)
    ws_marker = np.hypot(u_marker, v_marker)
    wd_marker = np.arctan2(-u_marker, -v_marker)

    u_avg = (u[1:] + u[:-1]) / 2
    v_avg = (v[1:] + v[:-1]) / 2

    wind_spd_avg = np.hypot(u_avg, v_avg)
    wind_dir_avg = np.arctan2(-u_avg, -v_avg)

    color_index = np.where((data['rms_error'][0] >= rms_error_thresh[:-1]) & (data['rms_error'][0] < rms_error_thresh[1:]))[0][0]
    pylab.polar([ wind_dir[0], wind_dir_avg[0] ], [ data['wind_spd'][0], wind_spd_avg[0] ], color=rms_error_colors[color_index], lw=1.5)

    for idx in range(1, len(data['wind_dir']) - 1):
        color_index = np.where((data['rms_error'][idx] >= rms_error_thresh[:-1]) & (data['rms_error'][idx] < rms_error_thresh[1:]))[0][0]
        pylab.polar([ wind_dir_avg[idx - 1], wind_dir[idx], wind_dir_avg[idx] ], [ wind_spd_avg[idx - 1], data['wind_spd'][idx], wind_spd_avg[idx] ], color=rms_error_colors[color_index], lw=1.5)

    color_index = np.where((data['rms_error'][-1] >= rms_error_thresh[:-1]) & (data['rms_error'][-1] < rms_error_thresh[1:]))[0][0]
    pylab.polar([ wind_dir_avg[-1], wind_dir[-1] ], [ wind_spd_avg[-1], data['wind_spd'][-1] ], color=rms_error_colors[color_index], lw=1.5)

    u_500_marker = np.interp(0.5, data['altitude'], u, left=np.nan, right=np.nan)
    v_500_marker = np.interp(0.5, data['altitude'], v, left=np.nan, right=np.nan)

    ws_500_marker = np.hypot(u_500_marker, v_500_marker)
    wd_500_marker = np.arctan2(-u_500_marker, -v_500_marker)

    pylab.polar(wd_500_marker, ws_500_marker, ls='None', mec='k', mfc='k', marker='o', ms=3)
    pylab.polar(wd_marker, ws_marker, ls='None', mec='k', mfc='k', marker='o', ms=4)

    storm_direction, storm_speed = storm_motion
    pylab.plot(np.pi * storm_direction / 180., storm_speed, 'k+')

    pylab.gca().set_theta_direction(-1)
    pylab.gca().set_theta_zero_location('S')
    pylab.gca().set_thetagrids(np.arange(0, 360, 30), labels=np.arange(0, 360, 30), frac=1.05)
    pylab.gca().set_rgrids(np.arange(10, 80, 10), labels=np.arange(10, 70, 10), angle=15)
    pylab.ylim((0, 70))

    pylab.text(wind_dir[0], data['wind_spd'][0], "%3.1f" % data['altitude'][0], size='small', weight='bold')
    pylab.text(wind_dir[-1], data['wind_spd'][-1], "%3.1f" % data['altitude'][-1], size='small', weight='bold')

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


