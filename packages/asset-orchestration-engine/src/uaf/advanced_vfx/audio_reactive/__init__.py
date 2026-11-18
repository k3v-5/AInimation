"""
UAF-81.89: Audio reactive exports.
"""

from .spectral_coupler import ADSREnvelope, AudioSpectralCoupler, BAND_FREQUENCIES

__all__ = [
    "ADSREnvelope",
    "AudioSpectralCoupler",
    "BAND_FREQUENCIES",
]
