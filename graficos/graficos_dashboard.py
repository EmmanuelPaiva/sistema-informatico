# graficos_dashboard.py — optimizado (usa MVs si existen, fallback a tablas; misma lógica/salida)

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

from graficos import graficos_style as gs
gs.apply_chart_theme(False)

# --- Abreviaturas de meses en español (independiente del locale) ---
_SP_MONTHS = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

# === Canonicalización de categorías (sin textos del mock) ===
_CATEGORIA_MAP = {
    "material": "Materiales", "materials": "Materiales",
    "labor": "Mano de obra", "mano de obra": "Mano de obra",
    "transport": "Transporte", "logistics": "Transporte", "transporte": "Transporte",
    "utilities": "Servicios", "services": "Servicios", "servicios": "Servicios", "energy": "Servicios",
    "tools": "Herramientas y equipo", "equipment": "Herramientas y equipo",
    "overhead": "Gastos generales", "general": "Gastos generales",
    "taxes": "Impuestos", "impuestos": "Impuestos",
    "maintenance": "Mantenimiento", "mantenimiento": "Mantenimiento",
    "fees": "Comisiones", "comisiones": "Comisiones",
    "otros": "Otros", "other": "Otros", "misc": "Otros",
    "sin tipo": "Sin tipo",
}

def _canon_label(s: str) -> str:
    k = str(s or "").strip().lower()
    if not k:
        return "Sin tipo"
    if k in _CATEGORIA_MAP:
        return _CATEGORIA_MAP[k]
    return k.capitalize()

def _short(s: str, w: int = 24) -> str:
    try:
        import textwrap
        return textwrap.shorten(str(s), width=w, placeholder="…")
    except Exception:
        return str(s)

def get_engine():
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if url:
        if "sslmode=" not in url:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}sslmode=require"
        return create_engine(url, pool_pre_ping=True)
    user = os.getenv("PGUSER", "")
    pwd  = os.getenv("PGPASSWORD", "")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    db   = os.getenv("PGDATABASE", "")
    return create_engine(f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}", pool_pre_ping=True)

# =========================
# Helpers
# =========================
def _fmt_moneda(x: float, sufijo=" Gs") -> str:
    try:
        return f"{int(round(x)):,}".replace(",", ".") + sufijo
    except Exception:
        return str(x) + sufijo

def _month_floor(dt: datetime) -> datetime:
    """Primer día de mes (00:00) para un datetime dado."""
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def _months_back_start(meses: int) -> datetime:
    """Devuelve el primer día del mes de la ventana de `meses` hacia atrás (incluye el mes actual)."""
    end = _month_floor(datetime.today())
    start = end - relativedelta(months=meses - 1)
    return _month_floor(start)

def _read_df(con, sql_mv, sql_base, params=None):
    """
    Intenta leer desde la MV (columnas esperadas: periodo::date, total::numeric);
    si no existe o falla el esquema, cae a la consulta base sobre tablas.
    """
    try:
        return pd.read_sql(text(sql_mv), con, params=params)
    except ProgrammingError:
        return pd.read_sql(text(sql_base), con, params=params)

# ============================================================
# 1) Ventas vs Compras mensuales (usa MVs si existen)
# ============================================================
def create_ventas_vs_compras_mensuales(engine=None, meses=12):
    engine = engine or get_engine()
    desde = _months_back_start(meses).date()  # filtramos en SQL para menos transferencia

    with engine.connect() as con:
        # --- Ventas
        qv_mv = """
            SELECT periodo, total
            FROM public.mv_ventas_mensual
            WHERE periodo >= :desde
            ORDER BY periodo
        """
        qv_base = """
            SELECT DATE_TRUNC('month', fecha_venta)::date AS periodo,
                   COALESCE(SUM(total_venta),0) AS total
            FROM public.ventas
            WHERE fecha_venta >= :desde
            GROUP BY 1
            ORDER BY 1
        """
        dfv = _read_df(con, qv_mv, qv_base, params={"desde": desde})

        # --- Compras
        qc_mv = """
            SELECT periodo, total
            FROM public.mv_compras_mensual
            WHERE periodo >= :desde
            ORDER BY periodo
        """
        qc_base = """
            SELECT DATE_TRUNC('month', fecha)::date AS periodo,
                   COALESCE(SUM(total_compra),0) AS total
            FROM public.compras
            WHERE fecha >= :desde
            GROUP BY 1
            ORDER BY 1
        """
        dfc = _read_df(con, qc_mv, qc_base, params={"desde": desde})

    # Índice visible de meses (mismo comportamiento que tu versión)
    end = _month_floor(datetime.today())
    months = [(end - pd.DateOffset(months=i)).date() for i in range(meses - 1, -1, -1)]
    idx = pd.to_datetime(pd.Series(months))

    sv = dfv.set_index(pd.to_datetime(dfv['periodo']))['total'].reindex(idx, fill_value=0)
    sc = dfc.set_index(pd.to_datetime(dfc['periodo']))['total'].reindex(idx, fill_value=0)

    sv_scaled, suf = gs.maybe_scale_to_millions(sv)
    sc_scaled, _   = gs.maybe_scale_to_millions(sc)

    labels = [_SP_MONTHS[d.month - 1] for d in idx]

    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    gs.bars_grouped_willow(
        ax,
        categories=labels,
        series=[sv_scaled, sc_scaled],
        labels=["Ventas", "Compras"],
        colors=[gs.P_PRIMARY, gs.P_SECONDARY],
        show_values=False
    )
    ax.set_title(f"Ventas vs Compras mensuales{suf}")
    gs.legend_chips(
        ax,
        [("Ventas", gs.P_PRIMARY), ("Compras", gs.P_SECONDARY)],
        loc="upper left",
        anchor=(0, 1.03),
        fontsize=10
    )
    gs.tight_fig(fig)
    return fig

# ============================================================
# 2) Gastos mensuales (línea) — usa MV si existe
# ============================================================
def create_gastos_mensuales(engine=None, meses=12):
    engine = engine or get_engine()
    desde = _months_back_start(meses).date()

    with engine.connect() as con:
        q_mv = """
            SELECT periodo, total
            FROM public.mv_gastos_mensual
            WHERE periodo >= :desde
            ORDER BY periodo
        """
        q_base = """
            SELECT DATE_TRUNC('month', fecha)::date AS periodo,
                   COALESCE(SUM(costo_total),0) AS total
            FROM public.gastos
            WHERE fecha >= :desde
            GROUP BY 1
            ORDER BY 1
        """
        df = _read_df(con, q_mv, q_base, params={"desde": desde})

    end = _month_floor(datetime.today())
    months = [(end - pd.DateOffset(months=i)).date() for i in range(meses - 1, -1, -1)]
    idx = pd.to_datetime(pd.Series(months))

    s = df.set_index(pd.to_datetime(df['periodo']))['total'].reindex(idx, fill_value=0)
    s_scaled, suf = gs.maybe_scale_to_millions(s)
    xlabels = [_SP_MONTHS[d.month - 1] for d in idx]

    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    gs.line_smooth(ax, xlabels, s_scaled, title=f"Gastos mensuales{suf}", area=True)
    gs.tight_fig(fig)
    return fig

# ============================================================
# 3) Presupuesto vs Gasto por obra (barras agrupadas)
#    Subconsulta agregada para gasto (aprovecha idx_trabajos_obra si existe).
# ============================================================
def create_presupuesto_vs_gasto_por_obra(engine=None, top_n=10):
    """
    Compara Presupuesto vs Gasto por obra (mismo resultado), pero:
    - Suma costos de trabajos en una subconsulta agrupada (aprovecha índices por obra).
    - Limita en SQL por presupuesto (reduce transferencia).
    """
    engine = engine or get_engine()
    with engine.connect() as con:
        q = text("""
            WITH gasto_por_obra AS (
                SELECT t.obra_id, COALESCE(SUM(t.costo_total), 0) AS gasto
                FROM public.trabajos t
                GROUP BY t.obra_id
            )
            SELECT o.id_obra,
                   o.nombre,
                   COALESCE(o.presupuesto_total, 0) AS presupuesto,
                   COALESCE(g.gasto, 0) AS gasto
            FROM public.obras o
            LEFT JOIN gasto_por_obra g ON g.obra_id = o.id_obra
            ORDER BY o.presupuesto_total DESC NULLS LAST
            LIMIT :top_n
        """)
        df = pd.read_sql(q, con, params={"top_n": int(top_n)})

    if df.empty:
        fig, ax = plt.subplots(figsize=(7.6, 4.2))
        ax.text(0.5, 0.5, "Sin datos de obras", ha="center", va="center", color=gs.INK_MAIN)
        ax.axis("off")
        return fig

    cats = [gs.short_label(s, 28) for s in df["nombre"]]
    pres_scaled, suf = gs.maybe_scale_to_millions(df["presupuesto"])
    gast_scaled, _   = gs.maybe_scale_to_millions(df["gasto"])

    fig, ax = plt.subplots(figsize=(9.2, 5.0))

    x = np.arange(len(cats))
    bw = 0.36
    gap = 0.06
    pres_x = x - (bw/2 + gap/2)
    gast_x = x + (bw/2 + gap/2)

    ax.bar(pres_x, pres_scaled, width=bw, label="Presupuesto",
           color=gs.P_SECONDARY, edgecolor="white", linewidth=0.6)
    b2 = ax.bar(gast_x, gast_scaled, width=bw, label="Gasto",
                color=gs.P_PRIMARY, edgecolor="white", linewidth=0.6)

    ax.set_xticks(x, cats, rotation=0, ha="center")
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)

    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    pct = (df["gasto"] / df["presupuesto"]).replace([np.inf, -np.inf], np.nan).fillna(0) * 100
    ymax = max(float(max(gast_scaled) if len(gast_scaled) else 0),
               float(max(pres_scaled) if len(pres_scaled) else 0))
    yoff = ymax * 0.02 if ymax > 0 else 0.05

    for rect, p in zip(b2, pct.to_list()):
        h = rect.get_height()
        if h <= 0:
            continue
        ax.text(rect.get_x() + rect.get_width()/2, h + yoff, f"{p:.1f}%",
                ha="center", va="bottom", fontsize=9, color=gs.INK_MAIN)

    ax.legend(frameon=False, fontsize=9)
    ax.set_ylabel(f"Monto{suf}", fontsize=10)
    gs.pro_axes(ax, title=f"Presupuesto vs Gasto por obra{suf}")
    gs.tight_fig(fig)
    return fig

# ============================================================
# 4) Distribución de gastos por tipo (donut) — misma lógica
# ============================================================
def create_distribucion_gastos_por_tipo(engine=None, max_cats: int = 5, min_pct_otro: float = 0.03):
    engine = engine or get_engine()
    with engine.connect() as con:
        q = text("""
            SELECT COALESCE(NULLIF(TRIM(tipo), ''), 'Sin tipo') AS tipo,
                   SUM(COALESCE(costo_total, 0)) AS total
            FROM public.gastos
            GROUP BY 1
            HAVING SUM(COALESCE(costo_total,0)) > 0
        """)
        df_raw = pd.read_sql(q, con)

    if df_raw.empty:
        fig, ax = plt.subplots(figsize=(6.8, 4.0))
        ax.text(0.5, 0.5, 'Sin datos de gastos', ha='center', va='center', color=gs.INK_MAIN)
        ax.axis('off')
        return fig

    df_raw["tipo"] = df_raw["tipo"].apply(_canon_label)
    df = df_raw.groupby("tipo", as_index=False)["total"].sum()

    total = float(df["total"].sum())
    if total <= 0:
        fig, ax = plt.subplots(figsize=(6.8, 4.0))
        ax.text(0.5, 0.5, 'Sin datos de gastos', ha='center', va='center', color=gs.INK_MAIN)
        ax.axis('off')
        return fig

    df = df.sort_values("total", ascending=False).reset_index(drop=True)
    df["pct"] = df["total"] / total

    small = df[df["pct"] < min_pct_otro]
    big   = df[df["pct"] >= min_pct_otro]
    otros_total = float(small["total"].sum())
    df = big.copy()
    if otros_total > 0:
        df = pd.concat([df, pd.DataFrame([{"tipo": "Otros", "total": otros_total}])], ignore_index=True)

    if len(df) > max_cats:
        top = df.head(max_cats - 1)
        resto = df.iloc[max_cats - 1:]["total"].sum()
        df = top.copy()
        if resto > 0:
            if (df["tipo"] == "Otros").any():
                i = df.index[df["tipo"] == "Otros"][0]
                df.loc[i, "total"] += resto
            else:
                df = pd.concat([df, pd.DataFrame([{"tipo": "Otros", "total": resto}])], ignore_index=True)

    total_final = float(df["total"].sum())
    df["pct"] = df["total"] / total_final

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    base_colors = [gs.P_PRIMARY, gs.P_SECONDARY, gs.P_ACCENT, gs.P_WARN, gs.P_DANGER, gs.INK_MUTE]
    colors = (base_colors * ((len(df) // len(base_colors)) + 1))[:len(df)]

    labels = df["tipo"].tolist()
    values = df["total"].to_numpy(dtype=float)

    gs.donut_willow(ax, percent_text="", values=values, labels=labels, colors=colors)
    gs.tight_fig(fig)
    return fig

# ============================================================
# 5) Stock crítico (barh) — misma lógica; WHERE + ORDER BY indexables
# ============================================================
def create_stock_critico(engine=None, limit=10):
    engine = engine or get_engine()
    with engine.connect() as con:
        q = text("""
            SELECT
              nombre,
              COALESCE(stock_actual, 0)  AS stock_actual,
              COALESCE(stock_minimo, 0)  AS stock_minimo,
              GREATEST(COALESCE(stock_minimo,0) - COALESCE(stock_actual,0), 0) AS deficit
            FROM public.productos
            WHERE COALESCE(stock_actual,0) <= COALESCE(stock_minimo,0)
            ORDER BY deficit DESC, nombre ASC
            LIMIT :limit
        """)
        df = pd.read_sql(q, con, params={'limit': int(limit)})

    if df.empty:
        fig, ax = plt.subplots(figsize=(7.2, 3.5))
        ax.text(0.5, 0.5, 'Sin productos en nivel crítico', ha='center', va='center', color=gs.INK_MAIN)
        ax.axis('off')
        return fig

    df['nombre_corto'] = df['nombre'].apply(lambda s: gs.short_label(s, width=28))

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    bars = ax.barh(df['nombre_corto'], df['deficit'], color=gs.P_DANGER)

    ax.invert_yaxis()
    ax.set_xlabel('Unidades faltantes')
    gs.pro_axes(ax, title='Stock crítico (déficit vs mínimo)')
    ax.xaxis.set_major_formatter(FuncFormatter(gs.fmt_thousands_smart))

    maxv = float(df['deficit'].max())
    offset = (maxv * 0.02) if maxv > 0 else 0.05
    if maxv <= 0:
        ax.set_xlim(0, 1)

    for b in bars:
        w = b.get_width()
        ax.text(w + offset, b.get_y() + b.get_height()/2,
                gs.fmt_thousands_smart(w),
                va='center', ha='left', fontsize=10, color=gs.INK_MAIN)

    gs.tight_fig(fig)
    return fig

# ============================================================
# 6) Materiales más usados en el mes (barh) — desde obras
# ============================================================
def create_top_materiales_mes(engine=None, dias=30, limit=10):
    """
    TOP-N materiales más usados (consumidos) en obras durante los últimos `dias`.
    Se calcula desde gastos vinculados a obras (no ventas).
    """
    engine = engine or get_engine()
    desde = (datetime.today() - timedelta(days=dias)).date()

    with engine.connect() as con:
        q = text("""
            SELECT
              p.id_producto,
              COALESCE(NULLIF(TRIM(p.nombre), ''), 'Sin nombre') AS material,
              SUM(COALESCE(g.cantidad,0))::numeric AS total_unidades
            FROM public.gastos g
            JOIN public.productos p ON p.id_producto = g.id_producto
            JOIN public.trabajos  t ON t.id         = g.trabajo_id
            JOIN public.obras     o ON o.id_obra    = t.obra_id
            WHERE g.fecha >= :desde
              AND g.trabajo_id IS NOT NULL
              AND (g.tipo ILIKE 'material%' OR g.id_producto IS NOT NULL)
            GROUP BY p.id_producto, material
            HAVING SUM(COALESCE(g.cantidad,0)) > 0
            ORDER BY total_unidades DESC
            LIMIT :limit
        """)
        df = pd.read_sql(q, con, params={'desde': desde, 'limit': int(limit)})

    if df.empty:
        fig, ax = plt.subplots(figsize=(7.2, 3.5))
        ax.text(0.5, 0.5, 'Sin consumos recientes de materiales en obras', ha='center', va='center', color=gs.INK_MAIN)
        ax.axis('off')
        return fig

    df['material_corto'] = df['material'].apply(lambda s: gs.short_label(s, width=28))

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    bars = ax.barh(df['material_corto'], df['total_unidades'], color=gs.P_PRIMARY, edgecolor='none')

    ax.invert_yaxis()
    ax.set_xlabel('Unidades consumidas')
    gs.pro_axes(ax, title=f'Materiales más usados en obras (últimos {dias} días)')
    ax.xaxis.set_major_formatter(FuncFormatter(gs.fmt_thousands))

    maxv = float(df['total_unidades'].max())
    offset = maxv * 0.02 if maxv > 0 else 0.05
    for b in bars:
        w = b.get_width()
        ax.text(w + offset, b.get_y() + b.get_height()/2,
                gs.fmt_thousands(w),
                va='center', ha='left', fontsize=9, color=gs.INK_MAIN)

    gs.tight_fig(fig)
    return fig
