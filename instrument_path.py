import os
import re

FILENAME_PATTERN = re.compile(
    r"(?P<instrument>[a-zA-Z]+)_"      # cello
    r"(?P<pitch>[A-G][sb]?\d)_"        # A2, Gs6
    r"(?P<index>\d+)_"                 # 1
    r"(?P<dynamic>[a-z\-]+)_"          # mezzo-piano
    r"(?P<technique>[a-z\-]+)\.mp3"    # non-vibrato
)

def parse_sample_filename(filename):
    m = FILENAME_PATTERN.match(filename)
    if not m:
        return None
    return m.groupdict()

info = parse_sample_filename("cello_A2_1_mezzo-piano_non-vibrato.mp3")
print(info)
