# GronkhTV-Downloader

A simple python-written CLI tool to download videos from https://gronkh.tv without re-encoding.  
Doesn't require anything but an up-to-date Python version.

## Example usage:

First, get the episode id from https://gronkh.tv - e.g. for https://gronkh.tv/streams/703?at=5h13m28s the episode id is `703`.

Download a complete stream in the default format (720p):
```
./gtv-dl.py 703 --download gronkhtv-ep-703.ts
```

Download only minute 10 to 12:
```
./gtv-dl.py 703 --download gronkhtv-ep-703.ts --start 00:10:00 --stop 00:12:00
```

List available formats:
```
./gtv-dl.py 703 --list-formats
```

Download the first minute of the video in a specific format (in this case, FullHD at 60fps):
```
./gtv-dl.py 703 --download gronkhtv-ep-703.ts --stop 00:01:00 --format 1080p60
```

Get some help:
```
./gtv-dl.py --help
```