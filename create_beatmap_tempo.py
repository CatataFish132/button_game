# import modules
import madmom
import librosa
import IPython.display as ipd

# read audio file
x, sr = librosa.load('sounds/Catchit.wav')
ipd.Audio(x, rate=sr)

# # approach 1 - onset detection and dynamic programming
# tempo, beat_times = librosa.beat.beat_track(x, sr=sr, start_bpm=60, units='time')
#
# clicks = librosa.clicks(beat_times, sr=sr, length=len(x))
# ipd.Audio(x + clicks, rate=sr)
# print(clicks)
# print(sr)

# approach 2 - dbn tracker
proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
act = madmom.features.beats.RNNBeatProcessor()('sounds/Catchit.wav')

beat_times = proc(act)
print(beat_times)
with open("sounds/Catchit.beatmap.txt", "w") as f:
    f.write('\n'.join(['%.4f' % onset_time for onset_time in beat_times]))
# clicks = librosa.clicks(beat_times, sr=sr, length=len(x))
# ipd.Audio(x + clicks, rate=sr)


