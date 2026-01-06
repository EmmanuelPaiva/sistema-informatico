# -*- coding: utf-8 -*-
# graficos_dashboard.py — estable, sin cortes y sin warnings de layout

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
from db.conexion import DATABASE_URL
# --- Meses abreviados (ES) ---
_SP_MONTHS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# --- Canonicalización de categorías ---
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

def get_engine():
    """
    Devuelve un engine de SQLAlchemy usando la misma DATABASE_URL
    que usa todo el sistema (config.ini + sslmode=require).
    """
    return create_engine(DATABASE_URL, pool_pre_ping=True)

# =========================
# Helpers
# =========================
def _month_floor(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def _months_back_start(meses: int) -> datetime:
    end = _month_floor(datetime.today())
    start = end - relativedelta(months=meses - 1)
    return _month_floor(start)

def _read_df(con, sql_mv, sql_base, params=None):
    try:
        return pd.read_sql(text(sql_mv), con, params=params)
    except ProgrammingError:
        return pd.read_sql(text(sql_base), con, params=params)

def _dpi():
    # Usa gs.BASE_DPI si existe; si no, deja que Matplotlib decida
    return getattr(gs, "BASE_DPI", None)

# ============================================================
# 1) Ventas vs Compras mensuales
# ============================================================
def create_ventas_vs_compras_mensuales(engine=None, meses=12):
    engine = engine or get_engine()
    desde = _months_back_start(meses).date()

    with engine.connect() as con:
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
            GROUP BY 1 ORDER BY 1
        """
        dfv = _read_df(con, qv_mv, qv_base, params={"desde": desde})

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
            GROUP BY 1 ORDER BY 1
        """
        dfc = _read_df(con, qc_mv, qc_base, params={"desde": desde})

    end = _month_floor(datetime.today())
    months = [(end - pd.DateOffset(months=i)).date() for i in range(meses - 1, -1, -1)]
    idx = pd.to_datetime(pd.Series(months))

    sv = dfv.set_index(pd.to_datetime(dfv['periodo']))['total'].reindex(idx, fill_value=0)
    sc = dfc.set_index(pd.to_datetime(dfc['periodo']))['total'].reindex(idx, fill_value=0)

    sv_scaled, suf = gs.maybe_scale_to_millions(sv)
    sc_scaled, _   = gs.maybe_scale_to_millions(sc)
    labels = [_SP_MONTHS[d.month - 1] for d in idx]

    fig, ax = plt.subplots(figsize=(8.2, 4.4), dpi=_dpi())
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
        anchor=(0.02, 0.98),
        fontsize=10
    )

    # Márgenes propios seguros (evitan cortes)
    gs.disable_layout_engine(fig)
    fig._rodler_custom_margins = True
    fig.subplots_adjust(left=0.07, right=0.995, top=0.90, bottom=0.28)
    gs.tight_fig(fig)
    return fig

# ============================================================
# 2) Gastos mensuales (línea)
# ============================================================
def create_gastos_mensuales(engine=None, meses=12):
    engine = engine or get_engine()
    desde = _months_back_start(meses).date()

    with engine.connect() as con:
        q_mv = """
            SELECT periodo, total FROM public.mv_gastos_mensual
            WHERE periodo >= :desde ORDER BY periodo
        """
        q_base = """
            SELECT DATE_TRUNC('month', fecha)::date AS periodo,
                   COALESCE(SUM(costo_total),0) AS total
            FROM public.gastos
            WHERE fecha >= :desde
            GROUP BY 1 ORDER BY 1
        """
        df = _read_df(con, q_mv, q_base, params={"desde": desde})

    end = _month_floor(datetime.today())
    months = [(end - pd.DateOffset(months=i)).date() for i in range(meses - 1, -1, -1)]
    idx = pd.to_datetime(pd.Series(months))

    s = df.set_index(pd.to_datetime(df['periodo']))['total'].reindex(idx, fill_value=0)
    s_scaled, suf = gs.maybe_scale_to_millions(s)
    xlabels = [_SP_MONTHS[d.month - 1] for d in idx]

    fig, ax = plt.subplots(figsize=(8.4, 4.2), dpi=_dpi())
    gs.line_smooth(ax, xlabels, s_scaled, title=f"Gastos mensuales{suf}", area=True)

    gs.disable_layout_engine(fig)
    fig._rodler_custom_margins = True
    fig.subplots_adjust(left=0.07, right=0.995, top=0.92, bottom=0.28)
    gs.tight_fig(fig)
    return fig

# ============================================================
# 3) Presupuesto vs Gasto por obra (barras agrupadas)
# ============================================================
def create_presupuesto_vs_gasto_por_obra(engine=None, top_n=10):
    engine = engine or get_engine()
    with engine.connect() as con:
        q = text("""
            WITH gasto_por_obra AS (
                SELECT t.obra_id, COALESCE(SUM(t.costo_total), 0) AS gasto
                FROM public.trabajos t
                GROUP BY t.obra_id
            )
            SELECT o.id_obra, o.nombre,
                   COALESCE(o.presupuesto_total, 0) AS presupuesto,
                   COALESCE(g.gasto, 0) AS gasto
            FROM public.obras o
            LEFT JOIN gasto_por_obra g ON g.obra_id = o.id_obra
            ORDER BY o.presupuesto_total DESC NULLS LAST
            LIMIT :top_n
        """)
        df = pd.read_sql(q, con, params={"top_n": int(top_n)})

    if df.empty:
        fig, ax = plt.subplots(figsize=(7.6, 4.2), dpi=_dpi())
        ax.text(0.5, 0.5, "Sin datos de obras", ha="center", va="center", color=gs.INK_MAIN)
        ax.axis("off")
        return fig

    cats = [gs.short_label(s, 28) for s in df["nombre"]]
    pres_scaled, suf = gs.maybe_scale_to_millions(df["presupuesto"])
    gast_scaled, _   = gs.maybe_scale_to_millions(df["gasto"])

    fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=_dpi())

    x = np.arange(len(cats))
    bw, gap = 0.36, 0.06
    pres_x = x - (bw/2 + gap/2)
    gast_x = x + (bw/2 + gap/2)

    ax.bar(pres_x, pres_scaled, width=bw, label="Presupuesto",
           color=gs.P_SECONDARY, edgecolor="white", linewidth=0.6)
    b2 = ax.bar(gast_x, gast_scaled, width=bw, label="Gasto",
                color=gs.P_PRIMARY, edgecolor="white", linewidth=0.6)

    ax.set_xticks(x, cats)
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
        if h > 0:
            ax.text(rect.get_x() + rect.get_width()/2, h + yoff, f"{p:.1f}%",
                    ha="center", va="bottom", fontsize=9, color=gs.INK_MAIN)

    ax.legend(frameon=False, fontsize=9)
    ax.set_ylabel(f"Monto{suf}", fontsize=10)
    gs.pro_axes(ax, title=f"Presupuesto vs Gasto por obra{suf}")

    gs.disable_layout_engine(fig)
    fig._rodler_custom_margins = True
    fig.subplots_adjust(left=0.07, right=0.995, top=0.92, bottom=0.28)
    gs.tight_fig(fig)
    return fig

# ============================================================
# 4) Distribución de gastos por tipo (donut a la derecha)
# ============================================================
def create_distribucion_gastos_por_tipo(engine=None, max_cats: int = 5, min_pct_otro: float = 0.03):
    from matplotlib import gridspec
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
        fig, ax = plt.subplots(figsize=(9.8, 5.2), dpi=_dpi())
        gs.disable_layout_engine(fig)
        ax.text(0.5, 0.5, 'Sin datos de gastos', ha='center', va='center', color=gs.INK_MAIN)
        ax.axis('off')
        fig._rodler_custom_margins = True
        fig.subplots_adjust(left=0.06, right=0.99, top=0.94, bottom=0.12)
        gs.tight_fig(fig)
        return fig

    df_raw["tipo"] = df_raw["tipo"].apply(_canon_label)
    df = df_raw.groupby("tipo", as_index=False)["total"].sum()
    total = float(df["total"].sum())
    if total <= 0:
        fig, ax = plt.subplots(figsize=(9.8, 5.2), dpi=_dpi())
        gs.disable_layout_engine(fig)
        ax.text(0.5, 0.5, 'Sin datos de gastos', ha='center', va='center', color=gs.INK_MAIN)
        ax.axis('off')
        fig._rodler_custom_margins = True
        fig.subplots_adjust(left=0.06, right=0.99, top=0.94, bottom=0.12)
        gs.tight_fig(fig)
        return fig

    # Compactación a top + "Otros"
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

    vals = df["total"].to_numpy(dtype=float)
    labels = df["tipo"].tolist()
    total_final = float(vals.sum())
    pct = (vals / total_final) * 100.0

    base_colors = [gs.P_PRIMARY, gs.P_SECONDARY, gs.P_ACCENT, gs.P_WARN, gs.P_DANGER, gs.INK_MUTE]
    colors = (base_colors * ((len(vals) // len(base_colors)) + 1))[:len(vals)]

    # --- layout: [leyenda | donut] ---
    fig = plt.figure(figsize=(9.8, 5.2), dpi=_dpi())
    gs.disable_layout_engine(fig)
    gspe = gridspec.GridSpec(nrows=1, ncols=2, width_ratios=[0.58, 0.42], figure=fig)
    ax_left  = fig.add_subplot(gspe[0, 0])   # leyenda
    ax_right = fig.add_subplot(gspe[0, 1])   # donut

    # Donut a la DERECHA
    ax_right.pie(
        vals,
        labels=None,
        startangle=90,
        colors=colors[:len(vals)],
        wedgeprops=dict(width=0.44, edgecolor="white"),
        autopct=None,
        normalize=True
    )
    ax_right.add_artist(plt.Circle((0, 0), 0.60, fc=gs.BG))
    ax_right.set_aspect("equal")
    ax_right.margins(0.04)

    # Número arriba (ligeramente más abajo para no cortarse)
    ax_right.text(
        0.5, 1.04,
        f"{int(round(total_final)):,}".replace(",", ".") + " Gs",
        transform=ax_right.transAxes, ha="center", va="bottom",
        fontsize=16, color=gs.INK_MAIN, fontweight="bold"
    )
    ax_right._rodler_preserve_axes_text = True

    # Leyenda a la IZQUIERDA (texto + “bullet” de color)
    ax_left.set_axis_off()
    ax_left._rodler_preserve_axes_text = True

    legend_lines = [
        f"{gs.short_label(lbl, 28)} · {p:.1f}% · {int(round(v)):,}".replace(",", ".") + " Gs"
        for lbl, p, v in zip(labels, pct, vals)
    ]

    y0, dy = 0.96, 0.09
    for i, (c, txt) in enumerate(zip(colors[:len(legend_lines)], legend_lines)):
        y = y0 - i * dy
        ax_left.add_patch(plt.Rectangle((0.02, y - 0.02), 0.035, 0.035,
                                        transform=ax_left.transAxes, color=c, clip_on=False))
        ax_left.text(0.065, y, txt, transform=ax_left.transAxes,
                     ha="left", va="center", fontsize=10, color=gs.INK_MAIN)

    gs.disable_layout_engine(fig)
    fig._rodler_custom_margins = True
    fig.subplots_adjust(left=0.05, right=0.995, top=0.98, bottom=0.12, wspace=0.02)
    gs.tight_fig(fig)
    return fig

# ============================================================
# 5) Stock crítico (barh)
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
        fig, ax = plt.subplots(figsize=(7.2, 3.5), dpi=_dpi())
        ax.text(0.5, 0.5, 'Sin productos en nivel crítico', ha='center', va='center', color=gs.INK_MAIN)
        ax.axis('off')
        return fig

    df['nombre_corto'] = df['nombre'].apply(lambda s: gs.short_label(s, width=28))

    fig, ax = plt.subplots(figsize=(8.8, 4.8), dpi=_dpi())
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

    gs.disable_layout_engine(fig)
    fig._rodler_custom_margins = True
    fig.subplots_adjust(left=0.14, right=0.98, top=0.92, bottom=0.20)
    gs.tight_fig(fig)
    return fig

# ============================================================
# 6) Materiales más usados en el mes (barh)
# ============================================================
def create_top_materiales_mes(engine=None, dias=30, limit=10):
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
        fig, ax = plt.subplots(figsize=(7.2, 3.5), dpi=_dpi())
        ax.text(0.5, 0.5, 'Sin consumos recientes de materiales en obras', ha='center', va='center', color=gs.INK_MAIN)
        ax.axis('off')
        return fig

    df['material_corto'] = df['material'].apply(lambda s: gs.short_label(s, width=28))

    fig, ax = plt.subplots(figsize=(7.8, 4.6), dpi=_dpi())
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

    gs.disable_layout_engine(fig)
    fig._rodler_custom_margins = True
    fig.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.20)
    gs.tight_fig(fig)
    return fig
