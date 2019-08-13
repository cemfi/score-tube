import os
import tempfile
from enum import Enum, auto

import hug
import jpype
import librosa
from falcon import HTTP_BAD_REQUEST

import youtube
from audio import process_audio
from mei import mei_to_chroma


class Type(Enum):
    YOUTUBE = auto()
    AUDIO = auto()


# enable CORS to prevent browser blocking (Cross-Origin Resource Sharing)
@hug.response_middleware()
def process_data(request, response, resource):
    response.set_header('Access-Control-Allow-Origin', '*')


@hug.post('/align')
def get_alignment(body, response):
    """Calculate alignment of an MEI file to an youtube video or audio file.

    :param body: Form data from HTTP post request.
    :param response: Response header object.
    :return: Dictionary containing IDs of rests and notes as keys and
    their corresponding timing positions in the audio as values.
    """

    ###########################################################################
    # parse incoming request
    ###########################################################################
    if 'mei' not in body:
        response.status = HTTP_BAD_REQUEST
        return 'Please provide MEI file.'

    if 'youtube-url' in body:
        request_type = Type.YOUTUBE
    elif 'audio' in body:
        request_type = Type.AUDIO
    else:
        response.status = HTTP_BAD_REQUEST
        return 'Please provide either a valid YouTube link or an audio file.'

    ###########################################################################
    # save audio track to temporary file
    ###########################################################################
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = os.path.join(temp_dir, 'audio')
        if request_type == Type.YOUTUBE:
            youtube_url = body['youtube-url']
            try:
                youtube.download_audio(youtube_url, audio_path)
            except:  # broad exception clause on purpose!
                response.status = HTTP_BAD_REQUEST
                return 'YouTube video could not be downloaded. Check your network connection and make sure that the YouTube URL is valid.'
        else:  # request_type == Type.AUDIO
            # write audio to temporary file
            with open(audio_path, mode='wb') as audio_file:
                audio_file.write(body['audio'])

        try:
            audio_data, frame_rate, trim_start, _ = process_audio(audio_path)  # process and load audio data as numpy array
        except:
            response.status = HTTP_BAD_REQUEST
            return 'Audio file could not be processed. Make sure that the file format is supported by FFmpeg.'

    ###########################################################################
    # calculate MEI chroma features
    ###########################################################################
    mei_xml = body['mei'].decode('utf-8')
    try:
        chroma_mei, id_to_chroma_index = mei_to_chroma(mei_xml)  # might throw Java exception
    except:  # broad exception clause on purpose!
        response.status = HTTP_BAD_REQUEST
        return 'MEI file could not be processed.'

    ###########################################################################
    # calculate audio chroma features
    ###########################################################################
    chroma_size = round(len(audio_data) / chroma_mei.shape[1])
    chroma_audio = librosa.feature.chroma_stft(y=audio_data, sr=frame_rate, hop_length=chroma_size)

    ###########################################################################
    # calculate warping path
    ###########################################################################
    path = librosa.sequence.dtw(chroma_mei, chroma_audio)[1]
    path_dict = {key: value for (key, value) in path}

    ###########################################################################
    # build and return dictionary {MEI id: time[seconds]}
    ###########################################################################
    id_to_time = {}
    chroma_length = len(audio_data) / frame_rate / chroma_audio.shape[1]
    for id in id_to_chroma_index:
        id_to_time[id] = path_dict[id_to_chroma_index[id]] * chroma_length
        id_to_time[id] += trim_start / 1000  # Offset for trimmed audio in seconds

    return id_to_time  # return result as JSON


# serve static files (web ui)
@hug.static('/')
def user_interface():
    return ('/usr/src/app',)


# configure Java VM in order to use meico
jpype.startJVM(
    jpype.getDefaultJVMPath(),
    '-ea',  # Enable assertions
    '-Djava.class.path=' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meico.jar'),
    convertStrings=True
)

if __name__ == '__main__':
    # start dev server
    hug.API(__name__).http.serve(host='0.0.0.0', port=8001)
