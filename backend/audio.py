import subprocess

import numpy as np
from pydub import AudioSegment


def _detect_leading_silence(sound, threshold=-40.0, chunk_size=10):
    """Detect silence at beginning of audio data.

    :param sound: pydub.AudioSegment.
    :param threshold: Silence threshold in dB. (Default: -40.0)
    :param chunk_size: Size of audio chunk in ms. (Default: 10)
    :return: Silence duration in ms.
    """

    # iterate over chunks until first one with sound
    trim_ms = 0
    while sound[trim_ms:trim_ms + chunk_size].dBFS < threshold:
        trim_ms += chunk_size

    return trim_ms


def _trim_audio(audio):
    """Remove silence from start and end of audio data.

    :param audio: Audio data.
    :return: Trimmed audio and trimmed durations in ms.
    """

    trim_start = _detect_leading_silence(audio)
    trim_end = _detect_leading_silence(audio.reverse())
    trimmed = audio[trim_start:len(audio) - trim_end]

    return trimmed, trim_start, trim_end


def _convert_to_pcm(input_path, output_path):
    """Extract/convert audio using FFmpeg."""

    cmd = ['ffmpeg',
           '-i', input_path,  # input file
           '-acodec', 'pcm_s16le',  # codec: 16 bit PCM ("Wave")
           '-ac', '1',  # use 1 channel (mono)
           output_path]
    subprocess.call(cmd)


def process_audio(input_path):
    output_path = input_path + '_converted.wav'
    _convert_to_pcm(input_path, output_path)

    audio = AudioSegment.from_file(output_path, format='wav')  # load converted audio file
    trimmed_audio, trim_start, trim_end = _trim_audio(audio)  # trim silence in audio (enhances dynamic time warping)

    audio_data = np.asarray(trimmed_audio.get_array_of_samples(), dtype=np.float)  # convert trimmed audio into numpy array

    return audio_data, audio.frame_rate, trim_start, trim_end
