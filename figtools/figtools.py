import enum
import hashlib
import pathlib

import ipywidgets
import numpy as np
from IPython import display
from PIL import Image

IMG_DIR = 'img'


class Size(enum.Enum):
    SMALL = 1
    LARGE = 2

    def get_size(self):
        if self == Size.SMALL:
            return 4., 3.
        if self == Size.LARGE:
            return 8., 6.

        raise Exception('Unknown size')


def hash_img(filename):
    img = Image.open(filename).convert('RGBA')
    pixels = np.array(img).ravel()

    hsh = hashlib.sha256()
    hsh.update(pixels.tobytes())
    return hsh.hexdigest()


def save_fig(fig, filename_base, resize=Size.SMALL, **kwargs):
    if 'dpi' not in kwargs:
        kwargs['dpi'] = 400

    if resize:
        fig.set_size_inches(resize.get_size())

    return_img = None
    for ftype in ['png', 'pgf']:
        filename = str(pathlib.Path(IMG_DIR) / f'{filename_base}.{ftype}')
        fig.savefig(filename, **kwargs)

        if ftype == 'png':
            return_img = filename

    url = return_img
    absurl = 'file://' + str(pathlib.Path().absolute() / url)
    hsh = hash_img(return_img)
    link = display.HTML(f'<a href="{absurl}?{hsh}">{absurl}</a>')

    w, h = fig.get_size_inches() * 100
    w, h = int(w), int(h)
    img = display.Image(return_img, width=w, height=h)

    out = ipywidgets.Output()
    out.append_display_data(link)
    out.append_display_data(img)
    return out
