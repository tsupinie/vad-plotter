
from __future__ import print_function
import numpy as np

import struct
from datetime import datetime, timedelta

from wsr88d import build_has_name

try:
    from urllib.request import urlopen, URLError
except ImportError:
    from urllib2 import urlopen, URLError

try:
    from io import BytesIO
except ImportError:
    from BytesIO import BytesIO

import re

_base_url = "ftp://tgftp.nws.noaa.gov/SL.us008001/DF.of/DC.radar/DS.48vwp/"

class VADFile(object):
    fields = ['wind_dir', 'wind_spd', 'rms_error', 'divergence', 'slant_range', 'elev_angle']

    def __init__(self, file):
        self._rpg = file
        self._data = None

        self._read_headers()
        has_symbology_block, has_graphic_block, has_tabular_block = self._read_product_description_block()

        if has_symbology_block:
            self._read_product_symbology_block()

        if has_graphic_block:
            pass

        if has_tabular_block:
            self._read_tabular_block()

        self._data = self._get_data()
        return

    def _read_headers(self):
        wmo_header = self._read('s30')

        message_code = self._read('h')
        message_date = self._read('h')
        message_time = self._read('i')
        message_length = self._read('i')
        source_id = self._read('h')
        dest_id = self._read('h')
        num_blocks = self._read('h')

        return

    def _read_product_description_block(self):
        self._read('h') # Block separator
        self._radar_latitude  = self._read('i') / 1000.
        self._radar_longitude = self._read('i') / 1000.
        self._radar_elevation = self._read('h')

        product_code = self._read('h')
        if product_code != 48:
            raise IOError("This isn't a VWP file.")

        operational_mode    = self._read('h')
        self._vcp           = self._read('h')
        req_sequence_number = self._read('h')
        vol_sequence_number = self._read('h')

        scan_date    = self._read('h')
        scan_time    = self._read('i')
        product_date = self._read('h')
        product_time = self._read('i')

        self._read('h')   # Product-dependent variable 1 (unused)
        self._read('h')   # Product-dependent variable 2 (unused)
        self._read('h')   # Elevation (unused)
        self._read('h')   # Product-dependent variable 3 (unused)
        self._read('16h') # Product-dependent thresholds (how do I interpret these?)
        self._read('7h')  # Product-dependent variables 4-10 (mostly unused ... do I need the max?)

        version    = self._read('b')
        spot_blank = self._read('b')

        offset_symbology = self._read('i')
        offset_graphic   = self._read('i')
        offset_tabular   = self._read('i')

        self._time = datetime(1969, 12, 31, 0, 0, 0) + timedelta(days=scan_date, seconds=scan_time)

        return offset_symbology > 0, offset_graphic > 0, offset_tabular > 0

    def _read_product_symbology_block(self):
        self._read('h') # Block separator
        block_id = self._read('h')

        if block_id != 1:
            raise IOError("This isn't the product symbology block.")

        block_length    = self._read('i')
        num_layers      = self._read('h')
        layer_separator = self._read('h')
        layer_num_bytes = self._read('i')
        block_data      = self._read('%dh' % int(layer_num_bytes / struct.calcsize('h')))

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
                        str_data = struct.pack('>%dh' % int(packet_size / struct.calcsize('h') - 3), *packet[2:])
                    elif packet_code == 4:
                        pass

                    packet = []
                    packet_code = -1
                    packet_size = -1
                    packet_counter = -1
                    packet_value = -1
        return

    def _read_tabular_block(self):
        self._read('h')
        block_id = self._read('h')
        if block_id != 3:
            raise IOError("This isn't the tabular block.")

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

        self._read('h')   # Product-dependent variable 1 (unused)
        self._read('h')   # Product-dependent variable 2 (unused)
        self._read('h')   # Elevation (unused)
        self._read('h')   # Product-dependent variable 3 (unused)
        self._read('16h') # Product-dependent thresholds (how do I interpret these?)
        self._read('7h')  # Product-dependent variables 4-10 (mostly unused ... do I need the max?)

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
                num_chars = self._read('h')

        return

    def _read(self, type_string):
        if type_string[0] != 's':
            size = struct.calcsize(type_string)
            data = struct.unpack(">%s" % type_string, self._rpg.read(size))
        else:
            size = int(type_string[1:])
            data = tuple([ self._rpg.read(size).strip(b"\0").decode('utf-8') ])

        if len(data) == 1:
            return data[0]
        else:
            return list(data)

    def _get_data(self):
        vad_list = []
        for page in self._text_message:
            if (page[0].strip())[:20] == "VAD Algorithm Output":
                vad_list.extend(page[3:])

        data = dict((k, []) for k in VADFile.fields)

        for line in vad_list:
            values = line.strip().split()
            data['wind_dir'].append(float(values[4]))
            data['wind_spd'].append(float(values[5]))
            data['rms_error'].append(float(values[6]))
            data['divergence'].append(float(values[7]) if values[7] != 'NA' else np.nan)
            data['slant_range'].append(float(values[8]))
            data['elev_angle'].append(float(values[9]))

        for key, val in data.items():
            data[key] = np.array(val)


        data['slant_range'] *= 6067.1 / 3281.

        r_e = 4. / 3. * 6371
        data['altitude'] = np.sqrt(r_e ** 2 + data['slant_range'] ** 2 + 2 * r_e * data['slant_range'] * np.sin(np.radians(data['elev_angle']))) - r_e

        order = np.argsort(data['altitude'])
        for key, val in data.items():
            data[key] = val[order]
        return data

    def __getitem__(self, key):
        if key == 'time':
            val = self._time
        else:
            val = self._data[key]
        return val

    def add_surface_wind(self, sfc_wind):
        sfc_dir, sfc_spd = sfc_wind

        keys = ['wind_dir', 'wind_spd', 'rms_error', 'altitude']
        vals = [float(sfc_dir), float(sfc_spd), 0., 0.01]

        for key, val in zip(keys, vals):
            self._data[key] = np.append(val, self._data[key])

def find_file_times(rid):
    url = "%s/SI.%s/" % (_base_url, rid.lower())

    file_text = urlopen(url).read().decode('utf-8')
    file_list = re.findall("([\w]{3} [\d]{1,2} [\d]{2}:[\d]{2}) (sn.[\d]{4})", file_text)
    file_times, file_names = list(zip(*file_list))
    file_names = list(file_names)

    year = datetime.utcnow().year
    file_dts = []
    for ft in file_times:
        ft_dt = datetime.strptime("%d %s" % (year, ft), "%Y %b %d %H:%M")
        if ft_dt > datetime.utcnow():
            ft_dt = datetime.strptime("%d %s" % (year - 1, ft), "%Y %b %d %H:%M")

        file_dts.append(ft_dt)

    file_list = list(zip(file_names, file_dts))
    file_list.sort(key=lambda fl: fl[1])

    file_names, file_dts = list(zip(*file_list))
    file_names = list(file_names)

    # The files are only moved into place when the next one is generated, so shift the
    # file names by one index to account for that.
    file_names[:-1] = file_names[1:]
    file_names[-1] = 'sn.last'

    return list(zip(file_names, file_dts))[::-1]

  
def download_vad(rid, time=None, file_id=None, cache_path=None):
    if time is None:
        if file_id is None:
            url = "%s/SI.%s/sn.last" % (_base_url, rid.lower())
        else:
            url = "%s/SI.%s/sn.%04d" % (_base_url, rid.lower(), file_id)
    else:
        file_name = ""
        for fn, ft in find_file_times(rid):
            if ft <= time:
                file_name = fn
                break

        if file_name == "":
            raise ValueError("No VAD files before %s." % time.strftime("%d %B %Y %H%M UTC"))

        url = "%s/SI.%s/%s" % (_base_url, rid.lower(), file_name)

    try:
        frem = urlopen(url)
    except URLError:
        raise ValueError("Could not find radar site '%s'" % rid.upper())

    if cache_path is None:
        vad = VADFile(frem)
    else:
        bio = BytesIO(frem.read())
        vad = VADFile(bio)

        iname = build_has_name(rid, vad['time'])
        with open("%s/%s" % (cache_path, iname), 'wb') as floc:
            floc.write(bio.getvalue())

    return vad
