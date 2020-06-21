
import json
import gzip
from datetime import datetime, timedelta
import argparse

from vad_reader import download_vad, VADFile
from vad import parse_time
from wsr88d import build_has_name

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('radar_id', help="The 4-character identifier for the radar (e.g. KTLX, KFWS, etc.)")
    ap.add_argument('-t', '--time', dest='time', type=parse_time, help="Time to plot. Takes the form DD/HHMM, where DD is the day, HH is the hour, and MM is the minute.")
    ap.add_argument('-p', '--local-path', dest='local_path', help="Path to local data. If not given, download from the Internet.")
    ap.add_argument('-o', '--output', dest='output', default='.', help="Path to output JSON")
    ap.add_argument('-z', '--gzip', dest='gzip', action='store_true', help="Flag to gzip output")

    args = ap.parse_args()

    if args.local_path is None:
        vad = download_vad(args.radar_id, time=args.time)
    else:
        iname = build_has_name(args.radar_id, args.time)
        vad = VADFile(open("%s/%s" % (args.local_path, iname), 'rb'))

    vwp = {
        'radar_id': args.radar_id,
        'datetime': args.time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'data': {var: list(vad[var]) for var in ['wind_dir', 'wind_spd', 'altitude', 'rms_error']},
    }

    out_fname = f'{args.output}/{args.radar_id}_{args.time:%Y%m%d_%H%M}.json'
    if args.gzip:
        with gzip.open(f'{out_fname}.gz', 'wb') as fjson:
            fjson.write(json.dumps(vwp).encode('utf-8'))
    else:
        with open(out_fname, 'w') as fjson:
            fjson.write(json.dumps(vwp))


if __name__ == "__main__":
    main()
