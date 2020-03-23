import matplotlib.pyplot as plt
import librosa.display
import sklearn
import numpy as np
import matplotlib.gridspec as gridspec
import io
import base64
from datetime import datetime, timezone

# frame
# n_window = int(sample_rate * 4. / frames * 2) - 4 * 2
# # 50% overlap
# n_overlap = int(n_window / 2.)
# # Mel filter bank
# melW = librosa.filters.mel(sr=16000, n_fft=n_window, n_mels=bands, fmin=0., fmax=8000.)
# # Hamming window
# ham_win = np.hamming(n_window)


def visualize_voice_graph(dc_timer, duration, title="DUMMY", draw_verticles=True):
    fig = plt.figure(figsize=(7,3))

    for i in range(1,len(dc_timer)):
        y = i%2
        xflat = [dc_timer[i-1], dc_timer[i]]
        xdown = [dc_timer[i], dc_timer[i]]
        yflat = [y, y]
        ydown = [y, int(not y)]

        if i == len(dc_timer) - 1:
            xlast = [dc_timer[i], duration]
            ylast = [0, 0]
            plt.plot(xlast, ylast, 'g')

    #     print([dc_timer[i-1], dc_timer[i]],[y, y])
        col = 'r' if y == 1 else 'g'
        plt.plot(xflat, yflat, col)
        if draw_verticles:
            plt.plot(xdown, ydown, 'y--')
        if y == 1:
            prev_y = xflat[1]
#             if
            plt.text(xflat[0], 1.1, "{:.1f}".format(xflat[0]), horizontalalignment='left', fontsize=13,
                    style='italic')
            plt.text(xflat[1], 1.1, "{:.1f}".format(xflat[1]), horizontalalignment='right', fontsize=13,
                    bbox={'facecolor': 'red', 'alpha': 0.2, 'pad': 1})


    plt.xlabel('Time (sec)')
#     plt.ylabel('Human Speech', fontsize=15)
    plt.axis([-0.3, duration+0.3, -0.2, 1.2])
    plt.yticks([0,1],['Noise', "Human"])
    plt.xticks(range(duration+1))
    plt.rc('ytick',labelsize=14)
    plt.title(title, fontsize=16)
#     plt.suptitle('Human Speech Activity on Sample')

    buf = io.BytesIO() # in-memory files
    plt.savefig(buf, format="png", bbox_inches='tight') # save to the above file object
    src_data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
    plt.close()

    src_data = "data:image/png;base64,{}".format(src_data)
    return src_data

def vis_spectrogram(audio, sr):
    plt.figure(figsize=(14, 5))
    librosa.display.waveplot(audio, sr=sr)

    X = librosa.stft(audio)
    Xdb = librosa.amplitude_to_db(abs(X))
    plt.figure(figsize=(14, 5))

    print(">> Spectrogram")
    librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='hz')
    #If to pring log of frequencies
    librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar()

    print(">> Mel-Spectrogram")
    S = librosa.feature.melspectrogram(y=audio, sr=sr)
    librosa.display.specshow(librosa.power_to_db(S, ref=np.max))

    #Displaying  the MFCCs:
    mfccs = librosa.feature.mfcc(audio, sr=sr)
    print(mfccs.shape)
    librosa.display.specshow(mfccs, sr=sr, x_axis='time')

def vis_spectrogram1(audio, sr):
    duration = int(np.ceil(len(audio)/sr))

    col, row = 16,7
    # Plot figure with subplots of different sizes
    fig = plt.figure(1, figsize=(col,row))
    plt.title('WaveFrom & Spectrogram')

    # set up subplot grid
    gridspec.GridSpec(row, col)

    ## SMALLER WaveForm
    plt.subplot2grid((8,14), (0,0), colspan=col, rowspan=2)
    plt.plot(audio)
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.title('WaveFrom', fontsize=22)
#     print(np.min(audio)-(np.min(audio)*0.01), np.max(audio)+(np.max(audio)*0.01))
#     plt.axis([-0.3, duration+0.3, np.min(audio), np.max(audio)])
    plt.autoscale(enable=True, axis='x', tight=True)
#     plt.xticks(range(duration+1))


    # large SPECTROGRAM
    plt.subplot2grid((row, col), (3,0), colspan=col, rowspan=4)
    plt.specgram(audio, Fs=sr)
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    plt.title('Spectrogram', fontsize=28)



def vis_spectral_centroids(audio, sr):

    #spectral centroid -- centre of mass -- weighted mean of the frequencies present in the sound
    spectral_centroids = librosa.feature.spectral_centroid(audio, sr=sr)[0]
    spectral_centroids.shape

    # Computing the time variable for visualization
    frames = range(len(spectral_centroids))
    t = librosa.frames_to_time(frames)

    # Normalising the spectral centroid for visualisation
    def normalize(x, axis=0):
        return sklearn.preprocessing.minmax_scale(audio, axis=axis)

    #Plotting the Spectral Centroid along the waveform
    librosa.display.waveplot(audio, sr=sr, alpha=0.4)
    plt.plot(t, normalize(spectral_centroids), color='r')

def get_labels(path):
    with open(path+'/labels.txt') as txt:
        content = txt.read()
    labels = content.split(',')
    return labels
