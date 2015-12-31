
import numpy as np

def vec2comp(wdir, wspd):
    u = -wspd * np.sin(np.radians(wdir))
    v = -wspd * np.cos(np.radians(wdir))
    return u, v


def interp(u, v, altitude, hght):
    u_hght = np.interp([hght], altitude, u, left=np.nan, right=np.nan)
    v_hght = np.interp([hght], altitude, v, left=np.nan, right=np.nan)
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
    storm_u, storm_v = vec2comp(*storm_motion)

    sru = (u - storm_u) / 1.94
    srv = (v - storm_v) / 1.94

    sru_hght, srv_hght = interp(sru, srv, data['altitude'], hght)
    sru_clip = _clip_profile(sru, data['altitude'], hght, sru_hght)
    srv_clip = _clip_profile(srv, data['altitude'], hght, srv_hght)

    layers = (sru_clip[1:] * srv_clip[:-1]) - (sru_clip[:-1] * srv_clip[1:])
    return layers.sum()
    

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
    storm_dir, storm_spd = storm_motion

    params = {}

    params['critical'] = compute_crit_angl(data, storm_motion)
    for hght in [1, 3, 6]:
        params["shear_mag_%dkm" % hght] = compute_shear_mag(data, hght)

    for hght in [1, 3]:
        params["srh_%dkm" % hght] = compute_srh(data, storm_motion, hght)

    return params


