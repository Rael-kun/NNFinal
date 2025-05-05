import pygame.midi
from music21 import pitch
import time
import re
from fractions import Fraction



def pitchstr_to_num(note_name):
    return pitch.Pitch(note_name).midi


BPM = 480 ##################################################### REALLY FAST FOR NOW, JUST TESTING PURPOSES
second_per_quarter_note = 60 / BPM


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

    base = pitchstr_to_num(name) - 60 #See the NOTE_TO_MIDI dictionary. -60 because it automatically assumes middle c octave. We add octaves later 

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

def quantize_duration(dur_str: str):
    STANDARD_DURATIONS = [ #what length of fractions do we allow?
        Fraction(1, 16), Fraction(1, 8), Fraction(1, 6), Fraction(1, 4),
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
        dur = max(quantize_duration(dur) * 4, 0.125) #turn quarter notes into 1s, minimum time is 1/8 of a quarter note (ie 1/32)
    except:
        dur = 1 #default quarter note
    return dur

def play_tokens(tokens, instrument):
    pygame.midi.init()
    player = pygame.midi.Output(0)
    player.set_instrument(instrument)

    i = 0
    while i < len(tokens):

        #SIMULTANEOUS HANDLING
        if tokens[i] == "<simul>":
            beginning = i
            i += 1

            simul_notes = []
            while i < len(tokens) and tokens[i] != "</simul>" and i - beginning < 7: #Cannot be more than 7 notes played simultaneously
                token = tokens[i]
                match = re.match(r"note(.+)_(\w+)", token)
                if match:
                    pitch, dur = match.groups()
                    midi = pitch_to_midi(pitch)

                    length = get_duration(dur) * second_per_quarter_note

                    if midi is not None:
                        simul_notes.append((midi, length))
                i += 1

            

            # Play all simultaneously
            for midi_note, _ in simul_notes:
                player.note_on(midi_note, 100)

            time.sleep(max((d for _, d in simul_notes), default=0.3))

            for midi_note, _ in simul_notes:
                player.note_off(midi_note, 100)
            i += 1  # Skip </simul>


        #NONSIMULTANEOUS HANDLING
        else:
            token = tokens[i]

            #NOTES
            if token.startswith("note"):
                match = re.match(r"note(.+)_(\w+)", token)
                if match:
                    pitch, dur = match.groups()
                    midi = pitch_to_midi(pitch)
                    length = get_duration(dur) * second_per_quarter_note
                    if midi is not None:
                        play_note(player, midi, length)

            #RESTS
            elif token.startswith("rest_"):
                match = re.match(r"rest_(\w+)", token)
                if match:
                    dur = match.group(1)
                    time.sleep(get_duration(dur) * second_per_quarter_note)

            i += 1
            

    del player
    pygame.midi.quit()

#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
#                                     PLAY TOKENS
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------

notes = ['</simul>', 'noteB-5_1/2', '<simul>', 'noteE6_1/2', 'noteA1_3', 'rest_1/4', 'noteC5_2', '</simul>', '<simul>', 'noteG5_2', 'noteD6_2', 'noteG4_2', 'rest_3/8', '</simul>', 'noteC3_1/3', 'rest_1/4', '<simul>', 'noteE-4_1/2', 'noteC5_1/3', 'noteB-2_1', '</simul>', '<simul>', 'noteG#3_1/16', 'noteC3_3', 'noteG2_3', 'noteG5_3', 'noteC5_3', 'noteC6_3', 'noteB-3_3', 'noteC3_3', '</simul>', '<simul>', 'noteG5_3', 'noteG3_2', 'noteG1_1', 'noteA5_1/16', 'noteB2_1/16', 'noteC5_3', 'noteB4_3', 'noteG4_3', '</simul>', '<simul>', 'noteA5_1/16', 'noteE5_3', 'noteG5_3', 'noteG3_3', 'noteG4_3', 'noteC5_3', 'noteC5_3', 'noteB5_3', 'noteC#5_3', 'noteG4_1/2', 'noteB3_1/3', 'noteC5_3', 'noteD5_3', 'noteB5_2/3', 'noteG5_3', 'noteG3_3', '</simul>', 'noteG4_1/2', '<simul>', 'noteC5_3', 'noteE5_3', 'noteB4_3', 'noteG4_1/3', 'noteG3_3', 'noteB-3_3', 'noteG2_3', 'noteC5_3', 'noteC#5_3', 'noteG1_1', 'noteC3_2', '</simul>', '<simul>', 'noteD5_3', 'noteC5_3', 'noteG4_3', 'noteG3_3', '</simul>', '<simul>', 'noteC#5_3', 'noteD2_1', '</simul>', 'noteB-3_4', 'noteB-3_3', 'noteD5_1/16', 'noteA2_4', 'noteG3_3', '</simul>', '<simul>', 'noteC5_3', 'noteE-1_1', 'noteB-2_3', 'noteF2_1', '</simul>', '<simul>', 'noteG3_3', 'noteC#4_3', 'noteB4_3', 'noteG3_3', '</simul>', '<simul>', 'noteG4_3', 'noteG3_3', 'noteB-3_3', 'noteD4_3', 'noteC5_3', 'noteC4_3', 'noteD3_3', 'noteG3_3', 'noteB-3_3', 'noteG4_3', 'noteB1_2', 'noteG2_3/2', 'noteG2_3', 'noteG3_3', 'noteB-3_3', '</simul>', '<simul>', 'noteF#2_1', 'noteC3_3', 'noteD3_2', 'noteD4_2', 'noteG3_3', 'noteB-2_3', 'noteD3_3', 'noteB-3_3', 'noteC#4_3', '</simul>', '<simul>', 'noteG1_3', 'noteG2_3', 'noteB-2_3', 'noteD3_3', 'noteG3_3', 'noteC3_3', 'noteB-1_1', 'noteB-3_3', 'noteE4_3', 'noteB-2_3', 'noteG3_3', 'noteC#4_3', 'noteB1_1', 'noteF3_3/2', 'noteA3_3/2', 'noteC3_3', 'noteG2_3', 'noteB-3_3', 'noteC#3_3', 'noteG3_3', 'noteC#3_3', 'noteF3_3', 'noteB-3_3', 'noteC3_3', 'rest_2', '</simul>', '<simul>', 'noteB-1_1', 'noteG3_3', 'noteB-3_3', 'noteG#3_3', 'noteC#4_3', 'noteF3_1', 'noteB-2_3', 'noteG3_3', 'noteC#3_3', 'noteG#3_3', 'noteG2_3', 'noteC2_3', 'noteG2_3', 'noteB-1_3', 'noteG3_3', 'noteC#4_3', 'noteC3_3', 'noteF4_3', 'noteB-3_3', 'noteC3_3', 'noteF3_3', 'noteG3_3', 'noteG2_3', 'noteB-2_3', 'noteD3_3', 'noteB-3_3', 'noteC3_3', 'noteF#3_3', 'noteC4_3', 'noteF4_3', 'noteG4_3', 'noteE4_3', 'noteB-2_3', 'noteC3_3', 'noteC3_3', 'noteG3_3', 'noteC4_3', 'noteF3_1', 'noteB-2_3/2', 'noteG2_3', 'noteG3_3', 'noteB-3_3', 'noteC#4_3', 'noteC3_3', 'noteE-3_3', 'noteG2_3', 'noteD3_3', 'noteB-3_3', 'noteC#4_3', 'noteB-2_3', 'noteG3_3', 'noteE4_3', 'noteC3_3', 'noteB-3_3', '</simul>', '<simul>', 'noteB-2_3', 'noteB-3_1', 'noteG3_3', 'noteC3_3', 'noteB-3_3', 'noteB-1_3', 'noteB-2_3', 'noteC5_3', 'noteG3_3', 'noteC3_3', '</simul>', '<simul>', 'noteE-3_3', 'noteC3_3', 'noteF#3_3', 'noteB-2_3', 'noteG2_3', 'noteB-1_3', 'noteG#2_3', 'noteD3_3/2', 'noteB-2_3/2', 'noteG2_3', 'noteC3_3', 'noteE-3_3', 'noteG3_3', 'noteB-3_3', 'noteB-2_3', 'noteG4_3', 'noteC3_3', '</simul>', '<simul>', 'noteB-3_3', 'noteC3_3', 'noteB-2_3', 'noteC3_3', 'noteE-3_3', 'noteD3_3', 'noteC5_3', 'noteG2_3', 'noteB-2_3', '</simul>', '<simul>', 'noteB-3_3', 'noteB-2_3', 'noteC#3_3', 'noteG2_3', 'noteB-2_3', 'noteC3_3', 'noteG#2_3', '</simul>', '<simul>', 'noteB-1_3', 'noteB-2_3', 'noteC3_3', 'noteC3_3', 'noteF#3_3', 'noteB-2_3/2', 'noteE3_3/2', 'noteB-3_3', 'noteC3_3', 'noteC3_3', 'noteB-2_3', 'noteC#3_3', 'noteB-2_3', 'noteD3_3', 'noteF2_2', 'noteC3_3', 'noteF#3_3', 'noteG#2_3', 'noteG2_3', 'noteB-2_3', 'noteC#4_3', 'noteD3_3', 'noteB-1_3', 'noteB-2_3', 'noteC3_3', 'noteG4_3', 'noteG2_3', 'noteB-3_3', 'noteE4_3', 'noteC5_3', 'noteB-2_3', 'noteG3_3', 'noteC3_3', 'noteC3_3', 'noteF#3_3', 'noteE-3_3', 'noteG2_3', 'noteG3_3', 'noteC#4_3', 'noteB-1_3', 'noteB-2_3', 'noteG#3_3', 'noteG2_3', 'noteC3_3', 'noteF3_3', 'noteB-3_2', 'noteB-2_3', 'noteG#2_3', '</simul>', '<simul>', 'noteC4_3', 'noteE-4_3', 'noteB-1_3', 'noteB-2_3', 'noteG2_3', 'noteB-2_3', 'noteC3_3', 'noteC3_3', '</simul>', '<simul>', 'noteB-3_3', 'noteC#4_3', 'noteB-2_3', 'noteD3_3', 'noteF3_3', 'noteC#3_3', 'noteE-1_3', 'noteE-2_3', 'noteC3_3', 'noteC3_3', 'noteB-2_3', 'noteB-3_3', 'noteG3_3', 'noteC#4_3', 'noteC3_3', 'noteE-3_3', 'noteB-3_2', 'noteB-2_3', 'noteB-3_3', 'noteF4_3', 'noteB-2_3', 'noteG#2_3', 'noteG2_3', 'noteG3_3', 'noteC#4_3', 'noteB-2_3', 'noteF3_3', 'noteE-2_3/2', 'noteB-2_3/2', 'noteC3_3', 'noteB2_3', '</simul>', 'noteF3_1/2', 'noteB-2_3', 'noteG5_3', 'noteG#2_3', 'noteC3_3', 'noteE-3_3', 'noteG3_3', 'noteF2_3', 'noteE-3_1/2', 'noteD3_3', 'noteB-2_3', 'noteC3_3', '</simul>', '<simul>', 'noteE-4_3', 'noteB-2_3', 'noteF#1_3', 'noteB-2_3', 'noteC3_3', 'noteG2_3', 'noteG#3_3', 'noteE-3_3', 'noteB-3_3', 'noteE-4_3', 'noteC3_3', 'noteB-2_3', '</simul>', '<simul>', 'noteB-3_3', 'noteG2_3', 'noteC3_3', 'noteB-2_3', 'noteD3_3', 'noteB-2_3', 'noteG#3_3', 'noteE-4_3', 'noteE-1_3', 'noteE-2_3', 'noteC3_3', 'noteF#3_3', 'noteB-2_3', 'noteC#3_3', 'noteB-3_3', 'noteB-2_3', 'noteG3_3', '</simul>', 'noteE-1_3', 'noteE-2_3', 'noteD3_1/16', 'noteB-2_3', 'noteA3_3/2', 'noteC3_3', 'noteC3_3/2', 'noteB-2_3/2', '</simul>', 'noteB1_1/16', 'noteB-2_3', 'noteC3_3', 'noteE-3_3', 'noteC3_3', 'noteB-3_3', 'noteA3_3/2', 'noteG2_3', 'noteB-2_3', 'noteF3_3', 'noteB-2_3', 'noteG#3_3', 'noteF3_1', 'noteG2_3', 'noteC3_3', 'noteB-2_3', 'noteB-3_3', 'noteB-2_3', 'noteD3_3', 'noteG#3_3', 'noteG2_3', 'noteC4_3', 'noteE-4_3', 'noteB-2_3', 'noteC3_3', 'noteG2_3', 'noteG#3_3', 'noteB-1_3', 'noteE-1_3', 'noteE-2_3', 'noteB-2_3', 'noteE-4_3', 'noteC3_3', 'noteG3_3', 'noteE4_3', 'noteF#2_3', '</simul>', 'noteB-2_3', 'noteE-1_3', 'noteA3_3/2', 'noteG2_3', 'noteB-2_3', 'noteC#3_3', 'noteB-3_3', 'noteC#4_3', 'noteC3_3', 'noteE-3_3', 'noteG3_3', 'noteB-2_3', 'noteB-3_3', 'noteG#2_3', 'noteC3_3', '</simul>', 'noteF2_3', 'noteB-2_3', 'noteG2_3', 'noteC3_3/2', 'noteC3_3', 'noteC3_3', 'noteE-3_3', 'noteD3_3', 'noteB-2_3', 'noteB-3_3', 'noteC#4_3', 'noteC3_3', 'noteC3_3', 'noteB-2_3', 'noteG#3_3', 'noteC#4_3', '</simul>', 'noteD3_3', 'noteC3_3', 'noteB-2_3', 'noteG#3_3', 'noteC4_3', 'noteE-1_3', 'noteG#2_3', 'noteB2_3', 'noteB-2_3', 'noteG#3_3', 'noteC3_3', 'noteB-3_3', 'noteE-4_3', 'noteE-5_3', 'noteB-2_3', 'noteC#3_3', 'noteC3_4', 'noteF3_3', 'noteF#2_3', 'noteC3_3', 'noteE-3_3', 'noteC3_3', 'noteB-2_3', 'noteC2_3', 'noteG#3_3', 'noteD3_3', 'noteF3_3', 'noteC3_3', 'noteG3_3', 'noteB-3_3', 'noteB-2_3', 'noteC#3_3', 'noteC4_3', 'noteC#4_3', 'noteC3_3', 'noteB-2_3', 'noteB-3_3', 'noteG#3_3', 'noteB3_3', 'noteE-1_3', 'noteE-2_3', 'noteB-2_3', 'noteG#4_3', 'noteE-2_3/2', 'noteB-2_1/2', 'noteG#2_3', 'noteC3_3', 'noteG3_3', 'noteB-3_3', 'noteG3_3', 'noteB-2_3', 'noteC#4_3', 'noteC3_3', 'noteC4_3', 'noteE-4_3', 'noteG4_3', 'noteB-2_3', 'noteB-2_3', 'noteE-3_3', 'noteC#3_3', 'noteE-1_3', 'noteB-1_3', 'noteG#2_3', 'noteB-2_3', 'noteB-3_3', 'noteC#4_3', 'noteC4_3', 'noteC3_3', 'noteB-2_3', 'noteF#2_3', 'noteE-2_3/2', 'noteA2_3/2', 'noteB-2_3', 'noteB-3_3', 'noteC4_3', 'noteG3_3', 'noteC3_3', 'noteG#3_3', 'noteC3_3', 'noteB-2_3', 'noteC#3_3', 'noteB-3_3', 'noteE-3_3', 'noteD3_3', 'noteG#3_3', 'noteE-1_3', 'noteB-2_3', 'noteC#4_3', 'noteC#3_3', 'noteC3_3', 'noteB3_3', 'noteB-3_3', 'noteG3_3', 'noteB-2_3', 'noteF#3_3', 'noteE-1_3', 'noteB-1_3', 'noteF2_3', 'noteC#3_3', 'noteB-2_1/6', 'noteG2_3', 'noteB-2_3', 'noteG#3_3', 'noteF3_3', 'noteC#4_3', 'noteC3_3', 'noteG2_3', 'noteE-4_3', 'noteB-1_3', 'noteB-2_3', 'noteA2_3', 'noteC3_3', 'noteF#3_3', 'noteB-2_1/2', 'noteB-1_3', 'noteB-2_3', 'noteG#3_3', 'noteC3_3', 'noteB-2_3', 'noteB-3_3', 'noteC#4_3', 'noteB-2_3', '</simul>', 'noteF2_3', 'noteB-3_3', 'noteC4_3', 'noteC3_3', 'noteB-2_3', 'noteF3_3', 'noteB-3_3', 'noteG#2_3', '</simul>', 'noteD3_3/2', 'noteC3_3', 'noteC3_3', 'noteG3_1/2', 'noteG3_3', 'noteB-2_3', 'noteB-3_3', 'noteC#4_3', 'noteC3_3', 'noteC4_3', 'noteB-2_1', 'noteB-2_3', 'noteF3_3', 'noteG#3_3', 'noteC4_3', 'noteC#4_3', 'noteC#3_3', 'noteE-1_3', 'noteE-2_3', 'noteF3_3', 'noteG#3_3', 'noteC4_3', 'noteF4_3', 'noteG5_3', 'noteG#2_3', 'noteF2_1/2', 'noteF3_3/2', 'noteE-1_3', 'noteC4_3/2', 'noteB-3_3', 'noteG2_3', 'noteG#3_3', 'noteC#4_3', 'noteF2_3', 'noteC3_3', 'noteB-2_3', 'noteF#3_3', 'noteC2_3', 'noteB-3_3', 'noteC#4_3', 'noteB-2_3', 'noteE-1_3', 'noteE-3_3', 'noteG3_3', 'noteC4_3', 'noteE-4_3', 'noteG3_3/2', 'noteF#1_3', 'noteB-2_3', 'noteF#2_3', 'noteD3_3', 'noteB-3_3', 'noteC3_3', 'noteB-3_3', 'noteC#4_3', 'noteG2_3', 'noteB-2_3', 'noteD3_3', 'noteF#3_3', 'noteF1_1/16', 'noteG1_3', 'noteB1_3', 'noteF#2_3', 'noteB-3_3', '</simul>', 'noteC5_3', 'noteC4_3', 'noteE-4_3', 'noteE-1_3', 'noteB-1_1/8', 'noteE2_3', 'noteB-3_3', 'noteC#4_3', 'noteG#4_3', 'noteC3_3', '</simul>', 'noteB3_3', 'noteG#3_3', 'noteC3_3/2', 'noteG#2_3', 'noteC4_3', 'noteC#4_3', 'noteC3_3', 'noteC4_3/2', 'noteG#1_3/2', 'noteE-3_3', 'noteG3_3', 'noteA2_4', 'noteG#3_3', 'noteB-3_3', 'noteC3_3', 'noteE-2_3/2', 'noteF2_3', 'noteG#2_3', 'noteB-1_3', 'noteB-2_3', 'noteC2_3', 'noteC3_3', 'noteC4_3', 'rest_1', 'noteD4_1/3', 'noteC2_3/2', 'noteF1_1/4', 'noteG4_1/4', '<simul>', 'noteC4_3', 'noteE-4_3', 'noteC#2_3', 'noteA7_1/8', '</simul>', '<simul>', 'noteA3_3/2', 'noteA4_3/2', 'noteB-2_3', 'noteG#2_3', 'noteG#3_3', 'noteE-4_3', 'noteG#4_3', 'noteE-2_3/2', 'noteF1_1/4', 'noteG2_3', 'noteC3_3', 'noteB-2_3', 'noteC4_3/2', 'noteC3_3/2', 'noteC2_3', 'rest_1', 'noteE-1_3', 'noteB-1_3', 'noteB-3_3', 'noteG#2_3', 'noteB-2_3', 'noteC3_3', 'noteG3_3', 'noteC4_3', 'noteE-4_3', 'noteG4_3', 'noteB-2_3', 'noteF3_3', 'noteC4_3', '</simul>', '<simul>', 'noteC5_3/2', 'noteF1_1/4', 'noteF2_1/4', 'noteG6_1/8', 'noteB-1_1/8', 'noteB-2_3', 'noteC3_3/2', '</simul>', '<simul>', 'noteE-5_3/2', 'noteC3_3', 'noteE4_1/3', 'noteB-2_3', 'noteG#3_3', '</simul>', 'noteG1_3/2', 'noteA4_1/2', 'rest_1', 'noteC#3_3', 'noteE-3_3', 'noteC3_3', 'noteF3_3', 'noteB-3_3', 'noteC#4_3', 'noteC3_3', 'noteG3_3', 'noteG#2_3', 'noteB-1_3', 'noteB-2_3', 'noteC#4_3', 'noteC4_3', 'noteC5_3', 'noteB-3_3', 'noteF2_3/2', 'noteG#3_3', 'noteC3_3', 'noteG3_3', 'noteE-3_3', 'noteB-3_3', 'noteF4_3', 'noteC#3_3', 'noteF3_3', 'noteG#3_3', 'noteB-2_3', 'noteG#3_3', '</simul>', 'noteC4_3/2', 'noteC3_3', 'noteG#3_3', 'noteB-1_3', 'noteB-3_3', 'noteE-4_3', 'noteB-5_3', 'noteE-1_3', 'noteE-2_3', 'noteB2_3', 'noteB-2_3', 'noteF3_3', 'noteG#3_3', '</simul>', '<simul>', 'noteE4_3', 'noteC#4_3', 'noteC3_3', 'noteF#3_3', 'noteB-1_1/6', 'noteC#3_3', 'noteG#3_3', '</simul>', '<simul>', 'noteC4_3', 'noteE-1_3', 'noteE-2_3', 'noteG2_3', 'noteC3_3', 'noteG3_3', 'noteA3_3', '</simul>', '<simul>', 'noteF3_3', 'noteG#3_3', '</simul>', 'noteE-1_3', 'noteB-2_3/2', 'noteE-2_3', 'noteB-2_3', '</simul>', '<simul>', 'noteB-3_3', 'noteC#3_3', 'noteF#2_3', 'noteC3_3', 'noteC3_3', 'noteF3_3', 'noteB-3_3', '</simul>', '<simul>', 'noteE4_3', 'noteG#2_3', '</simul>', 'noteC5_1/2', 'noteC5_3', 'noteE-2_3', 'noteB-2_3', 'noteB-3_3', 'noteE-3_3', 'noteG3_3', 'noteB-3_3', 'noteC3_3', 'noteG#3_3', 'noteC#3_3', 'noteB-2_3', '</simul>', '<simul>', 'noteB-3_3', 'noteC3_3', 'noteF#3_3', 'noteC#2_3', 'noteF2_3', 'noteE-1_3', 'noteE-2_3', 'noteB-2_3', 'noteB-3_3', '</simul>', 'noteG4_3', 'noteB-2_3', 'noteG#3_3', '</simul>', '<simul>', 'noteB-3_3', 'noteE-2_3', 'noteC3_3', 'noteG#3_3', 'noteG#4_3', 'noteB-2_3', 'noteB-3_3', 'noteG#2_3', 'noteC3_3', '</simul>', '<simul>', 'noteG#3_3', 'noteC#4_3', 'noteB-2_3', 'noteB-3_3', '</simul>', '<simul>', 'noteB-3_3', 'noteC#4_3', 'noteC3_3', 'noteE-3_3', 'noteB-2_3', 'noteB3_3', '</simul>', '<simul>', 'noteC3_3', 'noteG#3_3', 'noteB-1_3', 'noteB-2_3', '</simul>', '<simul>', 'noteC3_3', 'noteG#3_3', 'noteC4_3', 'noteG#2_3', 'noteF3_3', 'noteB-2_3', '</simul>', '<simul>', 'noteC4_3', 'noteE-4_3', 'noteE-3_3', 'noteB-2_3', 'noteC#3_3', 'noteC3_3', 'noteE-3_3', 'noteG#2_3', 'rest_3', 'noteB-2_3', 'noteB-3_3', 'noteG4_3', '</simul>', '<simul>', 'noteE4_3', 'noteC3_3', 'noteB-3_3', 'noteC#2_3', 'noteB-2_3', 'noteF3_3', 'noteG#2_3', 'noteG3_3', 'noteC4_3', 'noteC3_3', 'noteB-2_3', 'noteB-2_3', 'noteF2_3', 'noteB-3_3', 'noteC4_3', 'noteG#2_3', 'noteG#3_3/2', 'noteG#2_3', 'noteG#3_3', 'noteB-3_3', 'noteC3_3', 'noteC3_3', '</simul>', '<simul>', 'noteB-2_3', 'noteG#3_3', 'noteC4_3', 'noteE-2_3', 'noteC3_3', 'noteF#3_3', 'noteG#2_3', '</simul>', 'noteE-5_3', 'noteB-2_3', 'noteA2_3', 'noteF3_3', 'noteC4_3', 'noteG#4_3', 'noteG#3_3', 'noteC3_3', 'noteE-3_3', 'noteC#3_3', 'noteG#2_3', 'noteF3_3', 'noteC#4_3', '</simul>', '<simul>', 'noteG#3_3', 'noteG#2_3', 'noteE-2_3', 'noteF3_3', 'noteB-3_3', 'noteC3_3', 'noteB-2_3', 'noteG#2_3', 'noteG#3_3', '</simul>', '<simul>', 'noteE4_3', 'noteB-2_3', 'noteG#2_3', 'noteG#3_3', 'noteC4_3/2', 'noteE-2_3', 'noteC3_3', 'noteG3_3', '</simul>', '<simul>', 'noteF#3_3', 'noteC#3_3', 'noteB-3_3', 'noteC3_3', 'noteC#4_3', 'noteE-3_3', 'noteE-2_3', 'noteB-2_3', 'noteG#3_3', 'noteC3_3', 'noteC3_3', 'noteG#3_3', '</simul>', '<simul>', 'noteE-4_3', 'noteB-2_3', 'noteG#2_3', 'noteC3_3', '</simul>', 'noteA3_1/2', '<simul>', 'noteB-3_3', 'noteB-2_3']


try:
    play_tokens(notes, 0)
except:
    pygame.midi.quit()

