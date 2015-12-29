
import numpy as np

def compute_parameters(data, storm_motion):
    def compute_shear(u1, v1, u2, v2):
        return u2 - u1, v2 - v1

    def clip_profile(prof, alt, clip_alt, intrp_prof):
        try:
            idx_clip = np.where((data['altitude'][:-1] <= clip_alt) & (data['altitude'][1:] > clip_alt))[0][0]
        except IndexError:
            return np.nan * np.ones(prof.size)

        prof_clip = prof[:(idx_clip + 1)]
        prof_clip = np.append(prof_clip, intrp_prof)

        return np.array(prof_clip)

    storm_dir, storm_spd = storm_motion

    params = {}

    wind_dir = np.radians(data['wind_dir'])
    storm_dir = np.radians(storm_dir)

    u = -data['wind_spd'] * np.sin(wind_dir)
    v = -data['wind_spd'] * np.cos(wind_dir)

    storm_u = -storm_spd * np.sin(storm_dir)
    storm_v = -storm_spd * np.cos(storm_dir)

    u_1km, u_3km, u_6km = np.interp([ 1., 3., 6. ], data['altitude'], u, left=np.nan, right=np.nan)
    v_1km, v_3km, v_6km = np.interp([ 1., 3., 6. ], data['altitude'], v, left=np.nan, right=np.nan)

    u_shear_1km, v_shear_1km = compute_shear(u[0], v[0], u_1km, v_1km)
    u_shear_3km, v_shear_3km = compute_shear(u[0], v[0], u_3km, v_3km)
    u_shear_6km, v_shear_6km = compute_shear(u[0], v[0], u_6km, v_6km)

    params['shear_mag_1km'] = np.hypot(u_shear_1km, v_shear_1km)
    params['shear_mag_3km'] = np.hypot(u_shear_3km, v_shear_3km)
    params['shear_mag_6km'] = np.hypot(u_shear_6km, v_shear_6km)

    sr_u = u - storm_u
    sr_v = v - storm_v

    sru_0_1km = clip_profile(sr_u, data['altitude'], 1, u_1km) / 1.94
    srv_0_1km = clip_profile(sr_v, data['altitude'], 1, v_1km) / 1.94

    layers = (sru_0_1km[1:] * srv_0_1km[:-1]) - (sru_0_1km[:-1] * srv_0_1km[1:])
    params['srh_1km'] = layers.sum()

    sru_0_3km = clip_profile(sr_u, data['altitude'], 3, u_3km) / 1.94
    srv_0_3km = clip_profile(sr_v, data['altitude'], 3, v_3km) / 1.94

    layers = (sru_0_3km[1:] * srv_0_3km[:-1]) - (sru_0_3km[:-1] * srv_0_3km[1:])
    params['srh_3km'] = layers.sum()

    return params


