# GronkhTV-Downloader

A simple python-written CLI tool to download videos from https://gronkh.tv without re-encoding.  
Doesn't require anything but an up-to-date Python version (3.10). Tested on Linux (Ubuntu 22.04) and Windows (Powershell).

## Example usage

First, get the episode id from https://gronkh.tv - e.g. for https://gronkh.tv/streams/700?at=5h13m28s the episode id is `700`.

Download the complete stream in the default format (720p) using the title as the filename:
```
./gtv-dl.py 700

================================================================================
GTV0700, 2023-03-03 - #FREiAB18 ⭐ Oder 24/7 auf @GronkhTV ⭐ !archiv !horde2
================================================================================
Downloading to "GTV0700, 2023-03-03 - #FREiAB18 ⭐ Oder 24_7 auf @GronkhTV ⭐ !a
rchiv !horde2.ts"
Format: 720p
================================================================================
100.00%
```

Download only minute 10 to 12 and write the video file to `~/gronkhtv-ep-700.ts`:
```
./gtv-dl.py 700 --start 00:10:00 --stop 00:12:00 --download-to ~/gronkhtv-ep-700.ts

================================================================================
GTV0700, 2023-03-03 - #FREiAB18 ⭐ Oder 24/7 auf @GronkhTV ⭐ !archiv !horde2
================================================================================
Downloading to "/home/julian/gronkhtv-ep-700.ts"
Format: 720p
================================================================================
100.00%
```

Download the episode in a specific format (in this case, FullHD at 60fps):
```
./gtv-dl.py 700 --format 1080p60

================================================================================
GTV0700, 2023-03-03 - #FREiAB18 ⭐ Oder 24/7 auf @GronkhTV ⭐ !archiv !horde2
================================================================================
Downloading to "GTV0700, 2023-03-03 - #FREiAB18 ⭐ Oder 24_7 auf @GronkhTV ⭐ !a
rchiv !horde2.ts"
Format: 1080p60
================================================================================
100.00%
```

List available formats:
```
./gtv-dl.py 700 --list-formats

================================================================================
GTV0700, 2023-03-03 - #FREiAB18 ⭐ Oder 24/7 auf @GronkhTV ⭐ !archiv !horde2
================================================================================
Found the following formats:
 - 1080p60
 - 720p
 - 360p
```

Get some help:
```
./gtv-dl.py --help
```
