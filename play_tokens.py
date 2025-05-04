import pygame.midi
from music21 import pitch
import time
import re
from fractions import Fraction



def pitchstr_to_num(note_name):
    return pitch.Pitch(note_name).midi

second_per_quarter_note = 0.1 #60 bpm


def pitch_to_midi(pitch):
    match = re.match(r"([A-Ga-g])([-#b]?)(\d)", pitch)
    if not match:
        return None
    name, accidental, octave = match.groups()
    name = name.upper()

    if accidental == '-' or accidental == 'b':
        name += 'b'
    elif accidental == '#':
        name += '#'

    base = pitchstr_to_num(name) - 60 # -60 because it automatically assumes middle c octave. We add octaves later 

    if base is None:
        return None
    midi_number = base + (int(octave) + 1) * 12
    if midi_number is None or midi_number < 0 or midi_number > 127:
        return None

    return midi_number

def play_note(midi_out, midi_note, duration, velocity=127): #velocity means volume. 127 is the max
    midi_out.note_on(midi_note, velocity)
    time.sleep(duration)
    midi_out.note_off(midi_note, velocity)


def quantize_duration(dur_str):
    STANDARD_DURATIONS = [
        Fraction(1, 16), Fraction(1, 32), Fraction(1, 8), Fraction(1, 6), Fraction(1, 4),
        Fraction(1, 3), Fraction(3, 8), Fraction(1, 2), Fraction(2, 3),
        Fraction(3, 4), Fraction(1), Fraction(3, 2), Fraction(2),
        Fraction(3), Fraction(4)
    ]
    try:
        raw = Fraction(dur_str)
        closest = min(STANDARD_DURATIONS, key=lambda x: abs(x - raw))
        return float(closest)
    except Exception:
        return 0.25


def get_duration(dur:str):
    try:
        dur = max(quantize_duration(dur) * 4, 0.125) #turn quarter notes into 1s
    except:
        dur = 1 #default quarter note
    return dur

def play_tokens(tokens, instrument):
    pygame.midi.init()
    player = pygame.midi.Output(0)
    player.set_instrument(instrument)

    i = 0
    while i < len(tokens):
        if tokens[i] == "<simul>":
            i += 1
            print(tokens[i])

            simul_notes = []
            while i < len(tokens) and tokens[i] != "</simul>":
                token = tokens[i]
                match = re.match(r"note(.+)_(\w+)", token)
                if match:
                    pitch, dur = match.groups()
                    midi = pitch_to_midi(pitch)

                    length = get_duration(dur) * second_per_quarter_note

                    if midi is not None:
                        simul_notes.append((midi, length))
                i += 1
                print(tokens[i])

            # Play all simultaneously
            for midi_note, _ in simul_notes:
                player.note_on(midi_note, 100)
            time.sleep(max((d for _, d in simul_notes), default=0.3))
            for midi_note, _ in simul_notes:
                player.note_off(midi_note, 100)
            i += 1  # Skip </simul>
            print(tokens[i])

        else:
            token = tokens[i]
            if token.startswith("note"):
                match = re.match(r"note(.+)_(\w+)", token)
                if match:
                    pitch, dur = match.groups()
                    midi = pitch_to_midi(pitch)
                    length = get_duration(dur) * second_per_quarter_note
                    if midi is not None:
                        play_note(player, midi, length)
            elif token.startswith("rest_"):
                match = re.match(r"rest_(\w+)", token)
                if match:
                    dur = match.group(1)
                    time.sleep(get_duration(dur) * second_per_quarter_note)
            i += 1
            print(tokens[i])
            

    del player
    pygame.midi.quit()


tokens = ['<simul>', 'rest_1/2', 'rest_1/2', '</simul>', '<simul>', 'noteF4_1/2', 'noteG#4_1/2', 'noteF4_1', 'noteG#4_1', '</simul>', '<simul>', 'noteF5_1/2', 'noteG#5_1/2', '</simul>', '<simul>', 'noteF5_3/2', 'noteG#5_3/2', 'noteF4_3', 'noteG#4_3', '</simul>', 'noteF5_1/5', 'noteE-4_171/512', 'noteB6_1/3', 'noteC#6_17/240', 'noteG#2_171/1024', 'noteA3_19/128', 'noteE4_1/2', 'noteC4_1', 'rest_81/16', 'noteB-6_51/512', 'noteG#2_171/1024', 'noteG#5_51/512', 'noteG1_1', 'noteC#2_1/10', 'noteE4_7/8', 'rest_23/8', 'noteG1_1/6', 'noteF#3_51/256', 'noteF#2_1/6', 'noteE-3_23/160', 'noteB3_1/10', 'noteF#6_37/240', 'noteG4_13/96', 'noteG#2_171/1024', 'noteG#3_1/24', 'noteE-7_13/96', 'noteB-6_2/5', 'noteB0_1/2', 'noteA1_1/10', 'noteC#4_341/1024', 'noteG#1_23/160', 'noteG5_1/8', 'noteA3_137/480', 'noteE6_171/512', 'noteC3_85/1024', 'noteC6_307/512', 'noteC#4_57/256', 'noteG#2_171/1024', 'noteG#6_7/4', 'noteE5_65/1024', 'noteG#2_171/1024', 'noteC5_307/512', 'noteD6_1/3', 'noteG#2_171/1024', 'noteB4_37/480', 'noteG5_1/8', 'noteA5_1/4', 'noteG#2_171/1024', 'noteC3_1/3', 'noteD6_1/3', 'noteB-2_1/3', 'rest_81/16', 'noteG1_2', 'noteA1_1/12', 'noteE5_1/2', 'noteG#4_79/1024', 'noteG#2_171/1024', 'noteC3_1/12', 'noteG#2_41/512', 'noteE-3_37/240', 'noteA4_3/8', 'noteD5_0', 'noteC#3_1/10', 'rest_145/96', 'noteE-5_2', 'noteC3_17/160', 'noteC#4_57/256', 'noteG#2_171/1024', 'noteG#6_341/512', 'noteC4_29/160', 'noteB4_617/240', 'noteA6_1/10', 'noteC#3_1/10', 'noteG7_51/1024', 'noteC6_1/6', 'noteB-3_171/1024', 'rest_1/96', 'noteC#1_4', 'noteF#3_51/256', 'noteA6_29/240', 'noteG#1_3/8', 'noteF#3_2/5']
try:
    play_tokens(tokens, 0)
except:
    pygame.midi.quit()

