from pathlib import Path

from .figtools import save_fig
from .figtools import Size as fig_size
from .figtools import IMG_DIR

import matplotlib as mpl

mpl.use('pgf')
mpl.rcParams.update({
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.texsystem': 'lualatex',
    'pgf.rcfonts': False,
})

Path('img').mkdir(exist_ok=True)
