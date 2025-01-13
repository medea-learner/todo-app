#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import argparse
import os

import numpy as np
import shlex
import subprocess
import sys
import wave
import json

from deepspeech import Model, version
from timeit import default_timer as timer

try:
    from shhlex import quote
except ImportError:
    from pipes import quote

model = "deepspeech-0.9.3-models.pbmm"

print('Loading model from file {}'.format(model), file=sys.stderr)
model_load_start = timer()
# sphinx-doc: python_ref_model_start
ds = Model(model)
# sphinx-doc: python_ref_model_stop
model_load_end = timer() - model_load_start
print('Loaded model in {:.3}s.'.format(model_load_end), file=sys.stderr)


def convert_samplerate(audio_path, desired_sample_rate):
    sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - '.format(quote(audio_path), desired_sample_rate)
    try:
        output = subprocess.check_output(shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError('SoX returned non-zero status: {}'.format(e.stderr))
    except OSError as e:
        raise OSError(e.errno, 'SoX not found, use {}hz files or install it: {}'.format(desired_sample_rate, e.strerror))

    return desired_sample_rate, np.frombuffer(output, np.int16)


def metadata_to_string(metadata):
    return ''.join(token.text for token in metadata.tokens)


def words_from_candidate_transcript(metadata):
    word = ""
    word_list = []
    word_start_time = 0
    # Loop through each character
    for i, token in enumerate(metadata.tokens):
        # Append character to word if it's not a space
        if token.text != " ":
            if len(word) == 0:
                # Log the start time of the new word
                word_start_time = token.start_time

            word = word + token.text
        # Word boundary is either a space or the last character in the array
        if token.text == " " or i == len(metadata.tokens) - 1:
            word_duration = token.start_time - word_start_time

            if word_duration < 0:
                word_duration = 0

            each_word = dict()
            each_word["word"] = word
            each_word["start_time"] = round(word_start_time, 4)
            each_word["duration"] = round(word_duration, 4)

            word_list.append(each_word)
            # Reset
            word = ""
            word_start_time = 0

    return word_list


def metadata_json_output(metadata):
    json_result = dict()
    json_result["transcripts"] = [{
        "confidence": transcript.confidence,
        "words": words_from_candidate_transcript(transcript),
    } for transcript in metadata.transcripts]
    return json.dumps(json_result, indent=2)


class VersionAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        super(VersionAction, self).__init__(nargs=0, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        print('DeepSpeech ', version())
        exit(0)


def speech2text(audio_path, beam_width=None, scorer="deepspeech-0.9.3-models.scorer",
                lm_alpha=None, lm_beta=None, version=None, extended=None, json_=None, candidate_transcripts=3,
                hot_words=None, remove_audio=False):
    """
    :param audio_path: Path to the audio file to run (WAV format)
    :param model: Path to the model (protocol buffer binary file)
    :param beam_width: Beam width for the CTC decoder
    :param scorer: Path to the external scorer file
    :param lm_alpha: Language model weight (lm_alpha). If not specified, use default from the scorer package.
    :param lm_beta: Word insertion bonus (lm_beta). If not specified, use default from the scorer package.
    :param version: Print version and exits
    :param extended: Output string from extended metadata
    :param json_: Output json from metadata with timestamp of each word
    :param candidate_transcripts: Number of candidate transcripts to include in JSON output
    :param hot_words: Hot-words and their boosts.
    :param remove_audio: Remove audio
    :return:
    """

    if beam_width:
        ds.setBeamWidth(beam_width)

    desired_sample_rate = ds.sampleRate()

    if scorer:
        print('Loading scorer from files {}'.format(scorer), file=sys.stderr)
        scorer_load_start = timer()
        ds.enableExternalScorer(scorer)
        scorer_load_end = timer() - scorer_load_start
        print('Loaded scorer in {:.3}s.'.format(scorer_load_end), file=sys.stderr)

        if lm_alpha and lm_beta:
            ds.setScorerAlphaBeta(lm_alpha, lm_beta)

    if hot_words:
        print('Adding hot-words', file=sys.stderr)
        for word_boost in hot_words.split(','):
            word, boost = word_boost.split(':')
            ds.addHotWord(word, float(boost))

    fin = wave.open(audio_path, 'rb')
    fs_orig = fin.getframerate()
    if fs_orig != desired_sample_rate:
        print(f'Warning: original sample rate ({fs_orig}) is different than {desired_sample_rate}hz. ', file=sys.stderr)
        fs_new, audio = convert_samplerate(audio_path, desired_sample_rate)
    else:
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

    fin.close()

    if remove_audio:
        os.remove(audio_path)

    if extended:
        return metadata_to_string(ds.sttWithMetadata(audio, 1).transcripts[0])
    elif json_:
        return metadata_json_output(ds.sttWithMetadata(audio, candidate_transcripts))
    else:
        return ds.stt(audio)


if __name__ == '__main__':
    print(speech2text("./temp.wav", scorer=None))
