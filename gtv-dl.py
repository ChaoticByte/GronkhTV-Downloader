#!/usr/bin/env python3

# Copyright (c) 2023 Julian Müller (ChaoticByte)

import re

from argparse import ArgumentParser
from gzip import decompress
from json import loads
from os import get_terminal_size, linesep, remove, stat
from os.path import exists
from string import ascii_letters, digits
from sys import stdout
from time import strptime
from unicodedata import normalize as normalize_unicode
from urllib import request as _request


def request_get(url: str, headers: dict = {}) -> bytes:
    '''Gets data and decodes gzip-compressed responses'''
    req = _request.Request(
        url,
        headers=headers)
    with _request.urlopen(req) as resp:
        response_data = resp.read()
        if resp.headers["Content-Encoding"] == "gzip":
            return decompress(response_data)
        else:
            return response_data

def rule(char:str="="):
    for i in range(get_terminal_size().columns - 1):
        stdout.write(char)
    stdout.write(linesep)
    stdout.flush()

def sanitize_unicode_filepath(filepath: str):
    # normalize unicode string
    filename_unfiltered = normalize_unicode("NFKD", filepath)
    # find all unicode characters
    unicode_chars = ""
    for char in filename_unfiltered:
        if str(char.encode("unicode-escape"))[2] == '\\' and not char in unicode_chars:
            unicode_chars += char
    # build allowlist
    allowed = ascii_letters + digits + "_-!,.@+# " + unicode_chars
    # filter
    filename = ""
    for char in filename_unfiltered:
        if char in allowed:
            filename += char
        else:
            filename += "_"
    return filename.strip()

class GTVideoStream:

    _CDN_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip", # must be gzip
        "Origin": "https://gronkh.tv",
        "Referer": "https://gronkh.tv/",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers"
    }

    def __init__(self, baseurl: str, chunks: list, chunk_duration: float):
        assert type(baseurl) == str
        assert type(chunks) == list
        assert type(chunk_duration) == float
        self.baseurl = baseurl
        self.chunks = chunks
        self.chunk_duration = chunk_duration
    
    def calculate_chunk_from_timestamp(self, timestamp:str) -> int:
        assert type(timestamp) == str
        # convert to seconds
        parsed_timestamp = strptime(timestamp, "%H:%M:%S")
        seconds = (
            parsed_timestamp.tm_hour * 60 * 60 +
            parsed_timestamp.tm_min * 60 +
            parsed_timestamp.tm_sec)
        # calculate chunk
        chunk = int(seconds / self.chunk_duration)
        return chunk

    @classmethod
    def from_m3u8_url(cls, m3u8_url: str):
        assert type(m3u8_url) == str
        # Get baseurl (remove last path component)
        baseurl = m3u8_url[:m3u8_url.rfind("/") + 1]
        # Get chunks & chunk duration
        m3u8_data = request_get(m3u8_url).decode()
        m3u8_data_lines = m3u8_data.splitlines()
        chunk_duration = None
        chunks = []
        for idx, line in enumerate(m3u8_data_lines):
            if line.startswith("#EXT-X-TARGETDURATION:"):
                chunk_duration = float(line.split(":")[1])
            elif line.startswith("#EXTINF:"):
                if len(m3u8_data_lines) <= idx + 1:
                    continue # url not specified
                chunks.append(m3u8_data_lines[idx + 1])
        if chunk_duration is None or chunks == []:
            raise Exception("Couldn't find any chunks or chunk duration.")
        return cls(baseurl, chunks, chunk_duration)

    def download_chunks(self, start: int = 0, stop: int = -1) -> bytes:
        if stop == -1:
            stop = len(self.chunks)
        for c in self.chunks[start:stop]:
            yield request_get(self.baseurl + c, self._CDN_HEADERS)


class GTVEpisodeDownloader:

    _GTV_EP_BASEURL = "https://gronkh.tv/streams/{episode}"
    _API_URL_INFO = "https://api.gronkh.tv/v1/video/info?episode={episode}"
    _API_URL_PLAYLIST = "https://api.gronkh.tv/v1/video/playlist?episode={episode}"
    _API_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip", # must be gzip
        "Origin": "https://gronkh.tv",
        "Connection": "keep-alive",
        "Referer": "https://gronkh.tv/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers"
    }

    def __init__(self, episode: int):
        assert type(episode) == int
        self.episode = episode
        # avaliable formats
        self.formats = None
        # info
        self.info = None

    def _parse_avail_formats_from_m3u8(self, m3u8_data:str) -> dict:
        '''A dumb m3u8 parser that returns the available formats in the following style:
            {
                "720p": "https://01.cdn.vod.farm/transcode/7709820a1d7736ba3db6569df77632db/720p30/46caf415b9b9a5790395935cb28439c6.m3u8",
                "360p": "https://01.cdn.vod.farm/transcode/7709820a1d7736ba3db6569df77632db/360p30/45bc2e1f4c2df5448542b0b7b6a73b3d.m3u8"
            }
        '''
        assert type(m3u8_data) == str
        found_formats = {}
        input_m3u8_lines = m3u8_data.splitlines()
        for idx, line in enumerate(input_m3u8_lines):
            if line.startswith("#EXT-X-STREAM-INF") and "RESOLUTION=" in line and "FRAMERATE=" in line and "NAME=" in line:
                format_name_re = re.search(r"NAME=\"(.*?)\"", line)
                if format_name_re is None:
                    continue # couldn't find format name
                format_name = format_name_re.group(1)
                if len(m3u8_data) <= idx + 1:
                    continue # url not specified
                format_url = input_m3u8_lines[idx+1]
                found_formats[format_name] = format_url
        return found_formats

    def _gtv_get_info(self) -> tuple:
        '''sets self.info to a tuple containing (title, filename)'''
        # Get title from API
        api_url_info_ep = self._API_URL_INFO.format(episode=self.episode)
        title = loads(request_get(api_url_info_ep, self._API_HEADERS))["title"]
        filename = sanitize_unicode_filepath(title)
        filename += ".ts"
        self.info = (title, filename)

    def _gtv_get_formats(self):
        # Get formats from the API
        api_url_pl_ep = self._API_URL_PLAYLIST.format(episode=self.episode)
        cdn_url_pl_avail_streams = loads(request_get(api_url_pl_ep, self._API_HEADERS))["playlist_url"]
        avail_formats_m3u8 = request_get(cdn_url_pl_avail_streams, GTVideoStream._CDN_HEADERS).decode()
        self.formats = self._parse_avail_formats_from_m3u8(avail_formats_m3u8)

    def print_title(self):
        self.get_meta()
        rule()
        print(self.info[0])
        rule()

    def download(self, output_filepath: str, desired_format: str, start_timestamp: str = None, stop_timestamp: str = None, overwrite: bool = False):
        assert type(output_filepath) == str or output_filepath is None
        assert type(desired_format) == str
        assert type(start_timestamp) == str or start_timestamp == None
        assert type(stop_timestamp) == str or stop_timestamp == None
        assert type(overwrite) == bool
        # Query metadata (info and formats)
        self.get_meta()
        # Check if desired format is available
        if desired_format not in self.formats:
            raise Exception(f"Format {desired_format} not found. You can list available formats with --list-formats")
        # Get GTVideoStream object from m3u8
        video_stream = GTVideoStream.from_m3u8_url(self.formats[desired_format])
        # Get start and stop idx
        if start_timestamp is None:
            start = 0
        else:
            start = video_stream.calculate_chunk_from_timestamp(start_timestamp)
        if stop_timestamp is None:
            stop = len(video_stream.chunks)
        else:
            stop = video_stream.calculate_chunk_from_timestamp(stop_timestamp)
        # Get video filename
        if output_filepath is None:
            output_filepath = self.info[1]
        info_output_filepath = f"{output_filepath}.gtv-dl-info"
        # Set current chunk offset
        current_dl_offset = 0
        if exists(info_output_filepath) and not overwrite:
            with open(info_output_filepath, "r") as info:
                info_data = info.read()
                if info_data != "":
                    current_dl_offset = min(max(int(info_data), 0), stop-start)
        # Download
        with open(output_filepath, "a+b") as o:
            # Download
            if exists(output_filepath) and (overwrite or stat(output_filepath).st_size == 0):
                # Only truncate the file to 0 when it's being overwritten
                o.truncate(0)
            elif exists(output_filepath) and current_dl_offset == 0:
                o.close()
                exit("Error. The file already exists and the download can not be continued.")
            with open(info_output_filepath, "w") as info:
                try:
                    # download & write the data
                    if current_dl_offset > 0:
                        print(f"Continuing download to \"{output_filepath}\"")
                    else:
                        print(f"Downloading to \"{output_filepath}\"")
                    print(f"Format: {desired_format}")
                    rule()
                    for c in video_stream.download_chunks(start + current_dl_offset, stop):
                        current_dl_offset += 1
                        # calculate & print progress
                        pct = current_dl_offset / (stop - start) * 100
                        print(f"\r{pct:05.2f}%", end="")
                        # Write data
                        o.write(c)
                        # Write info data
                        info.seek(0)
                        info.write(str(current_dl_offset))
                        info.truncate()
                    o.flush()
                    print(" done.")
                except KeyboardInterrupt:
                    # Ensure that the data is flushed
                    o.flush()
                    o.close()
                    info.flush()
                    info.close()
                    exit("Received KeyboardInterrupt")
                remove(info_output_filepath)

    def get_meta(self):
        if self.info is None:
            self._gtv_get_info()
        if self.formats is None:
            self._gtv_get_formats()


if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument("episode", type=int, help="The ID of that episode, e.g. 703 for https://gronkh.tv/streams/703")
    ap.add_argument("--list-formats", help="List available formats without downloading", action="store_true")
    ap.add_argument("--download-to", metavar="filepath", type=str, help="Download the video to this file (should end with .ts), e.g. gronkh703.ts", default=None)
    ap.add_argument("--format", metavar="format", type=str, help="The format to download, default is 720p", default="720p")
    ap.add_argument("--start", metavar="timestamp", type=str, help="At which timestamp to start downloading, e.g. at 01:00:00", default=None)
    ap.add_argument("--stop", metavar="timestamp", type=str, help="At which timestamp to stop downloading, e.g. at 02:50:12", default=None)
    ap.add_argument("--overwrite", help="Overwrite the file if it already exists", action="store_true")
    args = ap.parse_args()
    # Create an instance of a GTVEpisodeDownloader
    v = GTVEpisodeDownloader(args.episode)
    # do stuff with it
    did_something = False
    if args.list_formats:
        did_something = True
        v.print_title()
        v.get_meta()
        print("Found the following formats:")
        if v.formats == {}:
            print("Couldn't find any format.")
        else:
            for k in v.formats:
                print(f" - {k}")
    else:
        did_something = True
        v.print_title()
        v.download(args.download_to, args.format, args.start, args.stop, args.overwrite)
    if not did_something:
        ap.print_usage()
