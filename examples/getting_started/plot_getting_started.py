"""
Getting started with SpikeInterface
===================================

In this introductory example, you will see how to use the `spikeinterface` to perform a full elextrophysiology analysis.
We will first create some simulated data, and we will then perform some preprocessing, run a couple of spike sorting
algorithms, inspect and validate the results, export to Phy, and compare spike sorters.

"""


##############################################################################
# Let's first import the `spikeinterface` package.
# We can either import the whole package:

import spikeinterface as si

##############################################################################
# or import the different submodules separately (preferred). There are 5 modules
# which correspond to 5 separate packages:
#
# - `extractors` : file IO and probe handling
# - `toolkit` : processing toolkit for pre-, post-processing, validation, and automatic curation
# - `sorters` : Python wrappers of main spike sorters
# - `comparison` : comparison of spike sorting output
# - `widgets` : visualization


import spikeinterface.extractors as se
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import spikeinterface.comparison as sc
import spikeinterface.widgets as sw

##############################################################################
# First, let's create a toy example with the `extractors` module:

recording, sorting_true = se.example_datasets.toy_example(duration=60, num_channels=4, seed=0)

##############################################################################
# `recording` is a `RecordingExtractor` object, which extracts information #  about channel ids, channel locations
# (if present), the sampling frequency of the recording, and the extracellular  traces. `sorting_true` is a
# `SortingExtractor` object, which contains information about spike-sorting related information,  including unit ids,
# spike trains, etc. Since the data are simulated, `sorting_true` has ground-truth information of the spiking
# activity of each unit.
#
#  Let's use the widgets to visualize the traces and the raster plots.

w_ts = sw.plot_timeseries(recording)
w_rs = sw.plot_rasters(sorting_true)

##############################################################################
# This is how you retrieve info from a `RecordingExtractor`...

channel_ids = recording.get_channel_ids()
fs = recording.get_sampling_frequency()
num_chan = recording.get_num_channels()

print('Channel ids:', channel_ids)
print('Sampling frequency:', fs)
print('Number of channels:', num_chan)

##############################################################################
# ...and a `SortingExtractor`
unit_ids = sorting_true.get_unit_ids()
spike_train = sorting_true.get_unit_spike_train(unit_id=unit_ids[0])

print('Unit ids:', unit_ids)
print('Spike train of first unit:', spike_train)

##################################################################
# add a probe file?


##############################################################################
# Using the `toolkit`, you can perform pre-processing on the recordings. Each preprocessing function also returns
# a `RecordingExtractor`, which makes it easy to build pipelines. Here, we filter the recording and apply common
# median reference (CMR)

recording_f = st.preprocessing.bandpass_filter(recording, freq_min=300, freq_max=6000)
recording_cmr = st.preprocessing.common_reference(recording_f, reference='median')

##############################################################################
# Now you are ready to spikesort using the `sorters` module!
# Let's first check which sorters are implemented and which are installed

print('Available sorters', ss.available_sorters())
print('Installed sorters', ss.installed_sorter_list)

##############################################################################
# The `ss.installed_sorter_list` will list the sorters installed in the machine. Each spike sorter
# is implemented as a class. We can see we have Klusta and Mountainsort4 installed.
# Spike sorters come with a set of parameters that users can change. The available parameters are dictionaries and
# can be accessed with:

print(ss.get_default_params('mountainsort4'))
print(ss.get_default_params('klusta'))

##############################################################################
# Let's run mountainsort4 and change one of the parameter, the detection_threshold:

sorting_MS4 = ss.run_mountainsort4(recording=recording_cmr, detect_threshold=6)

##############################################################################
# Alternatively we can pass full dictionary containing the parameters.

ms4_params = ss.get_default_params('mountainsort4')
ms4_params['detect_threshold'] = 4
ms4_params['curation'] = False

# parameters set by params dictionary
sorting_MS4_2 = ss.run_mountainsort4(recording=recording, **ms4_params)

##############################################################################
# Let's run Klusta as well, with default parameters:

sorting_KL = ss.run_klusta(recording=recording_cmr)


##############################################################################
# The `sorting_MS4` and `sorting_MS4` are `SortingExtractor` objects. We can print the units found using:

print('Units found by Mountainsort4:', sorting_MS4.get_unit_ids())
print('Units found by Klusta:', sorting_KL.get_unit_ids())


##############################################################################
# Once we have paired `RecordingExtractor` and `SortingExtractor` objects we can postprocess, validate, and curate the
# results. With the `toolkit.postprocessing` submodule, one can, for example, get waveforms, templates, maximum
# channels, PCA scores, or export the data to Phy. [Phy]() is a GUI for manual curation of the spike sorting output.
# To export to phy you can run:

st.postprocessing.export_to_phy(recording, sorting_KL, output_folder='phy')

##############################################################################
# Then you can run the template-gui with: `phy template-gui phy/params.py` and manually curate the results.
#
# Validation of spike sorting output is very important. The `toolkit.validation` module implements several quality
# metrics to assess the goodness of sorted units. Among those

