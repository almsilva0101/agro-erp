import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. SETUP & UI/UX DESIGN
# ==========================================
st.set_page_config(page_title="AgroOS | Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050810; color: #E2E8F0; }
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    .glass-card { background: rgba(25, 30, 45, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .metric-title { font-size: 0.85rem; color: #94A3B8; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { font-size: 2rem; font-weight: 600; color: #FFFFFF; }
    .metric-alert { color: #EF4444; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 10px; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab"] { color: #8c9baf; background-color: #111827; border-radius: 8px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #1F2937 !important; color: #3B82F6 !important; border-bottom: 2px solid #3B82F6; }
    [data-testid="stSidebar"] { background-color: #0B0F19; border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stDataFrame"] { background-color: #111827; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONTROLE DE SESSÃO
# ==========================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = ""
if 'frota_cadastrada' not in st.session_state:
    st.session_state['frota_cadastrada'] = pd.DataFrame(columns=["ID", "Tipo", "Fabricante", "Chassi", "Operador"])

# ==========================================
# 3. MOTOR DE BANCO DE DADOS (SUPABASE NUVEM)
# ==========================================
# Cria a conexão com o Supabase usando o "Secret"
conn = st.connection("supabase", type="sql")

def inicializar_banco_nuvem():
    try:
        # Verifica se a tabela "Lavoura" já existe
        df_check = conn.query("SELECT table_name FROM information_schema.tables WHERE table_name = 'Lavoura';")
        
        if df_check.empty:
            st.toast("⚙️ Criando tabelas no Supabase pela primeira vez...")
            culturas = ["Soja M8349", "Soja BRS", "Milho AG8088", "Algodão FM985"]
            df_lavoura = pd.DataFrame([{"Talhao": f"TL-{i:03d}", "Unidade": np.random.choice(["Alvorada", "Santa Cruz"]), "Cultura": np.random.choice(culturas), "Hectares": np.random.randint(100, 800), "Prod_Estimada_Ton": np.random.randint(300, 3500), "NDVI_Saude": round(np.random.uniform(0.5, 0.95), 2)} for i in range(1, 41)])
            df_pecuaria = pd.DataFrame([{"Lote": f"LT-BR-{np.random.randint(1000, 9999)}", "Raca": np.random.choice(["Nelore", "Angus"]), "Cabecas": np.random.randint(50, 300), "Peso_Arroba": round(np.random.uniform(12.0, 22.0), 1), "Mortalidade_Perc": round(np.random.uniform(0.1, 2.5), 2), "Vacinados_Perc": np.random.randint(85, 100)} for i in range(1, 26)])
            df_rotas = pd.DataFrame([{"Manifesto": f"CT-{np.random.randint(100000, 999999)}", "Motorista": np.random.choice(["Sérgio", "Antônio"]), "Placa": f"XYZ-{np.random.randint(1000,9999)}", "Destino": "Santos (SP)", "Carga_Ton": np.random.randint(35, 55), "Espera_Porto_h": np.random.randint(4, 72), "Lat_O": -12.54, "Lon_O": -55.72, "Lat_D": -23.96, "Lon_D": -46.33} for i in range(1, 16)])

            # Envia os dados para a nuvem
            df_lavoura.to_sql('Lavoura', con=conn.engine, if_exists='replace', index=False)
            df_pecuaria.to_sql('Pecuaria', con=conn.engine, if_exists='replace', index=False)
            df_rotas.to_sql('Rotas', con=conn.engine, if_exists='replace', index=False)
    except Exception as e:
        st.error(f"⚠️ Erro ao conectar no Supabase. Detalhe: {e}")

# Inicia a checagem ao carregar a página
inicializar_banco_nuvem()

@st.cache_data(ttl=600)
def ler_dados_nuvem():
    df_l = conn.query("SELECT * FROM Lavoura")
    df_p = conn.query("SELECT * FROM Pecuaria")
    df_r = conn.query("SELECT * FROM Rotas")
    return df_l, df_p, df_r

df_lavoura, df_pecuaria, df_rotas = ler_dados_nuvem()

def calcular_telemetria_frota(hora_simulada):
    np.random.seed(hora_simulada)
    lista_frota = []
    operadores = ["Marcos", "Leandro", "Tiago", "Felipe", "João"]
    modelos = ["JD S700", "Case 250", "MF 9895", "NH CR8.90"]
    lat_b, lon_b = -12.8, -55.8 
    
    for i in range(1, 31):
        risco = np.random.choice(["Operacional", "Atenção", "CRÍTICO"], p=[0.75, 0.15, 0.10])
        status = risco
        lista_frota.append({
            "ID Ativo": f"MAQ-{i:03d}",
            "Modelo": np.random.choice(modelos),
            "Chassi (VIN)": f"9B9{np.random.randint(10000,99999)}BR",
            "Operador": np.random.choice(operadores),
            "Lat": lat_b + (hora_simulada*0.01) + np.random.normal(0, 0.05),
            "Lon": lon_b + (hora_simulada*0.01) + np.random.normal(0, 0.05),
            "Status IA": status,
            "OEE (%)": round(np.random.uniform(40, 95), 1),
            "Tanque Diesel (%)": np.random.randint(10, 100),
            "Temp. Motor (°C)": np.random.randint(85, 115) if status != "CRÍTICO" else np.random.randint(110, 130),
            "RPM Atual": np.random.randint(1500, 2400),
            "Ociosidade (h)": round(np.random.uniform(0, 5), 1),
            "Size_Map": 12 if status != "CRÍTICO" else 30
        })
    return pd.DataFrame(lista_frota)

# ==========================================
# 4. TELAS DO SISTEMA
# ==========================================
def tela_login():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>🛰️ AgroOS</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8;'>Acesso Restrito</p>", unsafe_allow_html=True)
        
        usuario = st.text_input("Usuário", placeholder="admin")
        senha = st.text_input("Senha", type="password", placeholder="admin")
        
        if st.button("Autenticar no ERP", use_container_width=True, type="primary"):
            if usuario == "admin" and senha == "admin":
                st.session_state['logado'] = True
                st.session_state['usuario'] = usuario
                st.rerun()
            else:
                st.error("Acesso Negado.")
        st.markdown('</div>', unsafe_allow_html=True)

def tela_dashboard(df_frota):
    st.markdown("<h3>🌐 Centro de Comando Integrado (C4)</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="glass-card"><div class="metric-title">Área Mapeada</div><div class="metric-value">{df_lavoura["Hectares"].sum():,.0f} ha</div><div class="metric-delta">{len(df_lavoura)} Talhões</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="glass-card"><div class="metric-title">Rebanho Ativo</div><div class="metric-value">{df_pecuaria["Cabecas"].sum():,.0f} Cab</div><div class="metric-delta">{len(df_pecuaria)} Lotes</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="glass-card"><div class="metric-title">Carga em Trânsito</div><div class="metric-value">{df_rotas["Carga_Ton"].sum():,.0f} Ton</div><div class="metric-delta">{len(df_rotas)} CT-es</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="glass-card"><div class="metric-title">🚨 Máquinas Críticas</div><div class="metric-value metric-alert">{len(df_frota[df_frota["Status IA"] == "CRÍTICO"])}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab_frota, tab_lavoura, tab_pecuaria, tab_logistica = st.tabs(["🚜 Frota & Telemetria", "🌾 Agronomia & Solos", "🐄 Gestão Pecuária", "🚛 Logística & Escoamento"])

    with tab_frota:
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            cores = {"Operacional": "#10B981", "Atenção": "#F59E0B", "CRÍTICO": "#EF4444"}
            fig_mapa = px.scatter_mapbox(df_frota, lat="Lat", lon="Lon", color="Status IA", size="Size_Map", hover_name="ID Ativo", color_discrete_map=cores, zoom=9.5, center={"lat": -12.8, "lon": -55.8}, title="Radar GPS")
            fig_mapa.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":40,"l":0,"b":0}, paper_bgcolor="#050810")
            st.plotly_chart(fig_mapa, use_container_width=True, height=400)
        with col_m2:
            fig_oee = px.scatter(df_frota, x="OEE (%)", y="Temp. Motor (°C)", color="Status IA", size="Tanque Diesel (%)", hover_name="ID Ativo", hover_data=["Operador", "RPM Atual"], title="Matriz de Desgaste", color_discrete_map=cores)
            fig_oee.update_layout(template="plotly_dark", paper_bgcolor="#050810", plot_bgcolor="#050810")
            st.plotly_chart(fig_oee, use_container_width=True, height=400)
        st.dataframe(df_frota.drop(columns=["Lat", "Lon", "Size_Map"]), use_container_width=True)

    with tab_lavoura:
        st.markdown("##### 📋 Tabela extraída do Supabase (PostgreSQL)")
        st.dataframe(df_lavoura.style.background_gradient(subset=['NDVI_Saude'], cmap='YlGn'), use_container_width=True, height=350)

    with tab_pecuaria:
        st.markdown("##### 📋 Tabela extraída do Supabase (PostgreSQL)")
        st.dataframe(df_pecuaria.style.highlight_max(subset=['Mortalidade_Perc'], color='#7F1D1D'), use_container_width=True, height=350)

    with tab_logistica:
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            fig_rotas = go.Figure()
            for _, row in df_rotas.iterrows():
                cor_linha = "#EF4444" if row['Espera_Porto_h'] > 24 else "#3B82F6"
                fig_rotas.add_trace(go.Scattermapbox(mode="lines+markers", lon=[row['Lon_O'], row['Lon_D']], lat=[row['Lat_O'], row['Lat_D']], marker={'size': 10}, line=dict(width=3, color=cor_linha), name=row['Destino'], text=f"Placa: {row['Placa']}"))
            fig_rotas.update_layout(title="Corredores Logísticos", mapbox_style="carto-darkmatter", mapbox=dict(center=dict(lat=-15.0, lon=-50.0), zoom=3.0), margin={"r":0,"t":40,"l":0,"b":0}, paper_bgcolor="#050810", showlegend=False)
            st.plotly_chart(fig_rotas, use_container_width=True, height=350)
        with col_c2:
            st.markdown("##### 📋 Diário de Bordo (CT-e)")
            st.dataframe(df_rotas.drop(columns=["Lat_O", "Lon_O", "Lat_D", "Lon_D"]), use_container_width=True, height=350)

def tela_cadastro():
    st.title("🗂️ Cadastro de Master Data")
    st.markdown("Insira novos operadores, equipamentos ou veículos na malha de dados.")
    with st.form("form_cadastro"):
        col1, col2, col3 = st.columns(3)
        id_ativo = col1.text_input("ID/Placa do Ativo", placeholder="Ex: TR-999")
        tipo = col1.selectbox("Categoria", ["Trator", "Colheitadeira", "Pulverizador"])
        fabricante = col2.text_input("Fabricante/Marca", placeholder="Ex: Scania / John Deere")
        chassi = col2.text_input("Chassi/VIN", placeholder="Obrigatório para seguro")
        operador = col3.text_input("Operador Padrão", placeholder="Nome completo")
        
        if st.form_submit_button("Salvar Localmente", type="primary"):
            if id_ativo:
                novo_dict = {"ID": id_ativo, "Tipo": tipo, "Fabricante": fabricante, "Chassi": chassi, "Operador": operador}
                novo_dado = pd.DataFrame([novo_dict])
                st.session_state['frota_cadastrada'] = pd.concat([st.session_state['frota_cadastrada'], novo_dado], ignore_index=True)
                st.success("Registro inserido com sucesso na sessão!")
            else:
                st.error("O campo ID/Placa é obrigatório.")
                
    st.markdown("---")
    st.markdown("##### Registros de Cadastro Manual")
    st.dataframe(st.session_state['frota_cadastrada'], use_container_width=True)

# ==========================================
# 5. ROTEAMENTO
# ==========================================
if not st.session_state['logado']:
    tela_login()
else:
    st.sidebar.markdown(f"**👤 Operador:** {st.session_state['usuario'].upper()}")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Módulos do Sistema", ["📊 Monitor C4 (Dashboard)", "🗂️ Inserção de Dados (Data Entry)"])
    st.sidebar.markdown("---")
    
    if menu == "📊 Monitor C4 (Dashboard)":
        hora = st.sidebar.slider("⏪ Simulador GPS/Telemetria", 0, 12, 0, format="%dh")
        df_frota = calcular_telemetria_frota(hora)
        tela_dashboard(df_frota)
        
    elif menu == "🗂️ Inserção de Dados (Data Entry)":
        tela_cadastro()

    st.sidebar.markdown("---")
    if st.sidebar.button("Encerrar Sessão", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['usuario'] = ""
        st.rerun()
