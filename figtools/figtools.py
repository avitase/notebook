import base64
import enum
import io
import pathlib
from pathlib import Path
from typing import Any, Tuple

import ipywidgets  # type: ignore
import matplotlib as mpl  # type: ignore
from IPython import display  # type: ignore

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
        
    fig.tight_layout()

    png_fqn = None
    for ftype in ['png', 'pgf']:
        filename = str(pathlib.Path(cfg['img_dir']) / f'{filename_base}.{ftype}')
        fig.savefig(filename, **kwargs)

        if ftype == 'png':
            png_fqn = filename

    img_bytes = io.BytesIO()
    fig.savefig(img_bytes, format='png', **kwargs)
    img_bytes.seek(0)
    encoded = base64.b64encode(img_bytes.read()).decode('ascii')

    png = f'{filename_base}.png'
    link = display.HTML(
        f'<a download="{png}" href="data:image/png;base64,{encoded}">[Download {png}]</a>')

    w, h = fig.get_size_inches() * 100
    w, h = int(w), int(h)
    img = display.Image(png_fqn, width=w, height=h)

    out = ipywidgets.Output()
    out.append_display_data(img)
    out.append_display_data(link)
    return out
