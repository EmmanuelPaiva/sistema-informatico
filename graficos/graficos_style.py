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

BASE_DPI = 96

RADIUS      = 16
PADDING     = 16

def disable_layout_engine(fig):
    """Desactiva cualquier layout engine para permitir subplots_adjust sin warnings."""
    if fig is None:
        return
    try:
        getter = getattr(fig, "get_layout_engine", None)
        if callable(getter):
            engine = getter()
            if engine != "none":
                fig.set_layout_engine("none")
            return
    except Exception:
        pass
    try: fig.set_constrained_layout(False)
    except Exception: pass
    try: fig.set_tight_layout(False)
    except Exception: pass

# ========= APLICAR TEMA GLOBAL =========
def apply_rodler_chart_style() -> None:
    global INK_MAIN, INK_SOFT, INK_MUTE, BG, GRID_COLOR, GRID_ALPHA
    # tokens light
    INK_MAIN = "#0F172A"; INK_SOFT = "#64748B"; INK_MUTE = "#94A3B8"
    BG = "#FFFFFF"; GRID_COLOR = "#E2E8F0"; GRID_ALPHA = 0.45
    plt.rcParams.update({
        "figure.dpi": BASE_DPI,
        "savefig.dpi": BASE_DPI,
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

        "figure.autolayout": False,
        "figure.constrained_layout.use": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

def apply_rodler_chart_style_dark() -> None:
    """Apply dark palette matching app dark theme."""
    global INK_MAIN, INK_SOFT, INK_MUTE, BG, GRID_COLOR, GRID_ALPHA
    # tokens dark
    INK_MAIN = "#E5E7EB"; INK_SOFT = "#9CA3AF"; INK_MUTE = "#94A3B8"
    BG = "#0F172A"; GRID_COLOR = "#1F2A44"; GRID_ALPHA = 0.55
    plt.rcParams.update({
        "figure.dpi": BASE_DPI,
        "savefig.dpi": BASE_DPI,
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

        "figure.autolayout": False,
        "figure.constrained_layout.use": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


_LIGHT_BASE_COLORS = {"#0F172A", "#0f172a"}
_DARK_BASE_COLORS = {"#E5E7EB", "#e5e7eb"}
_LIGHT_MUTED_COLORS = {"#64748B", "#64748b"}
_DARK_MUTED_COLORS = {"#9CA3AF", "#9ca3af", "#94A3B8", "#94a3b8"}


def apply_chart_theme(dark: bool) -> None:
    """Entry point to update global chart palette."""
    apply_rodler_chart_style_dark() if dark else apply_rodler_chart_style()


def restyle_figure(fig: plt.Figure) -> None:
    """Retint an existing Matplotlib figure to the current theme tokens."""
    if fig is None:
        return
    try:
        fig.set_facecolor(BG)
        for ax in fig.get_axes():
            ax.set_facecolor(BG)
            ax.tick_params(colors=INK_SOFT, labelcolor=INK_SOFT)
            if ax.title: ax.title.set_color(INK_MAIN)
            if ax.xaxis and ax.xaxis.label: ax.xaxis.label.set_color(INK_MAIN)
            if ax.yaxis and ax.yaxis.label: ax.yaxis.label.set_color(INK_MAIN)
            for spine in ax.spines.values():
                spine.set_edgecolor(GRID_COLOR)
            for gridline in ax.get_xgridlines() + ax.get_ygridlines():
                gridline.set_color(GRID_COLOR)
                gridline.set_alpha(GRID_ALPHA)
            # Text nodes: update those using base/muted palettes
            for txt in ax.texts:
                col = txt.get_color()
                if isinstance(col, str):
                    low = col.lower()
                    if low in _LIGHT_BASE_COLORS or low in _DARK_BASE_COLORS:
                        txt.set_color(INK_MAIN)
                    elif low in _LIGHT_MUTED_COLORS or low in _DARK_MUTED_COLORS:
                        txt.set_color(INK_SOFT)
            # Legend text
            legend = ax.get_legend()
            if legend:
                for txt in legend.get_texts():
                    txt.set_color(INK_MAIN)
                frame = legend.get_frame()
                if frame:
                    frame.set_facecolor("none")
                    frame.set_edgecolor("none")
    finally:
        try:
            fig.canvas.draw_idle()
        except Exception:
            pass

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
    """Ajuste seguro: respeta márgenes personalizados y evita motores automáticos."""
    if fig is None:
        return
    if getattr(fig, "_rodler_custom_margins", False):
        return
    try:
        disable_layout_engine(fig)
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

# --- Donut “Willow” (total arriba, título abajo, leyenda vertical) ---
def donut_willow(ax, percent_text: str, values, labels, colors=None):
    """
    Estilo Rodler:
    - Total grande arriba del donut (afuera).
    - "Gastos por tipo" debajo del donut (afuera).
    - Leyenda vertical (una por línea) con % y monto.
    - Donut más grande y centrado.
    """
    import numpy as np
    import matplotlib.patches as mpatches

    vals = np.asarray(values, dtype=float)
    total = float(vals.sum()) if vals.size else 0.0
    if total <= 0:
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                fontsize=11, color=INK_SOFT)
        ax.set_axis_off()
        return []

    if colors is None:
        colors = [P_PRIMARY, P_SECONDARY, P_ACCENT, P_WARN, P_DANGER, INK_MUTE]

    # Donut grande (más radio, aro un poco más ancho)
    wedges = ax.pie(
        vals,
        labels=None,
        startangle=90,
        colors=colors[:len(vals)],
        wedgeprops=dict(width=0.44, edgecolor="white"),  # aro más ancho
        radius=1.05,                                     # donut ligeramente mayor
        autopct=None,
        normalize=True
    )[0]

    # Centro vacío
    ax.add_artist(plt.Circle((0, 0), 0.60, fc=BG))
    ax.set_aspect("equal")

    # Mucho menos margen para que el donut crezca
    ax.margins(0.04)

    # ===== Textos FUERA del donut usando coords de ejes =====
    # Total arriba (y > 1) y título abajo (y < 0)
    ax.text(0.5, 1.10, f"{fmt_thousands(total).replace(',', '.')} Gs",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=16, color=INK_MAIN, fontweight="bold")
    ax.text(0.5, -0.14, "Gastos por tipo",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=10, color=INK_SOFT)

    # ===== Leyenda vertical (una por línea) =====
    pct = (vals / total) * 100.0
    legend_labels = [
        f"{short_label(lbl, 28)} · {p:.1f}% · {fmt_thousands(v).replace(',', '.')} Gs"
        for lbl, p, v in zip(labels, pct, vals)
    ]
    handles = [mpatches.Patch(color=c, label=txt)
               for c, txt in zip(colors[:len(vals)], legend_labels)]

    # Columna única, centrada, debajo del donut
    lg = ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.32),   # más abajo para que no choque
        frameon=False,
        ncols=1,
        columnspacing=0.8,
        handlelength=1.6,
        handleheight=0.9,
        borderaxespad=0.0,
        fontsize=9,
        handletextpad=0.6,
    )

    # Limpieza visual
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
    return wedges


# ---- Donut genérico “Rodler” limpio y centrado ----
def donut(ax, labels, values, center_label: str = "", colors: Optional[Sequence[str]] = None):
    """
    Donut genérico estilizado para widgets Rodler:
    - Mantiene firma compatible con el original.
    - Sin textos sobre las porciones (autopct).
    - Centro limpio: total grande + subtítulo opcional.
    - Leyenda opcional centrada debajo del gráfico (si labels disponibles).
    """
    import numpy as np

    vals = np.asarray(values, dtype=float)
    total = float(vals.sum()) if vals.size else 0.0
    if total <= 0:
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                fontsize=11, color=INK_SOFT)
        ax.set_axis_off()
        return []

    if colors is None:
        colors = [P_PRIMARY, P_SECONDARY, P_ACCENT, P_WARN, P_DANGER, INK_MUTE]

    # Gráfico limpio sin autopct
    wedges = ax.pie(
        vals,
        labels=None,
        startangle=90,
        colors=colors[:len(vals)],
        wedgeprops=dict(width=0.44, edgecolor="white"),
        autopct=None,
        normalize=True
    )[0]

    # Fondo interno y centrado
    ax.add_artist(plt.Circle((0, 0), 0.60, fc=BG))
    ax.set_aspect("equal")
    ax.margins(0.22)

    # === CENTRO ===
    # Total grande arriba
    ax.text(0, 0.10, f"{fmt_thousands(total).replace(',', '.')} Gs",
            ha="center", va="center", fontsize=16,
            color=INK_MAIN, fontweight="bold")
    # Subtítulo o label abajo
    if center_label:
        ax.text(0, -0.10, str(center_label), ha="center", va="center",
                fontsize=10, color=INK_SOFT)

    # === LEYENDA (si hay etiquetas) ===
    if labels and len(labels) == len(vals):
        pct = (vals / total) * 100.0
        legend_labels = [
            f"{short_label(lbl, 22)} · {p:.1f}% · {fmt_thousands(v).replace(',', '.')} Gs"
            for lbl, p, v in zip(labels, pct, vals)
        ]
        legend_chips(
            ax,
            labels_colors=list(zip(legend_labels, colors[:len(vals)])),
            loc="lower center",
            anchor=(0.5, -0.28),
            fontsize=9
        )

    # Limpieza visual
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
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
