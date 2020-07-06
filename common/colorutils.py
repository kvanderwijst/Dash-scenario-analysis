import colorsys
import numpy as np

def hex_to_rgb(hex, normalise=False):
    h = hex.lstrip('#')
    rgb = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    if normalise:
        return [x/255. for x in rgb]
    else:
        return rgb

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(rgb)

def hex_to_hls(hex):
    return colorsys.rgb_to_hls(*hex_to_rgb(hex, True))

def hls_to_hex(hls):
    return rgb_to_hex([int(np.round(x*255)) for x in colorsys.hls_to_rgb(*hls)])

def lighten_hex(hex, extra_lightness=0.1, extra_saturation=0.0):
    hls = list(hex_to_hls(hex))
    hls[1] += extra_lightness
    hls[2] += extra_saturation
    return hls_to_hex(hls)