from enum import Enum

from msox3000.msox3000 import MSOX3000


class ScopeMetadata:
    class AcquistiionModes(Enum):
        Segmented = 1
        Realtime = 2

    class AnalogChannel:
        def __init__(self, channel, units, probefactor, bw, offset, impedance, skew, coupling, inverted, label, vrange,
                     scale):
            self.channel = channel
            self.unit = units
            self.attenuation = probefactor
            self.bw = bw
            self.offset = offset
            self.impedance = impedance
            self.skew = skew
            self.coupling = coupling
            self.inverted = inverted
            self.label = label
            self.vrange = vrange
            self.scale = scale

    def __init__(self):
        self.idn = str
        self.acq_mode = self.AcquistiionModes
        self.channels = []

    def get_metadata(self, scope: MSOX3000):
        self.idn = scope.idnstr
        self.acq_mode = scope.get_acquisition_mode()
        for channel in scope.chanAnaValidList:
            if scope.get_channel_displayed(channel):
                chan_unit = scope.get_channel_units(channel)
                self.channels.append(self.AnalogChannel(channel, scope.get_channel_units(channel),
                                                        scope.get_channel_probe_factor(channel),
                                                        scope.get_channel_bw(channel),
                                                        scope.get_channel_offset(channel, chan_unit),
                                                        scope.get_channel_impedance(channel),
                                                        scope.get_channel_skew(channel),
                                                        scope.get_channel_coupling(channel),
                                                        scope.get_channel_inverted(channel),
                                                        scope.get_channel_label(channel),
                                                        scope.get_channel_range(channel, chan_unit),
                                                        scope.get_channel_scale(channel, chan_unit)))
