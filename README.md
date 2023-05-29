# GronkhTV-Downloader

A simple python-written CLI tool to download videos from https://gronkh.tv without re-encoding.  
Doesn't require anything but an up-to-date Python version. Tested on Linux (Ubuntu 22.04, Arch Linux) and Windows (Powershell) with Python 3.10 and 3.11.  
Aborted downloads will be continued automatically.

## Usage

```
gtv-dl.py [-h]
          [--list-formats]
          [--download-to filepath]
          [--format format]
          [--start timestamp]
          [--stop timestamp]
          [--overwrite]
          episode

positional arguments:

  episode               The ID of that episode, e.g. 703 for
                        https://gronkh.tv/streams/703

options:

  -h, --help             show this help message and exit
  --list-formats         List available formats without downloading
  --download-to filepath Download the video to this file (should end with .ts),
                         e.g. gronkh703.ts
  --format format        The format to download, default is 720p
  --start timestamp      At which timestamp to start downloading,
                         e.g. at 01:00:00
  --stop timestamp       At which timestamp to stop downloading,
                         e.g. at 02:50:12
  --overwrite            Overwrite the file if it already exists

```

### Examples

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

## Example usage on Windows (Powershell)

```
& python3 .\gtv-dl.py 700 --start 00:10:00 --stop 00:12:00
================================================================================
GTV0700, 2023-03-03 - #FREiAB18 □ Oder 24/7 auf @GronkhTV □ !archiv !horde2
================================================================================
Downloading to "GTV0700, 2023-03-03 - #FREiAB18 □ Oder 24_7 auf @GronkhTV □ !arc
hiv !horde2.ts"
Format: 720p
================================================================================
100.00%
```
