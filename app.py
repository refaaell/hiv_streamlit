import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard HIV Jawa Barat",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark background */
    .stApp { background-color: #0f1923; }
    section[data-testid="stSidebar"] { background-color: #16213e; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #16213e;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px 20px;
        border-left: 4px solid #e74c3c;
    }
    div[data-testid="metric-container"] label { color: #95a5a6 !important; font-size: 0.78rem !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #fff !important; font-size: 1.8rem !important; font-weight: 800 !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] { color: #2ecc71 !important; }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #96281b, #c0392b, #e74c3c);
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .main-header h1 { color: white; font-size: 1.8rem; margin: 0; }
    .main-header p  { color: rgba(255,255,255,0.8); margin: 4px 0 0; font-size: 0.9rem; }

    /* Section titles */
    .section-title {
        color: #ecf0f1;
        font-size: 1rem;
        font-weight: 600;
        padding: 8px 0;
        border-bottom: 2px solid #e74c3c;
        margin-bottom: 16px;
    }

    h1, h2, h3, p, label { color: #ecf0f1 !important; }
    .stSelectbox label { color: #95a5a6 !important; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('dinkes-od_18510_jumlah_kasus_hiv_berdasarkan_kabupatenkota_v3_data.csv')
    with open('Jabar_By_Kab.geojson') as f:
        geo = json.load(f)
    return df, geo

df, geo = load_data()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🦠 Dashboard HIV")
    st.markdown("**Provinsi Jawa Barat**")
    st.markdown("---")

    year = st.selectbox("📅 Pilih Tahun", sorted(df['tahun'].unique(), reverse=True))
    st.markdown("---")

    all_kab = sorted(df['nama_kabupaten_kota'].unique())
    selected_kab = st.selectbox("📍 Trend Kabupaten/Kota", all_kab,
                                 index=all_kab.index('KOTA BANDUNG'))
    st.markdown("---")
    st.caption("Sumber: Dinas Kesehatan Provinsi Jawa Barat · Open Data Jabar")
    st.caption("Periode: 2022 – 2024")

# ── FILTER DATA ───────────────────────────────────────────────────────────────
df_year = df[df['tahun'] == year].copy()
df_prev = df[df['tahun'] == year - 1].copy() if (year - 1) in df['tahun'].values else None

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
  <h1>🦠 Dashboard Penyebaran HIV — Jawa Barat</h1>
  <p>Visualisasi interaktif kasus HIV per Kabupaten/Kota · Tahun {year}</p>
</div>
""", unsafe_allow_html=True)

# ── METRIC CARDS ─────────────────────────────────────────────────────────────
total      = int(df_year['jumlah_kasus'].sum())
avg        = round(df_year['jumlah_kasus'].mean(), 1)
max_row    = df_year.loc[df_year['jumlah_kasus'].idxmax()]
min_row    = df_year.loc[df_year['jumlah_kasus'].idxmin()]

total_prev = int(df_prev['jumlah_kasus'].sum()) if df_prev is not None else None
delta_total = f"+{total - total_prev:,}" if total_prev else None

c1, c2, c3, c4 = st.columns(4)
c1.metric("📊 Total Kasus", f"{total:,}", delta_total)
c2.metric("📈 Rata-rata / Kab", f"{avg:,.1f}")
c3.metric("🔴 Tertinggi", f"{int(max_row['jumlah_kasus']):,}", max_row['nama_kabupaten_kota'])
c4.metric("🟢 Terendah",  f"{int(min_row['jumlah_kasus']):,}", min_row['nama_kabupaten_kota'])

st.markdown("<br>", unsafe_allow_html=True)

# ── ROW 1: PETA + BAR ────────────────────────────────────────────────────────
col_map, col_bar = st.columns([1.1, 0.9])

with col_map:
    st.markdown(f'<div class="section-title">🗺️ Peta Sebaran Kasus HIV — {year}</div>', unsafe_allow_html=True)

    fig_map = px.choropleth(
        df_year,
        geojson=geo,
        locations='kode_kabupaten_kota',
        featureidkey='properties.ID_KAB',
        color='jumlah_kasus',
        color_continuous_scale=['#fde8e6','#f5b7b1','#ec7063','#e74c3c','#c0392b','#7b241c'],
        hover_name='nama_kabupaten_kota',
        hover_data={'jumlah_kasus': True, 'kode_kabupaten_kota': False},
        labels={'jumlah_kasus': 'Jumlah Kasus'},
        fitbounds='locations',
        basemap_visible=False,
    )
    fig_map.update_geos(
        bgcolor='#0f1923',
        lakecolor='#0f1923',
        landcolor='#1a1a2e',
        showland=True,
        showlakes=False,
        showcoastlines=False,
        showframe=False,
        showocean=False,
    )
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        height=420,
        paper_bgcolor="#387bbe",
        coloraxis_colorbar=dict(
            title=dict(
                text="Kasus",
                font=dict(color="#ecf0f1")
            ),
            tickfont=dict(color="#ecf0f1")
        )
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_bar:
    st.markdown(f'<div class="section-title">📊 Kasus per Kabupaten/Kota — {year}</div>', unsafe_allow_html=True)

    df_sorted = df_year.sort_values('jumlah_kasus', ascending=True)
    short_names = df_sorted['nama_kabupaten_kota'].str.replace('KABUPATEN ','KAB. ').str.replace('KOTA ','Kota ')

    fig_bar = go.Figure(go.Bar(
        x=df_sorted['jumlah_kasus'],
        y=short_names,
        orientation='h',
        marker=dict(
            color=df_sorted['jumlah_kasus'],
            colorscale=[[0,'#f5b7b1'],[0.5,'#e74c3c'],[1,'#7b241c']],
            showscale=False
        ),
        text=df_sorted['jumlah_kasus'],
        textposition='outside',
        textfont=dict(color='#ecf0f1', size=9)
    ))
    fig_bar.update_layout(
        height=420, margin=dict(l=0, r=40, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', tickfont=dict(color='#95a5a6')),
        yaxis=dict(tickfont=dict(color='#ecf0f1', size=9), showgrid=False)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── ROW 2: TREN + DONUT ───────────────────────────────────────────────────────
col_trend, col_donut = st.columns(2)

with col_trend:
    st.markdown('<div class="section-title">📉 Tren Total Kasus 2022–2024</div>', unsafe_allow_html=True)

    yearly = df.groupby('tahun')['jumlah_kasus'].agg(['sum','mean']).reset_index()
    yearly.columns = ['tahun','total','rata_rata']

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(go.Scatter(
        x=yearly['tahun'], y=yearly['total'], name='Total Kasus',
        mode='lines+markers+text',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10, color='#e74c3c'),
        fill='tozeroy', fillcolor='rgba(231,76,60,0.12)',
        text=yearly['total'].apply(lambda x: f"{x:,}"),
        textposition='top center', textfont=dict(color='#e74c3c', size=11)
    ), secondary_y=False)
    fig_trend.add_trace(go.Scatter(
        x=yearly['tahun'], y=yearly['rata_rata'].round(1), name='Rata-rata/Kab',
        mode='lines+markers',
        line=dict(color='#f39c12', width=2, dash='dot'),
        marker=dict(size=8, color='#f39c12')
    ), secondary_y=True)
    fig_trend.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(font=dict(color='#ecf0f1'), bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(tickfont=dict(color='#95a5a6'), gridcolor='rgba(255,255,255,0.06)', tickmode='array', tickvals=yearly['tahun'].tolist()),
    )
    fig_trend.update_yaxes(tickfont=dict(color='#95a5a6'), gridcolor='rgba(255,255,255,0.06)', secondary_y=False)
    fig_trend.update_yaxes(tickfont=dict(color='#f39c12'), showgrid=False, secondary_y=True)
    st.plotly_chart(fig_trend, use_container_width=True)

with col_donut:
    st.markdown(f'<div class="section-title">🥧 Proporsi Top 5 Kab/Kota — {year}</div>', unsafe_allow_html=True)

    top5   = df_year.nlargest(5, 'jumlah_kasus')
    others = df_year['jumlah_kasus'].sum() - top5['jumlah_kasus'].sum()
    labels = list(top5['nama_kabupaten_kota'].str.replace('KABUPATEN ','').str.replace('KOTA ','Kota ')) + ['Lainnya']
    values = list(top5['jumlah_kasus']) + [others]

    fig_donut = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.5,
        marker=dict(colors=['#e74c3c','#e67e22','#f1c40f','#3498db','#9b59b6','#7f8c8d'],
                    line=dict(color='#0f1923', width=2)),
        textfont=dict(color='#ecf0f1'),
    ))
    fig_donut.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(font=dict(color='#ecf0f1', size=10), bgcolor='rgba(0,0,0,0)',
                    orientation='v', x=1.0)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ── ROW 3: TREND PER KAB + GROUPED BAR ───────────────────────────────────────
col_kab, col_grp = st.columns(2)

with col_kab:
    st.markdown(f'<div class="section-title">📈 Tren — {selected_kab}</div>', unsafe_allow_html=True)

    df_kab = df[df['nama_kabupaten_kota'] == selected_kab].sort_values('tahun')
    fig_kab = go.Figure()
    fig_kab.add_trace(go.Scatter(
        x=df_kab['tahun'], y=df_kab['jumlah_kasus'],
        mode='lines+markers+text',
        line=dict(color='#3498db', width=3),
        marker=dict(size=12, color='#3498db'),
        fill='tozeroy', fillcolor='rgba(52,152,219,0.12)',
        text=df_kab['jumlah_kasus'], textposition='top center',
        textfont=dict(color='#3498db', size=12)
    ))
    fig_kab.update_layout(
        height=300, margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickfont=dict(color='#95a5a6'), gridcolor='rgba(255,255,255,0.06)',
                   tickmode='array', tickvals=df_kab['tahun'].tolist()),
        yaxis=dict(tickfont=dict(color='#95a5a6'), gridcolor='rgba(255,255,255,0.06)',
                   title=dict(text='Jumlah Kasus', font=dict(color='#95a5a6')))
    )
    st.plotly_chart(fig_kab, use_container_width=True)

with col_grp:
    st.markdown('<div class="section-title">📊 Perbandingan 2022 vs 2023 vs 2024</div>', unsafe_allow_html=True)

    years_all = sorted(df['tahun'].unique())
    colors_yr = ['#e74c3c', '#f39c12', '#27ae60']
    fig_grp = go.Figure()
    for i, y_ in enumerate(years_all):
        df_y = df[df['tahun'] == y_].sort_values('nama_kabupaten_kota')
        short = df_y['nama_kabupaten_kota'].str.replace('KABUPATEN ','KAB. ').str.replace('KOTA ','Kota ')
        fig_grp.add_trace(go.Bar(
            name=str(y_), x=short, y=df_y['jumlah_kasus'],
            marker_color=colors_yr[i], opacity=0.85
        ))
    fig_grp.update_layout(
        barmode='group', height=300,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(font=dict(color='#ecf0f1'), bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(tickfont=dict(color='#ecf0f1', size=8), showgrid=False),
        yaxis=dict(tickfont=dict(color='#95a5a6'), gridcolor='rgba(255,255,255,0.06)')
    )
    st.plotly_chart(fig_grp, use_container_width=True)

# ── TABEL RANKING ─────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-title">🏆 Tabel Ranking Kabupaten/Kota — {year}</div>', unsafe_allow_html=True)

df_rank = df_year[['nama_kabupaten_kota','jumlah_kasus']].sort_values('jumlah_kasus', ascending=False).reset_index(drop=True)
df_rank.index += 1
df_rank.columns = ['Kabupaten / Kota', 'Jumlah Kasus']
df_rank['% dari Total'] = (df_rank['Jumlah Kasus'] / df_rank['Jumlah Kasus'].sum() * 100).round(2).astype(str) + '%'

st.dataframe(
    df_rank,
    use_container_width=True,
    height=400,
    column_config={
        'Jumlah Kasus': st.column_config.ProgressColumn(
            'Jumlah Kasus',
            min_value=0,
            max_value=int(df_rank['Jumlah Kasus'].max()),
            format="%d"
        )
    }
)

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#95a5a6;font-size:.78rem;'>"
    "Dashboard Penyebaran HIV · Jawa Barat · "
    "Sumber: Dinas Kesehatan Provinsi Jawa Barat via Open Data Jabar · "
    "Dibuat untuk Tugas Akhir Perencanaan Perangkat Lunak</p>",
    unsafe_allow_html=True
)
