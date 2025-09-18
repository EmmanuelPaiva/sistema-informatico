# graficos_dashboard.py
import os
from datetime import datetime, timedelta

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import textwrap

# =========================
# Estilo Rodler (Matplotlib)
# =========================
PRIMARY = '#4fc3f7'
PRIMARY_SOFT = '#90caf9'
DANGER = '#ef5350'
TEXT = '#0d1b2a'
GRID = '#dfe7f5'
BG = '#ffffff'

def apply_rodler_style():
    try:
        import seaborn as sns
        sns.set_theme(style="whitegrid")
        sns.set_context("notebook")  # más chico que "talk"
    except Exception:
        pass

    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Segoe UI', 'Arial', 'DejaVu Sans'],
        'figure.facecolor': BG,
        'axes.facecolor': BG,
        'axes.edgecolor': GRID,
        'axes.grid': True,
        'grid.color': GRID,
        'grid.linestyle': '--',
        'grid.alpha': 0.6,
        'axes.axisbelow': True,
        # tipografías AJUSTADAS (más chicas)
        'axes.titlesize': 13,       # antes 16
        'axes.titleweight': 'bold',
        'axes.labelsize': 11,       # antes 13
        'xtick.labelsize': 10,      # antes 12
        'ytick.labelsize': 10,      # antes 12
        'legend.fontsize': 10,      # antes 12
        'figure.autolayout': False,
    })


apply_rodler_style()

# =========================
# Conexión a PostgreSQL
# =========================
def get_engine():
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if url:
        return create_engine(url)

    user = os.getenv("PGUSER", "")
    pwd = os.getenv("PGPASSWORD", "")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    db   = os.getenv("PGDATABASE", "")
    return create_engine(f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}")

# =========================
# Helpers visuales
# =========================
def _fmt_miles(x, _pos=None):
    # 12 345 -> "12.345" (miles con punto)
    return f"{x:,.0f}".replace(",", ".")

def _short(texto, width=22):
    # acorta etiquetas muy largas con "…"
    return textwrap.shorten(str(texto), width=width, placeholder="…")

def _beautify_axes(ax, y_as_money=False):
    # Límites & formato ejes
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, prune=None))
    if y_as_money:
        ax.yaxis.set_major_formatter(FuncFormatter(_fmt_miles))
    ax.tick_params(axis='x', rotation=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def _tight(fig):
    try:
        fig.tight_layout(pad=0.8)
    except Exception:
        pass
def _fmt_miles_smart(x, _pos=None):
    # Si el valor es chico, mostrar decimales; si es grande, miles sin decimales
    ax_abs = abs(x)
    if ax_abs < 10:
        s = f"{x:,.2f}"
    elif ax_abs < 1000:
        s = f"{x:,.1f}"
    else:
        s = f"{x:,.0f}"
    return s.replace(",", ".")

def _maybe_scale_to_millions(series):
    """
    Si los montos son grandes, escala a millones y devuelve (serie_escalada, sufijo_label).
    Umbral heurístico: max >= 10 millones.
    """
    m = series.max() if len(series) else 0
    if m >= 10_000_000:
        return series / 1_000_000.0, " (millones)"
    return series, ""

def _y_money(ax, smart=False):
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, prune=None))
    ax.yaxis.set_major_formatter(FuncFormatter(_fmt_miles_smart if smart else _fmt_miles))

# =========================
# 1) Ventas vs Compras mensuales (barras agrupadas)
# =========================
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
    months = [(end - pd.DateOffset(months=i)).date() for i in range(meses-1, -1, -1)]
    idx = pd.to_datetime(pd.Series(months))

    sv = dfv.set_index(pd.to_datetime(dfv['periodo']))['total'].reindex(idx, fill_value=0)
    sc = dfc.set_index(pd.to_datetime(dfc['periodo']))['total'].reindex(idx, fill_value=0)

    labels = [d.strftime('%Y-%m') for d in idx]
    x = range(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(7.6, 4.1), constrained_layout=False)
    ax.bar([i - width/2 for i in x], sv.values, width=width, label='Ventas', color=PRIMARY)
    ax.bar([i + width/2 for i in x], sc.values, width=width, label='Compras', color=PRIMARY_SOFT)

    sv_scaled, suf = _maybe_scale_to_millions(sv)
    sc_scaled, _   = _maybe_scale_to_millions(sc)  # usa mismo umbral
    ...
    ax.bar([i - width/2 for i in x], sv_scaled.values, width=width, label='Ventas', color=PRIMARY)
    ax.bar([i + width/2 for i in x], sc_scaled.values, width=width, label='Compras', color=PRIMARY_SOFT)
    ax.set_ylabel('Monto total' + suf)
    _y_money(ax, smart=True)

    ax.set_title('Ventas vs Compras (mensual)')
    ax.set_xlabel('Mes')
    ax.set_ylabel('Monto total')
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=30, ha='right')
    ax.yaxis.set_major_formatter(FuncFormatter(_fmt_miles))
    ax.legend(loc='upper left', ncols=2, frameon=False)
    _beautify_axes(ax, y_as_money=True)
    _tight(fig)
    return fig

# =========================
# 2) Gastos mensuales (línea)
# =========================
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
    months = [(end - pd.DateOffset(months=i)).date() for i in range(meses-1, -1, -1)]
    idx = pd.to_datetime(pd.Series(months))
    s = df.set_index(pd.to_datetime(df['periodo']))['total'].reindex(idx, fill_value=0)

    s_scaled, suf = _maybe_scale_to_millions(s)
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.plot([d.strftime('%Y-%m') for d in idx], s_scaled.values, marker='o', linewidth=2.5, color=PRIMARY)
    ax.set_ylabel('Total gastado' + suf)
    _y_money(ax, smart=True)
    return fig

# =========================
# 3) Presupuesto vs Gasto por obra (barras agrupadas)
# =========================
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

        df = df.sort_values('presupuesto', ascending=False).head(top_n).copy()
        df['nombre_corto'] = df['nombre'].apply(_short)
        
        # Escalar a millones si hace falta
        pres_scaled, suf = _maybe_scale_to_millions(df['presupuesto'])
        gast_scaled,  _  = _maybe_scale_to_millions(df['gasto'])
        
        x = range(len(df))
        width = 0.38
        fig, ax = plt.subplots(figsize=(9.0, 5.0))
        ax.bar([i - width/2 for i in x], pres_scaled, width=width, label='Presupuesto', color=PRIMARY_SOFT)
        ax.bar([i + width/2 for i in x], gast_scaled, width=width, label='Gasto',       color=PRIMARY)
        
        ax.set_title('Presupuesto vs Gasto por Obra')
        ax.set_xlabel('Obra')
        ax.set_ylabel('Monto' + suf)
        ax.set_xticks(list(x))
        ax.set_xticklabels(df['nombre_corto'], rotation=15, ha='right')
        _y_money(ax, smart=True)
        ax.legend(loc='upper left', ncols=2, frameon=False)
        
        # % ejecutado sobre el bar de Gasto para ayudar lectura
        pct = (df['gasto'] / df['presupuesto']).replace([pd.NA, pd.NaT, float('inf')], 0).fillna(0) * 100
        for i, v in enumerate(gast_scaled):
            ax.text(i + width/2, v, f"{pct.iat[i]:.1f}%", ha='left', va='bottom', fontsize=11, color=TEXT)
        
        _beautify_axes(ax, y_as_money=True)
        _tight(fig)
        return fig

# =========================
# 4) Distribución de gastos por tipo (donut limpio + leyenda afuera)
# =========================
def create_distribucion_gastos_por_tipo(engine=None):
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
        ax.text(0.5, 0.5, 'Sin datos de gastos', ha='center', va='center', fontsize=12, color=TEXT)
        ax.axis('off')
        return fig

    # Para evitar saturación: top 6 categorías + "Otros"
    df = df.sort_values('total', ascending=False)
    if len(df) > 6:
        top = df.head(6)
        otros = pd.DataFrame({'tipo': ['Otros'], 'total': [df['total'][6:].sum()]})
        df = pd.concat([top, otros], ignore_index=True)

    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    wedges, _texts, autotexts = ax.pie(
        df['total'],
        labels=None,  # usamos leyenda para claridad
        autopct=lambda pct: f'{pct:.1f}%',
        startangle=90,
        pctdistance=0.78,
        textprops={'color': TEXT, 'fontsize': 9},
        wedgeprops={'linewidth': 1, 'edgecolor': GRID}
    )
    # Donut
    centre_circle = plt.Circle((0, 0), 0.58, fc=BG)
    ax.add_artist(centre_circle)

    ax.set_title('Distribución de Gastos por Tipo')
    ax.axis('equal')

    # Leyenda a la derecha
    ax.legend(wedges, [f"{_short(t)}" for t in df['tipo']],
              title=None, loc='center left', bbox_to_anchor=(1.02, 0.5),
              frameon=False)
    _tight(fig)
    return fig

# =========================
# 5) Stock crítico (barh, números legibles)
# =========================
def create_stock_critico(engine=None, limit=10):
    engine = engine or get_engine()
    with engine.connect() as con:
        q = text("""
            SELECT nombre, stock_actual, stock_minimo,
                   (stock_minimo - stock_actual) AS deficit
            FROM productos
            WHERE stock_actual < stock_minimo      -- ESTRICTO: excluye déficit 0
            ORDER BY deficit DESC, nombre ASC
            LIMIT :limit
        """)
        df = pd.read_sql(q, con, params={'limit': limit})

    if df.empty:
        fig, ax = plt.subplots(figsize=(7.2, 3.5))
        ax.text(0.5, 0.5, 'Sin productos en nivel crítico', ha='center', va='center', fontsize=12, color=TEXT)
        ax.axis('off')
        return fig
    df = df[df['deficit'] > 0]  
    df['nombre_corto'] = df['nombre'].apply(_short, width=28)

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    bars = ax.barh(df['nombre_corto'], df['deficit'], color=DANGER)
    ax.set_title('Stock Crítico (déficit vs mínimo)')
    ax.set_xlabel('Unidades faltantes')
    ax.set_ylabel('Producto')
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(FuncFormatter(_fmt_miles_smart))  # <<< smart
    # etiquetas al final de cada barra
    for b in bars:
        w = b.get_width()
        ax.text(w + max(df['deficit']) * 0.02, b.get_y() + b.get_height()/2,
        _fmt_miles_smart(w), va='center', ha='left', fontsize=11, color=TEXT)
    _beautify_axes(ax, y_as_money=False)
    _tight(fig)
    return fig

# =========================
# 6) Materiales más usados en el mes (barh)
# =========================
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
        ax.text(0.5, 0.5, 'Sin consumos recientes de materiales', ha='center', va='center', fontsize=12, color=TEXT)
        ax.axis('off')
        return fig

    df['material_corto'] = df['material'].apply(_short, width=28)

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    bars = ax.barh(df['material_corto'], df['total_unidades'], color=PRIMARY)
    ax.set_title(f'Materiales más usados (últimos {dias} días)')
    ax.set_xlabel('Unidades consumidas')
    ax.set_ylabel('Material')
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(FuncFormatter(_fmt_miles))

    for b in bars:
        w = b.get_width()
        ax.text(w + max(df['total_unidades']) * 0.02, b.get_y() + b.get_height()/2,
                _fmt_miles(w), va='center', ha='left', fontsize=9, color=TEXT)
    _beautify_axes(ax, y_as_money=False)
    _tight(fig)
    return fig
