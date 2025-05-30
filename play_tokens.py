import pygame.midi
from music21 import pitch
import time
import re
from fractions import Fraction


def pitchstr_to_num(note_name):
    return pitch.Pitch(note_name).midi


BPM = 480
second_per_quarter_note = 60 / BPM


def pitch_to_midi(pitch):
    match = re.match(r"([A-Ga-g])([-#b]?)(\d)", pitch)
    if not match:
        return None
    name, accidental, octave = match.groups()
    octave = max(int(octave), 1)
    name = name.upper()

    if accidental == '-' or accidental == 'b':
        name += 'b'
    elif accidental == '#':
        name += '#'

    base = pitchstr_to_num(name) - 60 #See the NOTE_TO_MIDI dictionary. -60 because it automatically assumes middle c octave. We add octaves later 

    if base is None:
        return None
    midi_number = base + (octave + 1) * 12
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

def parse_tokens(tokens):
    i = 0
    notes = []
    while i < len(tokens):
        if tokens[i][:4] == "note" or tokens[i] == "rest":
            try:
                dur = eval(tokens[i+1]) #check if it's evalable, but still use the fraction
                dur = tokens[i+1]
            except:
                dur = 1
            notes.append(f"{tokens[i]}_{dur}")
            i += 2
        elif tokens[i] in ["<simul>", "</simul>", "<end_song>"]:
            notes += tokens[i]
            i += 1
        else:
            i += 1
    return notes
        
def play_tokens(tokens, instrument, parse=False):
    pygame.midi.init()
    player = pygame.midi.Output(0)
    player.set_instrument(instrument)
    if parse:
        tokens = parse_tokens(tokens)
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


tokens = ['noteC#4', '1/3', 'noteE-6', '1/8', 'noteE-8', '2', 'noteC#4', '1/3', 'noteB-1', '1/8', '<simul>', 'noteC#4', '2', 'noteC#4', '1/3', 'noteD8', '1/3', 'noteC#4', '1/4', 'noteC#4', '1/3', '</simul>', 'noteC#4', '2', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteB-0', '1/8', 'noteE-8', '2', 'noteC#4', '1/3', 'noteB-0', '1/8', 'noteE-8', '1/8', 'noteE4', '1/8', 'noteE-8', '1/8', 'noteB4', '2', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '2', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '2', 'noteC#4', '1/3', 'noteC#4', '2', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '2', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/4', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3', 'noteC#4', '1/3']
try:
    play_tokens(tokens, instrument=0, parse=True) #0: Piano, 101: Synth
except:
    pygame.midi.quit()

