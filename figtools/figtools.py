import enum
from typing import Any, Tuple
import hashlib
import pathlib
from pathlib import Path

import ipywidgets  # type: ignore
import matplotlib as mpl  # type: ignore
import numpy as np  # type: ignore
from IPython import display  # type: ignore
from PIL import Image  # type: ignore

from . import config as cfg


class Size(enum.Enum):
    SMALL = 1
    LARGE = 2

    def get_size(self) -> Tuple[int, int]:
        if self == Size.SMALL:
            return cfg['size_small']
        if self == Size.LARGE:
            return cfg['size_large']

        raise Exception('Unknown size')


def hash_img(filename: str) -> str:
    img = Image.open(filename).convert('RGBA')
    pixels = np.array(img).ravel()

    hsh = hashlib.sha256()
    hsh.update(pixels.tobytes())
    return hsh.hexdigest()


def init() -> None:
    mpl.use('pgf')
    mpl.rcParams.update({
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.texsystem': 'lualatex',
        'pgf.rcfonts': False,
    })

    Path(cfg['img_dir']).mkdir(exist_ok=True)


def save_fig(fig: Any, filename_base: str, resize: Size = Size.SMALL, **kwargs: Any) -> Any:
    if 'dpi' not in kwargs:
        kwargs['dpi'] = cfg['dpi']

    if resize:
        fig.set_size_inches(resize.get_size())

    return_img = ''
    for ftype in ['png', 'pgf']:
        filename = str(pathlib.Path(cfg['img_dir']) / f'{filename_base}.{ftype}')
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
