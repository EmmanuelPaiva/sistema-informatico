# graficos_dashboard_plotly.py — versión final con soporte completo dark/light y fondos coherentes
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sqlalchemy import text

# === Tema Plotly ===
from graficos.plotly_themes import apply_plotly_theme

# === Detección del tema del sistema Rodler ===
try:
    from main.themes import is_dark_mode
except Exception:
    def is_dark_mode() -> bool:
        return False

# === Engine SQL ===
from graficos.graficos_dashboard import get_engine

_TRANSPARENT = "rgba(0,0,0,0)"

_SP_MONTHS = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

# Paletas corporativas (Rodler)
_PALETTE_LIGHT = ["#2979FF", "#5EA8FF", "#60A5FA", "#90CAF9", "#93C5FD", "#1D4ED8"]
_PALETTE_DARK = ["#60A5FA", "#3B82F6", "#93C5FD", "#1D4ED8", "#5EA8FF", "#2563EB"]

def _pal():
    return _PALETTE_DARK if is_dark_mode() else _PALETTE_LIGHT

def _rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def _month_floor(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def _months_back_start(meses: int) -> datetime:
    end = _month_floor(datetime.today())
    return _month_floor(end - relativedelta(months=meses - 1))

def _maybe_scale_to_millions(s: pd.Series):
    m = float(s.max()) if len(s) else 0
    if m >= 10_000_000:
        return (s / 1_000_000.0), " (millones)"
    return s.astype(float), ""

def _fmt_gs(v: float) -> str:
    return f"{int(round(v)):,}".replace(",", ".") + " Gs"

def _base_layout(extra: dict | None = None) -> dict:
    """Layout base coherente con el tema actual."""
    dark = is_dark_mode()
    apply_plotly_theme(dark)
    bg = _TRANSPARENT
    font_color = "#E5E7EB" if dark else "#0F172A"
    grid_color = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.08)"
    base = dict(
        template="rodler",
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        margin=dict(l=72, r=28, t=20, b=40),
        font=dict(family="Poppins, Segoe UI, Arial, sans-serif", color=font_color),
        legend=dict(orientation="h", x=0, y=1.16),
        xaxis=dict(showgrid=True, gridcolor=grid_color, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=grid_color, zeroline=False, title_standoff=12)
    )
    if extra:
        base.update(extra)
    return base

# =============================
# 1) Ventas vs Compras
# =============================
def create_ventas_vs_compras_plotly(engine=None, meses: int = 12) -> go.Figure:
    eng = engine or get_engine()
    desde = _months_back_start(meses).date()
    with eng.connect() as con:
        try:
            dfv = pd.read_sql(text("""
                SELECT periodo::date AS periodo, total::numeric
                FROM public.mv_ventas_mensual WHERE periodo >= :desde ORDER BY periodo
            """), con, params={"desde": desde})
        except Exception:
            dfv = pd.read_sql(text("""
                SELECT date_trunc('month', fecha_venta)::date AS periodo,
                       COALESCE(SUM(total_venta),0) AS total
                FROM public.ventas WHERE fecha_venta >= :desde GROUP BY 1 ORDER BY 1
            """), con, params={"desde": desde})
        try:
            dfc = pd.read_sql(text("""
                SELECT periodo::date AS periodo, total::numeric
                FROM public.mv_compras_mensual WHERE periodo >= :desde ORDER BY periodo
            """), con, params={"desde": desde})
        except Exception:
            dfc = pd.read_sql(text("""
                SELECT date_trunc('month', fecha)::date AS periodo,
                       COALESCE(SUM(total_compra),0) AS total
                FROM public.compras WHERE fecha >= :desde GROUP BY 1 ORDER BY 1
            """), con, params={"desde": desde})

    idx = pd.to_datetime([( _month_floor(datetime.today()) - pd.DateOffset(months=i)).date()
                          for i in range(meses - 1, -1, -1)])
    sv = dfv.set_index(pd.to_datetime(dfv['periodo']))['total'].reindex(idx, fill_value=0)
    sc = dfc.set_index(pd.to_datetime(dfc['periodo']))['total'].reindex(idx, fill_value=0)
    sv_s, suf = _maybe_scale_to_millions(sv)
    sc_s, _ = _maybe_scale_to_millions(sc)
    labels = [_SP_MONTHS[d.month - 1] for d in idx]
    pal = _pal()

    fig = go.Figure()
    fig.add_bar(name="Ventas",  x=labels, y=sv_s, marker_color=pal[0])
    fig.add_bar(name="Compras", x=labels, y=sc_s, marker_color=pal[1])
    fig.update_layout(_base_layout(dict(barmode="group", yaxis_title=f"Monto{suf}")))
    fig.update_layout(paper_bgcolor=_TRANSPARENT, plot_bgcolor=_TRANSPARENT)
    return fig

# =============================
# 2) Gastos mensuales
# =============================
def create_gastos_mensuales_plotly(engine=None, meses: int = 12) -> go.Figure:
    eng = engine or get_engine()
    desde = _months_back_start(meses).date()
    with eng.connect() as con:
        try:
            df = pd.read_sql(text("""
                SELECT periodo::date AS periodo, total::numeric
                FROM public.mv_gastos_mensual WHERE periodo >= :desde ORDER BY periodo
            """), con, params={"desde": desde})
        except Exception:
            df = pd.read_sql(text("""
                SELECT date_trunc('month', fecha)::date AS periodo,
                       COALESCE(SUM(costo_total),0) AS total
                FROM public.gastos WHERE fecha >= :desde GROUP BY 1 ORDER BY 1
            """), con, params={"desde": desde})

    idx = pd.to_datetime([( _month_floor(datetime.today()) - pd.DateOffset(months=i)).date()
                          for i in range(meses - 1, -1, -1)])
    s = df.set_index(pd.to_datetime(df['periodo']))['total'].reindex(idx, fill_value=0)
    s_s, suf = _maybe_scale_to_millions(s)
    labels = [_SP_MONTHS[d.month - 1] for d in idx]
    line_c = _pal()[0]

    fig = go.Figure()
    fig.add_scatter(x=labels, y=s_s, mode="lines+markers", name="Gastos",
                    line=dict(color=line_c, width=3),
                    marker=dict(color=line_c, size=7),
                    fill="tozeroy", fillcolor=_rgba(line_c, 0.18))
    fig.update_layout(_base_layout(dict(yaxis_title=f"Monto{suf}")))
    fig.update_layout(paper_bgcolor=_TRANSPARENT, plot_bgcolor=_TRANSPARENT)
    return fig

# =============================
# 3) Presupuesto vs Gasto por obra
# =============================
def create_presupuesto_vs_gasto_plotly(engine=None, top_n: int = 10) -> go.Figure:
    eng = engine or get_engine()
    with eng.connect() as con:
        df = pd.read_sql(text("""
            WITH gasto_por_obra AS (
                SELECT obra_id, COALESCE(SUM(costo_total),0) AS gasto
                FROM public.trabajos GROUP BY obra_id
            )
            SELECT o.id_obra, COALESCE(NULLIF(TRIM(o.nombre),''),'(Sin nombre)') AS nombre,
                   COALESCE(o.presupuesto_total,0) AS presupuesto, COALESCE(g.gasto,0) AS gasto
            FROM public.obras o
            LEFT JOIN gasto_por_obra g ON g.obra_id=o.id_obra
            ORDER BY o.presupuesto_total DESC NULLS LAST LIMIT :n
        """), con, params={"n": int(top_n)})

    if df.empty:
        return go.Figure(layout=_base_layout(dict(annotations=[dict(text="Sin datos de obras",
            showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper")])))

    pres_s, suf = _maybe_scale_to_millions(df["presupuesto"])
    gast_s, _ = _maybe_scale_to_millions(df["gasto"])
    cats = [c if len(c) <= 28 else c[:27] + "…" for c in df["nombre"]]
    pal = _pal()

    fig = go.Figure()
    fig.add_bar(name="Presupuesto", x=cats, y=pres_s, marker_color=pal[1])
    fig.add_bar(name="Gasto", x=cats, y=gast_s, marker_color=pal[0])

    with np.errstate(divide="ignore", invalid="ignore"):
        pct = (df["gasto"] / df["presupuesto"].replace(0, np.nan)) * 100
    pct = pct.fillna(0).round(1)
    fig.update_traces(selector=dict(name="Gasto"),
                      text=[f"{p:.1f}%" for p in pct], textposition="outside")

    fig.update_layout(_base_layout(dict(
        barmode="group",
        yaxis_title=f"Monto{suf}",
        margin=dict(l=72, r=20, t=10, b=86)
    )))
    fig.update_layout(paper_bgcolor=_TRANSPARENT, plot_bgcolor=_TRANSPARENT)
    return fig

# =============================
# 4) Donut de gastos por tipo
# =============================
def create_gastos_por_tipo_plotly(engine=None, max_cats=5, min_pct_otro=0.03) -> go.Figure:
    eng = engine or get_engine()
    with eng.connect() as con:
        df = pd.read_sql(text("""
            SELECT COALESCE(NULLIF(TRIM(tipo),''),'Sin tipo') AS tipo,
                   SUM(COALESCE(costo_total,0)) AS total
            FROM public.gastos GROUP BY 1 HAVING SUM(COALESCE(costo_total,0)) > 0
            ORDER BY total DESC
        """), con)

    if df.empty:
        return go.Figure(layout=_base_layout(dict(annotations=[dict(text="Sin datos de gastos",
            showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper")])))

    total = float(df["total"].sum())
    df["pct"] = df["total"] / total
    big = df[df["pct"] >= min_pct_otro]
    small = df[df["pct"] < min_pct_otro]
    otros_total = small["total"].sum()
    if otros_total > 0:
        big = pd.concat([big, pd.DataFrame([{"tipo": "Otros", "total": otros_total}])])

    vals, labels = big["total"].to_list(), big["tipo"].to_list()
    total_final = float(sum(vals))
    colors = (_pal() * ((len(vals)//len(_pal()))+1))[:len(vals)]

    fig = go.Figure(data=[go.Pie(labels=labels, values=vals, hole=0.58,
                                 marker=dict(colors=colors, line=dict(color="white", width=1)),
                                 hovertemplate="%{label}: %{value:,.0f} Gs<extra></extra>")])
    fig.add_annotation(text=_fmt_gs(total_final),
                       x=0.86, y=0.94, xref="paper", yref="paper",
                       showarrow=False, font=dict(size=18))
    fig.update_layout(_base_layout(dict(
        margin=dict(l=72, r=26, t=10, b=26),
        legend=dict(orientation="v", x=0.0, y=1.0)
    )))
    fig.update_layout(paper_bgcolor=_TRANSPARENT, plot_bgcolor=_TRANSPARENT)
    return fig

# =============================
# 5) Helper HTML dinámico
# =============================
def fig_to_html(fig, dark: bool = False) -> str:
    """Convierte el gráfico a HTML con fondo totalmente transparente."""
    apply_plotly_theme(bool(dark))
    fig.update_layout(paper_bgcolor=_TRANSPARENT, plot_bgcolor=_TRANSPARENT)
    html = fig.to_html(include_plotlyjs="cdn", full_html=False)
    style_tag = "<style>html,body{background:transparent!important;margin:0;}</style>"
    if "<head>" in html:
        html = html.replace("<head>", f"<head>{style_tag}", 1)
    else:
        html = style_tag + html
    html = html.replace("<body>", '<body style="background: transparent !important; margin:0;">', 1)
    return html
