import math

import jpype
import librosa
import numpy as np
from lxml import etree


def mei_to_chroma(mei_xml):
    """Generate timestamps for all notes and rests of the MEI file using the Java framework meico.

    :param mei_xml: String containing the MEI XML data.
    :return: MEI string with included timestamps.
    """

    mei = jpype.JPackage('meico').mei.Mei(mei_xml, False)  # read in MEI data in meico
    mei.addIds()  # add unique IDs in case they are omitted
    mei.exportMsm(720, True, False)  # generate timestamps with ppq=720, no channel 10, no cleanup
    meico_xml = mei.toXML()

    return _meico_to_chroma(meico_xml)


def _meico_to_chroma(meico_xml):
    """Convert meico MEI XML data to chromagram."

    :param meico_xml: String containing the MEI XML data, including additional data calculated by meico.
    :return: Chromagram and dictionary with MEI IDs to chromagram indices.
    """
    # parse XML data
    parser = etree.XMLParser(collect_ids=False)
    meico_xml = etree.fromstring(meico_xml, parser=parser)

    shortest_duration = np.inf
    highest_date = 0
    notes_and_rests = {}
    id_to_chroma_index = {}

    # iterate through all rests and notes and extract pitch, date, and duration
    for elem in meico_xml.xpath('//*[local-name()="note"][@midi.dur]|//*[local-name()="rest"][@midi.dur]'):
        identifier = elem.get('{http://www.w3.org/XML/1998/namespace}id')

        pitch = (int(float(elem.get('pnum'))) if elem.tag == '{http://www.music-encoding.org/ns/mei}note' else None)
        date = float(elem.get('midi.date'))
        dur = float(elem.get('midi.dur'))

        # put all relevant data in dictionary for easier lookup (xpath calls are expensive!)
        notes_and_rests[identifier] = {}
        notes_and_rests[identifier]['pitch'] = pitch
        notes_and_rests[identifier]['date'] = date
        notes_and_rests[identifier]['dur'] = dur

        shortest_duration = min(shortest_duration, dur)  # save shortest note duration for grid resolution of chroma matrix
        highest_date = max(highest_date, date + dur)  # save overall length of score file

    # init chromagram matrix with zeros
    chroma_matrix = np.zeros((12, int(highest_date / shortest_duration)), dtype=np.float16)

    # add chroma feature for every note to matrix
    for elem in notes_and_rests:
        note_or_rest = notes_and_rests[elem]
        begin = math.floor(note_or_rest['date'] / shortest_duration)
        id_to_chroma_index[elem] = begin
        if note_or_rest['pitch'] is not None:  # only notes (pitch != None)
            end = math.ceil((note_or_rest['date'] + note_or_rest['dur']) / shortest_duration)
            try:
                chroma_matrix[note_or_rest['pitch'] % 12, begin:end] += 1
            except IndexError:  # ignore errors resulting from rounding in `end = math.ceil(...)`
                pass

    # normalize each chroma feature independently
    chroma_matrix = librosa.util.normalize(chroma_matrix)

    return chroma_matrix, id_to_chroma_index
