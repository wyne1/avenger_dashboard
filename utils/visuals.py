import base64
import matplotlib.pyplot as plt
import librosa
import io
import numpy as np
from pydub import AudioSegment

def get_spectrogram():

	## Creating SPECTROGRAM from example audio
	y, sr = librosa.load(librosa.util.example_audio_file())
	plt.figure(figsize=(7, 3))
	plt.title('Linear-frequency Power Spectrogram')
	plt.specgram(np.array(y), Fs=sr)
	plt.axis('off')

	## Converting MatplotLib Plot to Base64 for display
	## Source: https://stackoverflow.com/questions/49851280/showing-a-simple-matplotlib-plot-in-plotly-dash 
	buf = io.BytesIO() # in-memory files
	plt.savefig(buf, format="png", bbox_inches='tight') # save to the above file object
	data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
	plt.close()
	return data

def generate_plot(step=1):
	# podcast = AudioSegment.from_mp3(PATH)
	# PODCAST_LENGTH = podcast.duration_seconds
	# PODCAST_INTERVAL = 500

    print(PODCAST_INTERVAL * step, PODCAST_INTERVAL * (step + 1))
    # 5 second interval of podcast
    seg = podcast[PODCAST_INTERVAL * step: PODCAST_INTERVAL * (step + 1)]
    samples = seg.get_array_of_samples()
    arr = np.array(samples)
    df = pd.DataFrame(arr)
    df['idx'] = df.index.values
    df.columns = ['y', 'idx']
    fig = px.line(df, x='idx', y='y', render_mode="webgl")
    fig.update_layout(
        height=250,
        margin_r=0,
        margin_l=0,
        margin_t=0,
        yaxis_title="",
        yaxis_fixedrange=True,
    )

    layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    # mapbox=dict(
    #     accesstoken=mapbox_access_token,
    #     style="light",
    #     center=dict(lon=-78.05, lat=42.54),
    #     zoom=7,
    # ),
	)
    return fig, layout

def seconds_to_MMSS(slider_seconds):
    decimal, minutes = math.modf(slider_seconds / 60.0)
    seconds = str(round(decimal * 60.0))
    if len(seconds) == 1:
        seconds = "0" + seconds
    MMSS = "{0}:{1}".format(round(minutes), seconds)
    return MMSS

