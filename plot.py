
import numpy as np

import matplotlib
matplotlib.use('agg')
import pylab
from matplotlib.patches import Circle
from matplotlib.lines import Line2D

from params import vec2comp

_seg_hghts = [0, 3, 6, 9, 12, 18]
_seg_colors = ['r', '#00ff00', '#008800', '#993399', 'c']


def _plot_param_table(parameters):
    storm_dir, storm_spd = parameters['storm_motion']
    trans = pylab.gca().transAxes
    line_space = 0.028
    start_x = 1.02
    start_y = 1.0 - line_space

    line_y = start_y

    kwargs = {'color':'k', 'fontsize':10, 'clip_on':False, 'transform':trans}

    pylab.text(start_x + 0.175, start_y, "Parameter Table", ha='center', fontweight='bold', **kwargs)

    spacer = Line2D([start_x, start_x + 0.361], [line_y - line_space * 0.48] * 2, color='k', linestyle='-', transform=trans, clip_on=False)
    pylab.gca().add_line(spacer)
    line_y -= line_space * 1.5

    pylab.text(start_x + 0.095, line_y,          "BWD (kts)", fontweight='bold', **kwargs)
    pylab.text(start_x + 0.22,  line_y - 0.0025, "SRH (m$^2$s$^{-2}$)", fontweight='bold', **kwargs)

    line_y -= line_space

    pylab.text(start_x, line_y, "0-1 km", fontweight='bold', **kwargs)
    val = "--" if np.isnan(parameters['shear_mag_1km']) else "%d" % int(parameters['shear_mag_1km'])
    pylab.text(start_x + 0.095, line_y, val, **kwargs)
    val = "--" if np.isnan(parameters['srh_1km']) else "%d" % int(parameters['srh_1km'])
    pylab.text(start_x + 0.22,  line_y, val, **kwargs)

    line_y -= line_space

    pylab.text(start_x, line_y, "0-3 km", fontweight='bold', **kwargs)
    val = "--" if np.isnan(parameters['shear_mag_3km']) else "%d" % int(parameters['shear_mag_3km'])
    pylab.text(start_x + 0.095, line_y, val, **kwargs)
    val = "--" if np.isnan(parameters['srh_3km']) else "%d" % int(parameters['srh_3km'])
    pylab.text(start_x + 0.22,  line_y, val, **kwargs)

    line_y -= line_space

    pylab.text(start_x, line_y, "0-6 km", fontweight='bold', **kwargs)
    val = "--" if np.isnan(parameters['shear_mag_6km']) else "%d" % int(parameters['shear_mag_6km'])
    pylab.text(start_x + 0.095, line_y, val, **kwargs)

    spacer = Line2D([start_x, start_x + 0.361], [line_y - line_space * 0.48] * 2, color='k', linestyle='-', transform=trans, clip_on=False)
    pylab.gca().add_line(spacer)
    line_y -= 1.5 * line_space

    pylab.text(start_x, line_y, "Storm Motion:", fontweight='bold', **kwargs)
    val = "--" if np.isnan(parameters['storm_motion']).any() else "%03d/%02d kts" % (storm_dir, storm_spd)
    pylab.text(start_x + 0.26, line_y + 0.001, val, **kwargs)

    line_y -= line_space

    bl_dir, bl_spd = parameters['bunkers_left']
    pylab.text(start_x, line_y, "Bunkers Left Mover:", fontweight='bold', **kwargs)
    val = "--" if np.isnan(parameters['bunkers_left']).any() else "%03d/%02d kts" % (bl_dir, bl_spd)
    pylab.text(start_x + 0.26, line_y + 0.001, val, **kwargs)

    line_y -= line_space

    br_dir, br_spd = parameters['bunkers_right']
    pylab.text(start_x, line_y, "Bunkers Right Mover:", fontweight='bold', **kwargs)
    val = "--" if np.isnan(parameters['bunkers_right']).any() else "%03d/%02d kts" % (br_dir, br_spd)
    pylab.text(start_x + 0.26, line_y + 0.001, val, **kwargs)

    spacer = Line2D([start_x, start_x + 0.361], [line_y - line_space * 0.48] * 2, color='k', linestyle='-', transform=trans, clip_on=False)
    pylab.gca().add_line(spacer)
    line_y -= 1.5 * line_space

    pylab.text(start_x, line_y, "Critical Angle:", fontweight='bold', **kwargs)
    val = "--" if np.isnan(parameters['critical']) else "%d$^{\circ}$" % int(parameters['critical'])
    pylab.text(start_x + 0.18, line_y - 0.0025, val, **kwargs)


def _plot_data(data, parameters):
    storm_dir, storm_spd = parameters['storm_motion']
    bl_dir, bl_spd = parameters['bunkers_left']
    br_dir, br_spd = parameters['bunkers_right']

    u, v = vec2comp(data['wind_dir'], data['wind_spd'])
    alt = data['altitude']

    storm_u, storm_v = vec2comp(storm_dir, storm_spd)
    bl_u, bl_v = vec2comp(bl_dir, bl_spd)
    br_u, br_v = vec2comp(br_dir, br_spd)

    seg_idxs = np.searchsorted(alt, _seg_hghts)
    seg_u = np.interp(_seg_hghts, alt, u, left=np.nan, right=np.nan)
    seg_v = np.interp(_seg_hghts, alt, v, left=np.nan, right=np.nan)
    ca_u = np.interp(0.5, alt, u, left=np.nan, right=np.nan)
    ca_v = np.interp(0.5, alt, v, left=np.nan, right=np.nan)

    for idx in xrange(len(_seg_hghts) - 1):
        idx_start = seg_idxs[idx]
        idx_end = seg_idxs[idx + 1]

        if not np.isnan(seg_u[idx]):
            pylab.plot([seg_u[idx], u[idx_start]], [seg_v[idx], v[idx_start]], '-', color=_seg_colors[idx], linewidth=1.5)

        if idx_start < len(data['rms_error']) and data['rms_error'][idx_start] == 0.:
            # The first segment is to the surface wind, draw it in a dashed line
            pylab.plot(u[idx_start:(idx_start + 2)], v[idx_start:(idx_start + 2)], '--', color=_seg_colors[idx], linewidth=1.5)
            pylab.plot(u[(idx_start + 1):idx_end], v[(idx_start + 1):idx_end], '-', color=_seg_colors[idx], linewidth=1.5)
        else:
            pylab.plot(u[idx_start:idx_end], v[idx_start:idx_end], '-', color=_seg_colors[idx], linewidth=1.5)

        if not np.isnan(seg_u[idx + 1]):
            pylab.plot([u[idx_end - 1], seg_u[idx + 1]], [v[idx_end - 1], seg_v[idx + 1]], '-', color=_seg_colors[idx], linewidth=1.5)

        for upt, vpt, rms in zip(u, v, data['rms_error'])[idx_start:idx_end]:
            rad = np.sqrt(2) * rms
            circ = Circle((upt, vpt), rad, color=_seg_colors[idx], alpha=0.05)
            pylab.gca().add_patch(circ)

    pylab.plot([storm_u, u[0], ca_u], [storm_v, v[0], ca_v], 'c-', linewidth=0.75)

    if not (np.isnan(bl_u) or np.isnan(bl_v)):
        pylab.plot(bl_u, bl_v, 'ko', markersize=5, mfc='none')
        pylab.text(bl_u + 0.5, bl_v - 0.5, "LM", ha='left', va='top', color='k', fontsize=10)

    if not (np.isnan(br_u) or np.isnan(br_v)):
        pylab.plot(br_u, br_v, 'ko', markersize=5, mfc='none')
        pylab.text(br_u + 0.5, br_v - 0.5, "RM", ha='left', va='top', color='k', fontsize=10)

    if not (np.isnan(storm_u) or np.isnan(storm_v)) and storm_u != bl_u and storm_v != bl_v and storm_u != br_u and storm_v != br_v:
        pylab.plot(storm_u, storm_v, 'k+', markersize=6)
        pylab.text(storm_u + 0.5, storm_v - 0.5, "SM", ha='left', va='top', color='k', fontsize=10)


def _plot_background(max_u):
    max_ring = int(np.ceil(max_u * np.sqrt(2)))
    pylab.axvline(x=0, linestyle='-', color='#999999')
    pylab.axhline(y=0, linestyle='-', color='#999999')

    for irng in xrange(10, max_ring, 10):
        ring = Circle((0., 0.), irng, linestyle='dashed', fc='none', ec='#999999')
        pylab.gca().add_patch(ring)

        rng_str = "%d" % irng if irng != max_u - 10 else "%d kts" % irng

        pylab.text(irng + 0.5, -0.5, rng_str, ha='left', va='top', fontsize=9, color='#999999', clip_on=True, clip_box=pylab.gca().get_clip_box())


def plot_hodograph(data, parameters, fname=None):
    img_title = "%s VWP valid %s" % (data.rid, data['time'].strftime("%d %b %Y %H%M UTC"))
    if fname is not None:
        img_file_name = fname
    else:
        img_file_name = "%s_vad.png" % data.rid
    max_u = 80

    pylab.figure(figsize=(10, 7.5), dpi=150)
    fig_wid, fig_hght = pylab.gcf().get_size_inches()
    fig_aspect = fig_wid / fig_hght

    axes_left = 0.05
    axes_bot = 0.05
    axes_hght = 0.9
    axes_wid = axes_hght / fig_aspect
    pylab.axes((axes_left, axes_bot, axes_wid, axes_hght))

    _plot_background(max_u)
    _plot_data(data, parameters)
    _plot_param_table(parameters)

    pylab.xlim(-max_u / 2, max_u)
    pylab.ylim(-max_u / 2, max_u)
    pylab.xticks([])
    pylab.yticks([])

    pylab.title(img_title)
    pylab.savefig(img_file_name)
    pylab.close()

