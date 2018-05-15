#!/usr/bin/env python

"""
RS 2018/02/23:  Digesting Obsidian Output

Plots we want to see:
    Trace plots of key parameters like layer depths, rock properties
    Histograms of residuals between forward model values and data
    Contour maps of residuals between forward models and data
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import GPy

runtag = 'gascoyne_v3'


def plot_sensor(sensors, readings, chain, sample=None, units='unknown units'):
    """
    Plots the value of a sensor against the forward model:
        Contour plots of real data and forward models
        Contour plots of mean model residuals across the chain
        Histograms of model residuals across the chain
    :param sensors:  np.array of shape (N, 3) with the physical
        coordinates (x,y,z) of the sensors in meters; assumed to have a
        regular raster-like structure where N factors into (Nx, Ny)
    :param readings:  np.array of shape (N, ) with the observed
        sensor readings for the real dataset
    :param chain:  np.array of shape (M, N) with the synthetic
        sensor readings for each forward model
    :param sample:  int index of sample to grab from chain
        (defaults to None, which averages over the chain)
    :param units:  str describing the units of sensor readings
    """
    x, y, z = sensors.T
    d = readings - readings.mean()
    if sample is None:
        print "Averaged fwd models over chain of shape", chain.shape
        f = chain.mean(axis=0) - chain.mean()
    elif not isinstance(sample, int):
        print "ERROR:  sample = {} is of type {}, not int".format(
            sample, sample.__class__)
        return
    elif abs(sample) > len(chain):
        print "ERROR:  sample = {} not in range ({}, {})".format(
                sample, -len(chain), len(chain))
        return
    else:
        print "Picking sample", sample, "from chain of shape", chain.shape
        f = chain[sample] - chain[sample].mean()

    # Contour map of residuals in f
    plt.subplot(2, 1, 1)
    # plt.contourf(xgrid, ygrid, dgrid, alpha=0.5)
    plt.tricontourf(x, y, d, alpha=0.5)
    plt.colorbar()
    # plt.contour(xgrid, ygrid, fgrid, colors='k')
    plt.tricontour(x, y, f, colors='k')
    plt.xlabel("Eastings (m)")
    plt.ylabel("Northings (m)")

    # Histogram of residuals in f
    plt.subplot(2, 1, 2)
    plt.hist(d-f, bins=20)
    plt.xlabel("Data $-$ Model ({})".format(units))
    # Show
    plt.show()

def display_ground_truth(labels, spherical=True):
    """
    Displays geological ground-truth labels in a given area.  Put here
    until I find a better home for it.
    :param x:  x-coordinate of centre of extracted area
    :param y:  y-coordinate of centre of extracted area
    :param L:  length of side of (square) modeled area in metres
    :param labels:  pd.DataFrame with columns ['lat', 'lng', 'val']
    :param spherical:  bool, True if (x, y) = (lat, lng) in degrees
    """
    # Plot the ground truth
    x, y, v = labels.x, labels.y, labels.val
    for f in np.unique(v.values):
        idx = (v == f)
        plt.plot(x[idx], y[idx], ls='None', marker='o', ms=3, label=f)
    plt.legend(loc='upper left')
    # plt.title("${:.1f} \\times {:.1f}$ km$^2$ area centered on "
    #           "lng = ${:.3f}$, lat = ${:.3f}$"
    #           .format(L/1e+3, L/1e+3, lng, lat))
    plt.xlabel('Eastings (m)')
    plt.ylabel('Northings (m)')
    # plt.show()

def fieldobs_lookup(readings):

    from gascoyne_config import config_layers
    readstr = [ ]
    for i, v in enumerate(readings):
        if v in config_layers.index:
            readstr.append(config_layers.loc[v,'name'])
        else:
            readstr.append('Unknown layer')
    return readstr

def main_contours():
    """
    The main routine to run a suite of diagnostic plots
    """

    # Load everything
    magSensors = np.loadtxt("magSensors.csv", delimiter=',')
    magReadings = np.loadtxt("magReadings.csv", delimiter=',')
    gravSensors = np.loadtxt("gravSensors.csv", delimiter=',')
    gravReadings = np.loadtxt("gravReadings.csv", delimiter=',')
    samples = np.load(runtag + ".npz")

    # Make a few plots of sensors
    plot_sensor(magSensors, magReadings, samples['magReadings'], units='nT')
    plot_sensor(gravSensors, gravReadings, samples['gravReadings'], units='mgal')

def main_fieldobs():
    """
    The main routine to show simulated field observations
    """

    # First show the data we expect
    fieldSensors = pd.read_csv('fieldobsSensors.csv', names=['x','y'], comment='#')
    fieldReadings = pd.read_csv('fieldobsReadings.csv', names=['val'], comment='#')
    fieldLabels = fieldSensors.assign(val=fieldobs_lookup(fieldReadings.val))
    display_ground_truth(fieldLabels)

    # Now show samples
    samples = np.load(runtag + ".npz")
    for i in np.arange(0, 2500, 25):
        fig = plt.figure(figsize=(6,6))
        readings = samples['fieldReadings'][i]
        fieldLabels.val = fieldobs_lookup(readings)
        display_ground_truth(fieldLabels)
        plt.savefig('boundary_movie_frame{:04d}.png'.format(i))
        plt.close()

def main_boundarymovie():
    """
    Makes a movie of how the boundaries change as the chain samples
    """
    # Load everything
    magSensors = np.loadtxt("magSensors.csv", delimiter=',')
    magReadings = np.loadtxt("magReadings.csv", delimiter=',')
    gravSensors = np.loadtxt("gravSensors.csv", delimiter=',')
    gravReadings = np.loadtxt("gravReadings.csv", delimiter=',')
    samples = np.load(runtag + ".npz")

    # Try fitting a few GP layers
    layer_labels = ['layer{}ctrlPoints'.format(i) for i in range(4)]
    for i in np.arange(0, 2500, 25):
        layer_pars = np.array([samples[ll][i] for ll in layer_labels]).reshape(4,5,5)
        fig = plt.figure()
        gp_predict(gravSensors, layer_pars, ((0.0, 2e+4), (0.0, 2e+4)))
        plt.savefig('boundary_movie_frame{:04d}.png'.format(i))
        plt.close()


if __name__ == "__main__":
    main_contours()
