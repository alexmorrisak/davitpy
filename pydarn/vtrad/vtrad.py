import copy 
import datetime

from matplotlib import pyplot as mp
import numpy as np
import scipy as sp

import pydarn

# Create a system for handling metadata that applies to all signals. ###########
glob = {}
def globalMetaData():
  """Return the glob (global metadata) dictionary.
  """
  return glob

def globalMetaData_add(**metadata):
  """Add an item to the glob (global metadata) dictionary.
  :**metadata : keywords and values to be added to the glob dictionary.
  """
  global glob
  glob = dict(glob.items() + metadata.items())

def globalMetaData_del(keys):
  """Delete an item from the glob (global metadata) dictionary.
  :param keys: List of keys to be deleted.
  """
  global glob
  for key in keys:
    if glob.has_key(key): del glob[key]

def globalMetaData_clear():
  """Clear the glob (global metadata) dictionary.
  """
  global glob
  glob.clear()

# Signal Objects Start Here ####################################################
class vtrad(object):
  def __init__(self, dateStr, rad, time=[0, 2400], fileType='fitex', vb=0, beam=-1, filter=0, comment='Object Created', **metadata):
    """Define a vtsd sig object.

    :param dtv: datetime.datetime list
    :param data: raw data
    :param ylabel: Y-Label String for data
    :returns: sig object
    """
    defaults = {}
    defaults['ylabel'] = 'Untitled Y-Axis'
    defaults['xlabel'] = 'Time [UT]'
    defaults['title']  = 'Untitled Plot'
    defaults['fft_xlabel'] = 'Frequency [Hz]'
    defaults['fft_ylabel'] = 'FFT Spectrum Magnitude'

    self.metadata = dict(defaults.items() + metadata.items())
    self.raw = vtradStruct(dateStr, rad, time=time, fileType=fileType, vb=vb, beam=beam, filter=filter, comment=comment, parent=self)
    self.active = self.raw

class vtradStruct(object):
  def __init__(self, dateStr, rad, time=[0, 2400], fileType='fitex', vb=0, beam=-1, filter=0, comment=None, parent=0, **metadata):
    self.parent = parent
    """Define a vtsd sigStruct object.

    :param dtv: datetime.datetime list
    :param data: raw data
    :param id: A serial number uniquely identifying this signal in the
    : processing chain.
    :param **metadata: keywords sent to matplot lib, etc.
    :returns: sig object
    """

    self.data = pydarn.radDataRead(dateStr, rad, time=time, fileType=fileType,vb=vb, beam=beam, filter=filter)

    self.metadata = {}
    for key in metadata: self.metadata[key] = metadata[key]

    self.history = {datetime.datetime.now():comment}

  def setActive(self):
    """Sets this signal as the currently active signal.
    """
    self.parent.active = self

  def nyquistFrequency(self,dtv=None):
    """Calculate the Nyquist frequency of a vt sigStruct signal.
    :param dtv: List of datetime.datetime to use instead of self.dtv.
    :returns: nyq: Nyquist frequency of the signal in Hz.
    """
    dt  = self.samplePeriod(dtv=dtv)
    nyq = 1. / (2*dt)
    return nyq

  def samplePeriod(self,dtv=None):
    """Calculate the sample period of a vt sigStruct signal.
    :param dtv: List of datetime.datetime to use instead of self.dtv.
    :returns: samplePeriod: sample period of signal in seconds.
    """
    
    if dtv == None: dtv = self.dtv

    diffs = np.unique(np.diff(dtv))
    self.diffs = diffs

    if len(diffs) == 1:
      samplePeriod = diffs[0].total_seconds()
    else:
      maxDt = np.max(diffs) - np.min(diffs)
      maxDt = maxDt.total_seconds()
      avg = np.sum(diffs)/len(diffs)
      avg = avg.total_seconds()
      md  = self.getAllMetaData()
      warn = 'WARNING'
      if md.has_key('title'): warn = ' '.join([warn,'FOR','"'+md['title']+'"'])
      print warn + ':'
      print '   Date time vector is not regularly sampled!'
      print '   Maximum difference in sampling rates is ' + str(maxDt) + ' sec.'
      print '   Using average sampling period of ' + str(avg) + ' sec.'
      samplePeriod = avg

    return samplePeriod

  def updateValidTimes(self,times):
    """Update the metadata block times that a signal is valid for.
    :param: times: List of times between which the signal is valid.
    """
    if self.metadata.has_key('validTimes'):
      if self.metadata['validTimes'][0] < times[0]: self.metadata['validTimes'][0] = times[0]
      if self.metadata['validTimes'][1] > times[1]: self.metadata['validTimes'][1] = times[1]
    else:
      self.metadata['validTimes'] = times

  def getAllMetaData(self):
    return dict(globalMetaData().items() + self.parent.metadata.items() + self.metadata.items())

  def setMetaData(self,**metadata):
    self.metadata = dict(self.metadata.items() + metadata.items())

  def plotFan(self):
    pass
