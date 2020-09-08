import base64
import enum
import io
import pathlib
from pathlib import Path

import ipywidgets
import matplotlib as mpl
from IPython import display

from . import config as cfg


class Size(enum.Enum):
    SMALL = 1
    LARGE = 2

    def get_size(self):
        if self == Size.SMALL:
            return cfg['size_small']
        if self == Size.LARGE:
            return cfg['size_large']

        raise Exception('Unknown size')


class FigContext():
    def __init__(self, backend='', rcParams=None):
        self.backend = backend if backend else 'pgf'
        self.old_backend = mpl.get_backend()
        
        self.rcParams = {
            'font.family': 'serif',
            'text.usetex': True,
            'pgf.texsystem': 'lualatex',
            'pgf.rcfonts': False,
        }

        if rcParams:
            for k in rcParams:
                self.rcParams[k] = rcParams[k]    

        self.old_rcParams = {k: mpl.rcParams[k] for k in self.rcParams}

        
    def __enter__(self):
        mpl.use(self.backend)
        for k in self.rcParams:
            mpl.rcParams[k] = self.rcParams[k]

        
    def __exit__(self, *args):
        mpl.use(self.old_backend)
        for k in self.rcParams:
            mpl.rcParams[k] = self.old_rcParams[k]


def save_fig(fig, filename_base, resize=Size.SMALL, **kwargs):
    if 'dpi' not in kwargs:
        kwargs['dpi'] = cfg['dpi']

    if resize:
        fig.set_size_inches(resize.get_size())
        
    ftypes = ['png',]
    if mpl.get_backend() == 'pgf':
        ftypes.append('pgf')

        fig.tight_layout()


    png_fqn = None
    for ftype in ftypes:
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

    if mpl.get_backend() == 'pgf':
        w, h = fig.get_size_inches() * 100
        w, h = int(w), int(h)
        img = display.Image(png_fqn, width=w, height=h)

        out = ipywidgets.Output()
        out.append_display_data(img)
        out.append_display_data(link)
        return out
    else:
        return link


def img_grid(outputs, *, n_columns, width=300):
    tuples = [o.outputs for o in outputs]
    
    cells = []
    for img, link in tuples:
        img = img['data']['image/png']
        link = link['data']['text/html']
        cells.append('<br/>'.join([
            f'<img src="data:image/png;base64,{img}" width={width}px />',
            link
        ]))
    
    n_rows = len(cells) // n_columns
    if n_rows * n_columns < len(cells):
        n_rows += 1
    
    rows = []
    for i in range(n_rows):
        start = i * n_columns
        end = start + n_columns
        row = [f'<td style="text-align:center">{cell}</td>' for cell in cells[start:end]]
        rows.append(''.join(row))
    
    body = ''.join([f'<tr>{row}</tr>' for row in rows])
    return display.HTML(f'<table>{body}</table>')
