#!/usr/bin/env python

from math import sqrt
from csv import DictReader
from pandas import DataFrame, read_csv, Series
from os.path import join as pj
import numpy as np
from itertools import product
import matplotlib
matplotlib.use('agg')

from matplotlib import pyplot as plt


plt.close('all')

frequencies = [10, 25, 50, 75]

d = DataFrame(columns=('frequency', 'kind', 'estimator', "error", "y_err"))

for frequency in frequencies:

    with open(pj("./new_arbre/arbre_high_calibration_%d" % frequency, "estimation", "global_difference.csv")) as f:
        reader = DictReader(f)

        for row in reader:
            d.loc[len(d) + 1] = [frequency, row["kind"], row["estimator"], row["mean"], row["std"]]

print(d)

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.set_xlabel('Time between recalibration (s)')
ax1.set_ylabel(r'$\epsilon(t)$')
ax1.set_xticks(frequencies)
ax1.set_xlim([9, 80])

for kind, estimator in product(["tx", "rx"], ["route"]):
    errors = list(d[(d.kind == kind) & (d.estimator == estimator)].error)
    errors = [float(error) for error in errors]
    stds = list(d[(d.kind == kind) & (d.estimator == estimator)].y_err)
    stds = [float(std) for std in stds]
    # f = d[(d.kind == kind) & (d.estimator == estimator)].frequency
    # error = d[(d.kind == kind) & (d.estimator == estimator)].error
    # plt.plot(list(f), list(error), label="%s %s" % (kind, estimator))

    ax1.errorbar(frequencies, errors, fmt="o-", yerr=stds, label="%s %s" % (kind, estimator))

    ax1.legend(loc='best')
    format_axes(ax1)
    plt.tight_layout()
    fig.savefig("frequencies_difference.pdf", format="pdf")
