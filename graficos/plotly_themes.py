import copy
import plotly.io as pio

_TRANSPARENT = "rgba(0,0,0,0)"

# === PALETA RODLER PLOTLY ===
_RODLER_LIGHT = dict(
    layout=dict(
        paper_bgcolor=_TRANSPARENT,
        plot_bgcolor=_TRANSPARENT,
        font=dict(color="#0F172A", family="Poppins, Inter, Segoe UI"),
        title=dict(font=dict(size=18, color="#0F172A")),
        legend=dict(bgcolor=_TRANSPARENT, borderwidth=0),
        hoverlabel=dict(bgcolor="rgba(243,244,246,0.92)", font=dict(color="#0F172A")),
        xaxis=dict(gridcolor="rgba(0,0,0,0.08)", zeroline=False),
        yaxis=dict(gridcolor="rgba(0,0,0,0.08)", zeroline=False),
        colorway=["#2979FF", "#60A5FA", "#0EA5E9", "#0284C7", "#2563EB"],
    )
)

_RODLER_DARK = dict(
    layout=dict(
        paper_bgcolor=_TRANSPARENT,
        plot_bgcolor=_TRANSPARENT,
        font=dict(color="#E5E7EB", family="Poppins, Inter, Segoe UI"),
        title=dict(font=dict(size=18, color="#E5E7EB")),
        legend=dict(bgcolor=_TRANSPARENT, borderwidth=0),
        hoverlabel=dict(bgcolor="rgba(15,23,42,0.92)", font=dict(color="#E5E7EB")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", zeroline=False),
        colorway=["#3B82F6", "#60A5FA", "#93C5FD", "#1D4ED8", "#2563EB"],
    )
)


def apply_plotly_theme(dark: bool = False):
    """Aplica el tema Rodler global a Plotly con fondo totalmente transparente."""
    template = copy.deepcopy(_RODLER_DARK if dark else _RODLER_LIGHT)
    pio.templates["rodler"] = template
    pio.templates.default = "rodler"
