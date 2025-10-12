# graficos_dashboard.py
# ------------------------------------------------------------
# Funciones que consultan la BD y construyen figuras Matplotlib
# usando el kit de estilos/estructura de graficos_style.py
# ------------------------------------------------------------

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# === Tema y helpers centralizados (Pro Kit/Willow) ===
from graficos.graficos_style import (
    # Tema global
    apply_rodler_chart_style,
    # Tokens
    P_PRIMARY, P_SECONDARY, P_DANGER, INK_MAIN, BG, GRID_COLOR,
    # Formateadores & helpers
    fmt_thousands, fmt_thousands_smart, short_label, tight_fig, maybe_scale_to_millions,
    # Estructura PRO + clones del mock
    pro_axes, line_smooth,
    draw_overall_sales_header, legend_chips, bars_grouped_willow, donut_willow
)

# Aplica el estilo global una sola vez al importar el módulo
apply_rodler_chart_style()


# Conexión a PostgreSQL
def get_engine():
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if url:
        # Si usas Supabase y no trae sslmode, forzarlo
        if "sslmode=" not in url:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}sslmode=require"
        return create_engine(url)

    user = os.getenv("PGUSER", "")
    pwd = os.getenv("PGPASSWORD", "")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    db   = os.getenv("PGDATABASE", "")
    return create_engine(f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}")



# 1) Ventas vs Compras mensuales
def create_ventas_vs_compras_mensuales(engine=None, meses=12):
    engine = engine or get_engine()
    with engine.connect() as con:
        qv = text("""
            SELECT DATE_TRUNC('month', fecha_venta)::date AS periodo,
                   COALESCE(SUM(total_venta),0) AS total
            FROM ventas
            GROUP BY 1
            ORDER BY 1
        """)
        qc = text("""
            SELECT DATE_TRUNC('month', fecha)::date AS periodo,
                   COALESCE(SUM(total_compra),0) AS total
            FROM compras
            GROUP BY 1
            ORDER BY 1
        """)
        dfv = pd.read_sql(qv, con)
        dfc = pd.read_sql(qc, con)

    end = datetime.today().replace(day=1)
    months = [(end - pd.DateOffset(months=i)).date() for i in range(meses - 1, -1, -1)]
    idx = pd.to_datetime(pd.Series(months))

    sv = dfv.set_index(pd.to_datetime(dfv['periodo']))['total'].reindex(idx, fill_value=0)
    sc = dfc.set_index(pd.to_datetime(dfc['periodo']))['total'].reindex(idx, fill_value=0)

    # Escalar si son montos grandes
    sv_scaled, suf = maybe_scale_to_millions(sv)
    sc_scaled, _   = maybe_scale_to_millions(sc)

    labels = [d.strftime('%b').title() for d in idx]  # Jan, Feb, ...

    fig, ax = plt.subplots(figsize=(8.2, 4.4))

    # Encabezado doble como el mock
    total_order = int(sv.sum())
    draw_overall_sales_header(ax, f"{total_order:,.0f}".replace(",", "."))

    # Barras delgadas estilo mock + grilla sólo horizontal + chips
    bars_grouped_willow(
        ax,
        categories=labels,
        series=[sv_scaled, sc_scaled],
        labels=["Account Reached", "Account Engaged"],
        colors=[P_PRIMARY, P_SECONDARY],
        show_values=False
    )
    legend_chips(ax, [("Account Reached", P_PRIMARY), ("Account Engaged", P_SECONDARY)],
                 loc="upper left", anchor=(0, 1.03), fontsize=10)

    tight_fig(fig)
    return fig



# 2) Gastos mensuales (línea suave estilo Pro)
def create_gastos_mensuales(engine=None, meses=12):
    engine = engine or get_engine()
    with engine.connect() as con:
        q = text("""
            SELECT DATE_TRUNC('month', fecha)::date AS periodo,
                   COALESCE(SUM(costo_total),0) AS total
            FROM gastos
            GROUP BY 1
            ORDER BY 1
        """)
        df = pd.read_sql(q, con)

    end = datetime.today().replace(day=1)
    months = [(end - pd.DateOffset(months=i)).date() for i in range(meses - 1, -1, -1)]
    idx = pd.to_datetime(pd.Series(months))

    s = df.set_index(pd.to_datetime(df['periodo']))['total'].reindex(idx, fill_value=0)
    s_scaled, suf = maybe_scale_to_millions(s)
    xlabels = [d.strftime('%b').title() for d in idx]

    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    line_smooth(ax, xlabels, s_scaled, title=f"Gastos Mensuales{suf}", area=True)
    tight_fig(fig)
    return fig


# ============================================================
# 3) Presupuesto vs Gasto por obra (barras agrupadas estilo mock)
# ============================================================
def create_presupuesto_vs_gasto_por_obra(engine=None, top_n=10):
    engine = engine or get_engine()
    with engine.connect() as con:
        q = text("""
            SELECT o.nombre,
                   COALESCE(o.presupuesto_total, 0) AS presupuesto,
                   COALESCE(SUM(t.costo_total), 0) AS gasto
            FROM obras o
            LEFT JOIN trabajos t ON t.obra_id = o.id_obra
            GROUP BY o.id_obra, o.nombre, o.presupuesto_total
            ORDER BY o.created_at DESC
        """)
        df = pd.read_sql(q, con)

    if df.empty:
        fig, ax = plt.subplots(figsize=(7.6, 4.2))
        ax.text(0.5, 0.5, 'Sin datos de obras', ha='center', va='center', color=INK_MAIN)
        ax.axis('off')
        return fig

    df = df.sort_values('presupuesto', ascending=False).head(top_n).copy()
    cats = [short_label(s, 28) for s in df['nombre']]

    pres_scaled, suf = maybe_scale_to_millions(df['presupuesto'])
    gast_scaled, _   = maybe_scale_to_millions(df['gasto'])

    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    bars_grouped_willow(
        ax,
        categories=cats,
        series=[pres_scaled, gast_scaled],
        labels=["Presupuesto", "Gasto"],
        colors=[P_SECONDARY, P_PRIMARY],
        show_values=False
    )
    # % ejecutado sobre la barra de Gasto (segunda serie: offset +w/2)
    x = np.arange(len(cats))
    n = 2
    w = 0.6 / n  # igual que en bars_grouped_willow
    x_gasto = x + (w/2)
    with pd.option_context('mode.use_inf_as_na', True):
        pct = (df['gasto'] / df['presupuesto']).fillna(0) * 100
    for i, v in enumerate(gast_scaled):
        ax.text(x_gasto[i], v, f"{pct.iat[i]:.1f}%",
                ha='left', va='bottom', fontsize=10, color=INK_MAIN)

    # Título fuera (en cards podés poner QLabel). Si querés sobre el chart:
    pro_axes(ax, title=f"Presupuesto vs Gasto por Obra{suf}")
    tight_fig(fig)
    return fig


# ============================================================
# 4) Distribución de gastos por tipo (donut estilo mock)
# ============================================================
def create_distribucion_gastos_por_tipo(engine=None, top_cats=6):
    engine = engine or get_engine()
    with engine.connect() as con:
        q = text("""
            SELECT COALESCE(NULLIF(TRIM(tipo), ''), 'Sin tipo') AS tipo,
                   SUM(COALESCE(costo_total, 0)) AS total
            FROM gastos
            GROUP BY 1
            HAVING SUM(COALESCE(costo_total,0)) > 0
            ORDER BY 2 DESC
        """)
        df = pd.read_sql(q, con)

    if df.empty:
        fig, ax = plt.subplots(figsize=(6.8, 4.0))
        ax.text(0.5, 0.5, 'Sin datos de gastos', ha='center', va='center', color=INK_MAIN)
        ax.axis('off')
        return fig

    df = df.sort_values('total', ascending=False)
    if len(df) > top_cats:
        top = df.head(top_cats)
        otros = pd.DataFrame({'tipo': ['Otros'], 'total': [df['total'][top_cats:].sum()]})
        df = pd.concat([top, otros], ignore_index=True)

    # % central: mayor contribución (o ajusta a la métrica que prefieras)
    pct = int(round(100 * df['total'].max() / df['total'].sum()))

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    donut_willow(ax, f"{pct}%", df['total'], ["Order", "Revenue", "Visitor"])
    # Si querés usar tus nombres reales en leyenda, pásalos como labels arriba.

    tight_fig(fig)
    return fig


# ============================================================
# 5) Stock crítico (barh con pro_axes)
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
            FROM productos
            WHERE COALESCE(stock_actual,0) <= COALESCE(stock_minimo,0)
            ORDER BY deficit DESC, nombre ASC
            LIMIT :limit
        """)
        df = pd.read_sql(q, con, params={'limit': limit})

    if df.empty:
        fig, ax = plt.subplots(figsize=(7.2, 3.5))
        ax.text(0.5, 0.5, 'Sin productos en nivel crítico', ha='center', va='center', color=INK_MAIN)
        ax.axis('off')
        return fig

    # nombres cortos para las etiquetas
    df['nombre_corto'] = df['nombre'].apply(lambda s: short_label(s, width=28))

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    bars = ax.barh(df['nombre_corto'], df['deficit'], color=P_DANGER)

    ax.invert_yaxis()
    ax.set_xlabel('Unidades faltantes')
    pro_axes(ax, title='Stock Crítico (déficit vs mínimo)')
    ax.xaxis.set_major_formatter(FuncFormatter(fmt_thousands_smart))

    maxv = float(df['deficit'].max())
    # Si todos están exactamente en el mínimo (déficit 0), igual dejamos escala y etiquetas visibles
    if maxv <= 0:
        ax.set_xlim(0, 1)
        offset = 0.05
    else:
        offset = maxv * 0.02

    for b in bars:
        w = b.get_width()
        ax.text(w + offset,
                b.get_y() + b.get_height()/2,
                fmt_thousands_smart(w),
                va='center', ha='left', fontsize=10, color=INK_MAIN)

    tight_fig(fig)
    return fig



# ============================================================
# 6) Materiales más usados en el mes (barh con pro_axes)
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
            FROM gastos g
            JOIN productos p ON p.id_producto = g.id_producto
            WHERE g.fecha >= :desde
              AND (g.tipo ILIKE 'material%' OR g.id_producto IS NOT NULL)
            GROUP BY p.id_producto, material
            HAVING SUM(COALESCE(g.cantidad,0)) > 0
            ORDER BY total_unidades DESC
            LIMIT :limit
        """)
        df = pd.read_sql(q, con, params={'desde': desde, 'limit': limit})

    if df.empty:
        fig, ax = plt.subplots(figsize=(7.2, 3.5))
        ax.text(0.5, 0.5, 'Sin consumos recientes de materiales', ha='center', va='center', color=INK_MAIN)
        ax.axis('off')
        return fig

    df['material_corto'] = df['material'].apply(lambda s: short_label(s, width=28))

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    bars = ax.barh(df['material_corto'], df['total_unidades'], color=P_PRIMARY)

    ax.invert_yaxis()
    ax.set_xlabel('Unidades consumidas')
    pro_axes(ax, title=f'Materiales más usados (últimos {dias} días)')
    ax.xaxis.set_major_formatter(FuncFormatter(fmt_thousands))

    maxv = df['total_unidades'].max()
    for b in bars:
        w = b.get_width()
        ax.text(w + maxv * 0.02,
                b.get_y() + b.get_height()/2,
                fmt_thousands(w),
                va='center', ha='left', fontsize=9, color=INK_MAIN)

    tight_fig(fig)
    return fig
