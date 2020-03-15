
import numpy as np

def vec2comp(wdir, wspd):
    u = -wspd * np.sin(np.radians(wdir))
    v = -wspd * np.cos(np.radians(wdir))
    return u, v

def comp2vec(u, v):
    vmag = np.hypot(u, v)
    vdir = 90 - np.degrees(np.arctan2(-v, -u))
    vdir = np.where(vdir < 0, vdir + 360, vdir)
    vdir = np.where(vdir >= 360, vdir - 360, vdir)
    return vdir, vmag

def interp(u, v, altitude, hght):
    u_hght = np.interp(hght, altitude, u, left=np.nan, right=np.nan)
    v_hght = np.interp(hght, altitude, v, left=np.nan, right=np.nan)
    return u_hght, v_hght


def _clip_profile(prof, alt, clip_alt, intrp_prof):
    try:
        idx_clip = np.where((alt[:-1] <= clip_alt) & (alt[1:] > clip_alt))[0][0]
    except IndexError:
        return np.nan * np.ones(prof.size)

    prof_clip = prof[:(idx_clip + 1)]
    prof_clip = np.append(prof_clip, intrp_prof)

    return np.array(prof_clip)


def compute_shear_mag(data, hght):
    u, v = vec2comp(data['wind_dir'], data['wind_spd'])
    u_hght, v_hght = interp(u, v, data['altitude'], hght)
    return np.hypot(u_hght - u[0], v_hght - v[0])


def compute_srh(data, storm_motion, hght):
    u, v = vec2comp(data['wind_dir'], data['wind_spd'])
    if len(u) < 2 and len(v) < 2:
        return np.nan

    storm_u, storm_v = vec2comp(*storm_motion)

    sru = (u - storm_u) / 1.94
    srv = (v - storm_v) / 1.94

    sru_hght, srv_hght = interp(sru, srv, data['altitude'], hght)
    sru_clip = _clip_profile(sru, data['altitude'], hght, sru_hght)
    srv_clip = _clip_profile(srv, data['altitude'], hght, srv_hght)

    layers = (sru_clip[1:] * srv_clip[:-1]) - (sru_clip[:-1] * srv_clip[1:])
    return layers.sum()


def compute_bunkers(data):
    d = 7.5 * 1.94     # Deviation value emperically derived as 7.5 m/s
    hght = 6
                
    # SFC-6km Mean Wind
    u, v = vec2comp(data['wind_dir'], data['wind_spd'])
    u_hght, v_hght = interp(u, v, data['altitude'], hght)
    u_clip = _clip_profile(u, data['altitude'], hght, u_hght)
    v_clip = _clip_profile(v, data['altitude'], hght, v_hght)

    mnu6 = u_clip.mean()
    mnv6 = v_clip.mean()

    # SFC-6km Shear Vector
    shru = u_hght - u[0]
    shrv = v_hght - v[0]

    # Bunkers Right Motion
    tmp = d / np.hypot(shru, shrv)
    rstu = mnu6 + (tmp * shrv)
    rstv = mnv6 - (tmp * shru)
    lstu = mnu6 - (tmp * shrv)
    lstv = mnv6 + (tmp * shru)

    return comp2vec(rstu, rstv), comp2vec(lstu, lstv), comp2vec(mnu6, mnv6)
    

def compute_crit_angl(data, storm_motion):
    u, v = vec2comp(data['wind_dir'], data['wind_spd'])
    storm_u, storm_v = vec2comp(*storm_motion)

    u_05km, v_05km = interp(u, v, data['altitude'], 0.5)

    base_u = storm_u - u[0]
    base_v = storm_v - v[0]

    ang_u = u_05km - u[0]
    ang_v = v_05km - v[0]

    len_base = np.hypot(base_u, base_v)
    len_ang = np.hypot(ang_u, ang_v)

    base_dot_ang = base_u * ang_u + base_v * ang_v
    return np.degrees(np.arccos(base_dot_ang / (len_base * len_ang)))


def compute_parameters(data, storm_motion):
    params = {}

    try:
        params['bunkers_right'], params['bunkers_left'], params['mean_wind'] = compute_bunkers(data)
    except (IndexError, ValueError):
        params['bunkers_right'] = (np.nan, np.nan)
        params['bunkers_left'] = (np.nan, np.nan)
        params['mean_wind'] = (np.nan, np.nan)

    if storm_motion.lower() in ['blm', 'left-mover']:
        params['storm_motion'] = params['bunkers_left']
    elif storm_motion.lower() in ['brm', 'right-mover']:
        params['storm_motion'] = params['bunkers_right']
    elif storm_motion.lower() in ['mnw', 'mean-wind']:
        params['storm_motion'] = params['mean_wind']
    else:
        params['storm_motion'] = tuple(int(v) for v in storm_motion.split('/'))

    try:
        params['critical'] = compute_crit_angl(data, params['storm_motion'])
    except (IndexError, ValueError):
        params['critical'] = np.nan

    for hght in [1, 3, 6]:
        try:
            params["shear_mag_%dm" % (hght * 1000)] = compute_shear_mag(data, hght)
        except (IndexError, ValueError):
            params["shear_mag_%dm" % (hght * 1000)] = np.nan

    for hght in [1, 3]:
        params["srh_%dm" % (hght * 1000)] = compute_srh(data, params['storm_motion'], hght)

    return params


