"""Shared visual style for all ČT climate media charts.

Import at the top of any visualization script:
    from analysis.viz_style import apply_style, COLORS, PALETTE
or if running from the script's own directory:
    import sys; sys.path.insert(0, str(Path(__file__).parent.parent))
    from viz_style import apply_style, COLORS, PALETTE
"""

import matplotlib.pyplot as plt
import matplotlib as mpl

# ── Brand palette ──────────────────────────────────────────────────────────────
COLORS = {
    'primary':    '#8B1A1A',   # dark red — main data series, bars, lines
    'secondary':  '#C44E52',   # mid red — secondary series
    'accent':     '#E8A090',   # salmon — highlights, fill alpha
    'neutral':    '#6B6B6B',   # dark grey — neutral/S0
    'background': '#FFFAF5',   # cream — figure background
    'grid':       '#E0D8CF',   # warm grey — gridlines
    'text':       '#2B2B2B',   # near-black — all text
    'positive':   '#2E6B3E',   # dark green — informer/S6 when needed
}

# Ordered palette for multi-series charts (stances, speaker types, topics)
PALETTE = [
    '#8B1A1A',  # dark red
    '#C44E52',  # mid red
    '#E8A090',  # salmon
    '#4C6B9A',  # slate blue
    '#6B9A4C',  # muted green
    '#9A7A4C',  # tan
    '#7A4C9A',  # purple
    '#4C9A8B',  # teal
    '#9A8B4C',  # olive
    '#4C4C9A',  # indigo
]

# Stance colour mapping (consistent across all charts)
STANCE_COLORS = {
    'S0': '#AAAAAA',   # neutral — grey
    'S1': '#8B1A1A',   # denier — dark red
    'S2': '#C44E52',   # manipulator — mid red
    'S3': '#E07B39',   # delayer — orange
    'S4': '#4C6B9A',   # techno-optimist — blue
    'S5': '#9A7A4C',   # market-only — tan
    'S6': '#2E6B3E',   # informer — green
}

STANCE_LABELS = {
    'S0': 'Neutral',
    'S1': 'Denier',
    'S2': 'Manipulator',
    'S3': 'Delayer',
    'S4': 'Techno-optimist',
    'S5': 'Market-only',
    'S6': 'Informer',
}

TYPE_COLORS = {
    'M1': '#6B6B6B',
    'M2': '#4C6B9A',
    'M3': '#2E6B3E',
    'M4': '#8B1A1A',
    'M5': '#9A7A4C',
    'M6': '#C44E52',
}


def apply_style():
    """Apply the shared rcParams to matplotlib. Call once per script."""
    mpl.rcParams.update({
        # Figure
        'figure.facecolor':    COLORS['background'],
        'axes.facecolor':      COLORS['background'],
        'savefig.facecolor':   COLORS['background'],
        # Text
        'font.family':         'sans-serif',
        'font.sans-serif':     ['DejaVu Sans', 'Liberation Sans', 'Arial'],
        'text.color':          COLORS['text'],
        'axes.labelcolor':     COLORS['text'],
        'xtick.color':         COLORS['text'],
        'ytick.color':         COLORS['text'],
        # Font sizes
        'font.size':           11,
        'axes.titlesize':      13,
        'axes.labelsize':      11,
        'xtick.labelsize':     10,
        'ytick.labelsize':     10,
        'legend.fontsize':     10,
        # Grid
        'axes.grid':           True,
        'grid.color':          COLORS['grid'],
        'grid.linewidth':      0.6,
        'axes.axisbelow':      True,
        # Spines
        'axes.spines.top':     False,
        'axes.spines.right':   False,
        'axes.edgecolor':      COLORS['grid'],
        # Lines
        'lines.linewidth':     2.0,
        'patch.linewidth':     0.5,
        # Legend
        'legend.framealpha':   0.85,
        'legend.edgecolor':    COLORS['grid'],
        # DPI
        'figure.dpi':          100,
        'savefig.dpi':         150,
    })
