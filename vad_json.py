
import json
import gzip
from datetime import datetime, timedelta
import argparse
import sys

from vad_reader import download_vad, VADFile
from vad import parse_time
from wsr88d import build_has_name

def vad_json(radar_id, vwp_time=None, file_id=None, local_path=None, output='.', gzip=False):
    if local_path is None:
        vad = download_vad(radar_id, time=vwp_time, file_id=file_id)
    else:
        iname = build_has_name(radar_id, vwp_time)
        vad = VADFile(open("%s/%s" % (local_path, iname), 'rb'))

    output_dt = vad['time']

    vwp = {
        'radar_id': radar_id,
        'datetime': output_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'data': {var: list(vad[var]) for var in ['wind_dir', 'wind_spd', 'altitude', 'rms_error']},
    }

    out_fname = f'{output}/{radar_id}_{output_dt:%Y%m%d_%H%M}.json'
    if gzip:
        out_fname = f'{out_fname}.gz'
        with gzip.open(out_fname, 'wb') as fjson:
            fjson.write(json.dumps(vwp).encode('utf-8'))
    else:
        with open(out_fname, 'w') as fjson:
            fjson.write(json.dumps(vwp))

    output = {'filename': out_fname}
    print(json.dumps(output))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('radar_id', help="The 4-character identifier for the radar (e.g. KTLX, KFWS, etc.)")
    ap.add_argument('-t', '--time', dest='time', type=parse_time, help="Time to download. Takes the form DD/HHMM, where DD is the day, HH is the hour, and MM is the minute.")
    ap.add_argument('-i', '--file-id', dest='file_id', type=int, help="File id to download (this is the last 4 digits of sn.0250)")
    ap.add_argument('-p', '--local-path', dest='local_path', help="Path to local data. If not given, download from the Internet.")
    ap.add_argument('-o', '--output', dest='output', default='.', help="Path to output JSON")
    ap.add_argument('-z', '--gzip', dest='gzip', action='store_true', help="Flag to gzip output")

    args = ap.parse_args()

    try:
        vad_json(args.radar_id, vwp_time=args.time, file_id=args.file_id, local_path=args.local_path, 
            output=args.output, gzip=args.gzip)
    except Exception as exc:
        typ, val, trace = sys.exc_info()
        err_str = f"{typ.__name__}: {val}"
        error = {'error': err_str}
        print(json.dumps(error));

if __name__ == "__main__":
    main()
