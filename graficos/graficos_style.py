from __future__ import annotations
import math, textwrap
from typing import Optional, Sequence, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

# ========= TOKENS =========
P_PRIMARY   = "#2563EB"
P_SECONDARY = "#60A5FA"
P_ACCENT    = "#22C55E"
P_WARN      = "#F59E0B"
P_DANGER    = "#EF4444"

INK_MAIN    = "#0F172A"
INK_SOFT    = "#64748B"
INK_MUTE    = "#94A3B8"

BG          = "#FFFFFF"
BG_LIGHT    = "#F7F8FC"
GRID_COLOR  = "#E2E8F0"
GRID_ALPHA  = 0.45
FONT_STACK  = "Segoe UI, Inter, DejaVu Sans, Arial"

RADIUS      = 16
PADDING     = 16

# ========= APLICAR TEMA GLOBAL =========
def apply_rodler_chart_style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [s.strip() for s in FONT_STACK.split(",")],

        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "axes.edgecolor": GRID_COLOR,
        "axes.labelcolor": INK_MAIN,
        "xtick.color": INK_SOFT,
        "ytick.color": INK_SOFT,

        "axes.grid": True,
        "grid.color": GRID_COLOR,
        "grid.alpha": GRID_ALPHA,
        "grid.linestyle": "-",
        "axes.axisbelow": True,

        "axes.titleweight": "bold",
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.frameon": False,

        "figure.autolayout": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

# ========= FORMATEADORES & HELPERS =========
def fmt_thousands(x: float, _pos=None) -> str:
    try:
        return f"{int(round(x)):,}".replace(",", ".")
    except Exception:
        return str(x)

def fmt_thousands_smart(x: float, _pos=None) -> str:
    try:
        ax_abs = abs(x)
        if ax_abs < 10:    s = f"{x:,.2f}"
        elif ax_abs < 1e3: s = f"{x:,.1f}"
        else:              s = f"{x:,.0f}"
        return s.replace(",", ".")
    except Exception:
        return str(x)

def short_label(s: str, width: int = 24) -> str:
    return textwrap.shorten(str(s), width=width, placeholder="…")

def tight_fig(fig: plt.Figure, pad: float = 0.8) -> None:
    try:
        fig.tight_layout(pad=pad)
    except Exception:
        pass

def maybe_scale_to_millions(series) -> Tuple[np.ndarray, str]:
    try:
        import pandas as pd
        if isinstance(series, pd.Series):
            m = series.max() if len(series) else 0
            if m >= 10_000_000:
                return (series / 1_000_000.0).to_numpy(), " (millones)"
            return series.to_numpy(), ""
    except Exception:
        pass
    arr = np.asarray(series)
    m = arr.max() if arr.size else 0
    if m >= 10_000_000:
        return arr / 1_000_000.0, " (millones)"
    return arr, ""

# --- Formateador compacto '1k' ---
def fmt_kilo_compact(x: float, _pos=None) -> str:
    try:
        if abs(x) >= 1000:
            return f"{int(round(x/1000.0))}k"
        return f"{int(round(x))}"
    except Exception:
        return str(x)

# --- Leyenda tipo chips (como el mock) ---
def legend_chips(ax, labels_colors, loc="upper left", anchor=(0, 1), fontsize=10):
    import matplotlib.patches as mpatches
    handles = [mpatches.Patch(color=c, label=lbl) for lbl, c in labels_colors]
    lg = ax.legend(
        handles=handles, loc=loc, bbox_to_anchor=anchor, frameon=False,
        ncols=len(labels_colors), columnspacing=1.4, handlelength=1.4,
        handleheight=0.8, borderaxespad=0, fontsize=fontsize
    )
    return lg

# --- Estructura base de ejes: grilla horizontal, headroom, etc. ---
def pro_axes(ax: plt.Axes,
             title: Optional[str]=None,
             y_formatter: Optional[FuncFormatter]=None,
             rotate_xticks: int=0,
             y_integer_ticks: bool=False,
             headroom: float=0.10) -> None:
    if title:
        ax.set_title(title)
    if y_integer_ticks:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    if y_formatter is not None:
        ax.yaxis.set_major_formatter(y_formatter)
    if rotate_xticks:
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(rotate_xticks)
            lbl.set_horizontalalignment("right")
    # Solo grilla horizontal (mock)
    ax.grid(axis="y", which="major")
    ax.grid(axis="x", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # headroom arriba
    try:
        ymin, ymax = ax.get_ylim()
        if ymax > 0:
            ax.set_ylim(ymin, ymax * (1 + headroom))
    except Exception:
        pass

# --- Header “Overall Sales” + subheader “Total Order : 24.890” ---
def draw_overall_sales_header(ax, total_value_str: str):
    ax.text(0.0, 1.15, "Overall Sales",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=12, color=INK_MAIN, fontweight="bold")
    ax.text(0.0, 1.07, "Total Order :", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=12, color=INK_MAIN)
    ax.text(0.25, 1.07, total_value_str, transform=ax.transAxes,
            ha="left", va="bottom", fontsize=12, color=P_PRIMARY, fontweight="bold")

# --- Barras agrupadas “Willow” (idéntico al mock) ---
def add_value_labels(ax: plt.Axes,
                     bars,
                     fmt=fmt_thousands_smart,
                     dy: int = 4,
                     fontsize: int = 9,
                     color: str = INK_MAIN) -> None:
    for r in bars:
        h = r.get_height()
        if math.isnan(h):
            continue
        ax.annotate(fmt(h),
                    xy=(r.get_x() + r.get_width()/2.0, h),
                    xytext=(0, dy),
                    textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=fontsize, color=color)

def bars_grouped_willow(ax: plt.Axes,
                        categories: Sequence[str],
                        series: Sequence[Sequence[float]],
                        labels: Sequence[str],
                        colors: Sequence[str]=(P_PRIMARY, P_SECONDARY),
                        show_values: bool=False) -> None:
    x = np.arange(len(categories))
    n = len(series)
    w = 0.6 / max(n, 1)   # barras más delgadas
    for i, y in enumerate(series):
        offs = (i - (n-1)/2) * w
        bars = ax.bar(x + offs, y, width=w, label=labels[i],
                      color=colors[i % len(colors)], linewidth=0)
        if show_values:
            add_value_labels(ax, bars, dy=3, fontsize=9)
    ax.set_xticks(x, categories)
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_kilo_compact))
    pro_axes(ax, title=None, rotate_xticks=0)

# --- Donut “Willow” (aro ancho + centro porcentaje) ---
def donut_willow(ax, percent_text: str, values, labels, colors=None):
    if colors is None:
        colors = [P_PRIMARY, P_SECONDARY, INK_MUTE]
    pie_result = ax.pie(
        values,
        labels=None,
        startangle=90,
        colors=colors[:len(values)],
        wedgeprops=dict(width=0.42, edgecolor="white"),
        autopct=None,
        normalize=True
    )
    wedges = pie_result[0]
    ax.add_artist(plt.Circle((0, 0), 0.58, fc=BG))
    ax.set_aspect("equal")
    ax.text(0, 0.05, percent_text, ha="center", va="center",
            fontsize=20, color=INK_MAIN, fontweight="bold")
    ax.text(0, -0.12, "Total Sales", ha="center", va="center",
            fontsize=10, color=INK_SOFT)
    pro_axes(ax)
    legend_chips(ax, list(zip(labels, colors[:len(values)])),
                 loc="lower left", anchor=(0, -0.05), fontsize=10)
    return wedges

# ---- Versión donut genérica con autopct (para otros usos) ----
def donut(ax, labels, values, center_label: str = "", colors: Optional[Sequence[str]] = None):
    if colors is None:
        colors = [P_PRIMARY, P_SECONDARY, INK_MUTE, P_ACCENT, P_WARN, P_DANGER]

    pie_result = ax.pie(
        values,
        labels=None,
        startangle=90,
        colors=colors[:len(values)],
        wedgeprops=dict(width=0.38, edgecolor="white"),
        autopct=lambda p: f"{p:.1f}%",
        pctdistance=0.78,
        textprops={"color": INK_MAIN, "fontsize": 9},
        normalize=True
    )

    if len(pie_result) == 3:
        wedges, _texts, _autotexts = pie_result
    else:
        wedges, _texts = pie_result

    ax.add_artist(plt.Circle((0, 0), 0.58, fc=BG))
    ax.set_aspect("equal")

    if center_label:
        ax.text(0, 0, center_label, ha="center", va="center",
                fontsize=14, weight="bold", color=INK_MAIN)

    pro_axes(ax)
    return wedges

# --- Línea suave genérica (para series temporales) ---
def line_smooth(ax: plt.Axes,
                x_labels: Sequence[str],
                y: Sequence[float],
                title: str="",
                area: bool=True,
                color: str=P_PRIMARY) -> None:
    x = np.arange(len(x_labels))
    ax.plot(x, y, linewidth=2.4, marker="o", color=color)
    if area:
        ax.fill_between(x, 0, y, alpha=0.12, color=color)
    ax.set_xticks(x, x_labels)
    pro_axes(ax, title=title, y_formatter=FuncFormatter(fmt_thousands_smart), rotate_xticks=30)
