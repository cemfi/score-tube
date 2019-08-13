import math
import multiprocessing as mp

import requests

from pytube import YouTube  # local version -> able to fix things quickly in case youtube changes stuff


def download_audio(video_url, path):
    """Download audio from YouTube video using multiple connections in parallel.

    :param video_url: YouTube video url.
    :param path: Destination path for downloaded audio track.
    """

    stream = YouTube(video_url).streams.get_by_itag(249)  # 249 = <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus">
    url = stream.url  # get direct download url
    filesize = stream.filesize

    # split filesize in chunks
    CHUNK_SIZE = 3 * 2 ** 20  # in bytes
    ranges = [[url, i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE - 1] for i in range(math.ceil(filesize / CHUNK_SIZE))]
    ranges[-1][2] = None  # last range must be to the end of file, so it will be marked as None

    pool = mp.Pool(min(len(ranges), 64))  # worker pool for multiprocessing
    chunks = [0 for _ in ranges]  # init list of chunks

    # download chunks
    for i, chunk_tuple in enumerate(pool.imap_unordered(_download_chunk, enumerate(ranges)), 1):
        idx, chunk = chunk_tuple
        chunks[idx] = chunk

    # write chunks to final file
    with open(path, 'wb') as outfile:
        for chunk in chunks:
            outfile.write(chunk)


def _download_chunk(args):
    """Download a single chunk.

    :param args: Tuple consisting of (url, start, finish) with start and finish being byte offsets.
    :return: Tuple of chunk id and chunk data
    """
    idx, args = args
    url, start, finish = args
    range_string = '{}-'.format(start)

    if finish is not None:
        range_string += str(finish)

    response = requests.get(url, headers={'Range': 'bytes=' + range_string})  # Actual HTTP get download request
    return idx, response.content
