
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. SETUP & UI/UX DESIGN
# ==========================================
st.set_page_config(
    page_title="AgroOS | Enterprise ERP", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #050810; 
        color: #E2E8F0; 
    }
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    .glass-card { 
        background: rgba(25, 30, 45, 0.65); 
        border: 1px solid rgba(255, 255, 255, 0.08); 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
    }
    .metric-title { 
        font-size: 0.85rem; 
        color: #94A3B8; 
        text-transform: uppercase; 
        margin-bottom: 5px; 
    }
    .metric-value { font-size: 2rem; font-weight: 600; color: #FFFFFF; }
    .metric-alert { color: #EF4444; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { 
        background-color: transparent; gap: 10px; margin-bottom: 15px; 
    }
    .stTabs [data-baseweb="tab"] { 
        color: #8c9baf; background-color: #111827; 
        border-radius: 8px; padding: 10px 20px; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1F2937 !important; 
        color: #3B82F6 !important; 
        border-bottom: 2px solid #3B82F6; 
    }
    [data-testid="stSidebar"] { 
        background-color: #0B0F19; 
        border-right: 1px solid rgba(255,255,255,0.1); 
    }
    [data-testid="stDataFrame"] { 
        background-color: #111827; border-radius: 8px; 
    }
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
    colunas = ["ID", "Tipo", "Fabricante", "Chassi", "Operador"]
    st.session_state['frota_cadastrada'] = pd.DataFrame(columns=colunas)

# ==========================================
# 3. MOTOR DE DADOS DE ALTA DENSIDADE
# ==========================================
@st.cache_data
def gerar_dados_densos():
    np.random.seed(42)
    
    # --- DADOS DA LAVOURA ---
    lista_lavoura = []
    culturas = ["Soja M8349", "Soja BRS", "Milho AG8088", "Algodão FM985"]
    agronomos = ["Dr. Carlos Mendes", "Dra. Ana Paula", "Eng. Marcos Silva"]
    unidades = ["Alvorada", "Santa Cruz", "Pampa", "Vale"]
    
    for i in range(1, 41):
        dias_plantio = np.random.randint(30, 120)
        data_plantio = (datetime.today() - timedelta(days=dias_plantio))
        
        lista_lavoura.append({
            "Talhão": f"TL-{i:03d}",
            "Unidade": np.random.choice(unidades),
            "Cultura": np.random.choice(culturas),
            "Hectares": np.random.randint(100, 800),
            "Prod_Estimada (Ton)": np.random.randint(300, 3500),
            "NDVI (Saúde)": round(np.random.uniform(0.5, 0.95), 2),
            "Umidade Solo (%)": np.random.randint(15, 45),
            "Nitrogênio (ppm)": np.random.randint(20, 80),
            "Agrônomo Resp.": np.random.choice(agronomos),
            "Data Plantio": data_plantio.strftime("%Y-%m-%d")
        })
    df_lavoura = pd.DataFrame(lista_lavoura)
    
    # --- DADOS DA PECUÁRIA ---
    lista_pecuaria = []
    racas = ["Nelore", "Angus", "Brahman", "Cruzamento Industrial"]
    dietas = ["Pasto Brachiaria", "Confinamento Grão", "Pasto + Sup."]
    veterinarios = ["Vet. Júlia Costa", "Vet. Roberto Alves"]
    
    for i in range(1, 26):
        rfid = np.random.randint(1000, 9999)
        lista_pecuaria.append({
            "Lote (RFID)": f"LT-BR-{rfid}",
            "Raça": np.random.choice(racas),
            "Cabeças": np.random.randint(50, 300),
            "Peso Médio (@)": round(np.random.uniform(12.0, 22.0), 1),
            "Dieta": np.random.choice(dietas),
            "Mortalidade (%)": round(np.random.uniform(0.1, 2.5), 2),
            "Imunização (%)": np.random.randint(85, 100),
            "Idade Média (M)": np.random.randint(12, 36),
            "Veterinário": np.random.choice(veterinarios)
        })
    df_pecuaria = pd.DataFrame(lista_pecuaria)
    
    # --- DADOS DE LOGÍSTICA ---
    lista_rotas = []
    motoristas = ["Sérgio", "Antônio", "Pedro", "José"]
    transps = ["JSL", "Rumo", "Cargill", "Autônomo"]
    portos = ["Santos (SP)", "Paranaguá (PR)", "Itaqui (MA)"]
    
    for i in range(1, 16):
        porto = np.random.choice(portos)
        lat_d = -23.96 if "Santos" in porto else (-25.50 if "PR" in porto else -2.57)
        lon_d = -46.33 if "Santos" in porto else (-48.51 if "PR" in porto else -44.37)
        cte = np.random.randint(100000, 999999)
        placa_num = np.random.randint(1000,9999)
        
        lista_rotas.append({
            "Manifesto": f"CT-{cte}",
            "Motorista": np.random.choice(motoristas),
            "Placa": f"XYZ-{placa_num}",
            "Transportadora": np.random.choice(transps),
            "Destino": porto,
            "Carga (Ton)": np.random.randint(35, 55),
            "Custo Frete (R$)": np.random.randint(8000, 15000),
            "Espera Porto (h)": np.random.randint(4, 72),
            "Lat_O": -12.54 + np.random.normal(0, 2),
            "Lon_O": -55.72 + np.random.normal(0, 2),
            "Lat_D": lat_d,
            "Lon_D": lon_d
        })
    df_rotas = pd.DataFrame(lista_rotas)
    
    return df_lavoura, df_pecuaria, df_rotas

def calcular_telemetria_frota(hora_simulada):
    np.random.seed(hora_simulada)
    lista_frota = []
    operadores = ["Marcos", "Leandro", "Tiago", "Felipe", "João"]
    modelos = ["JD S700", "Case 250", "MF 9895", "NH CR8.90"]
    lat_b = -12.8
    lon_b = -55.8 
    
    for i in range(1, 31):
        risco = np.random.choice(["Operacional", "Atenção", "CRÍTICO"], p=[0.75, 0.15, 0.10])
        status = risco
        
        # Variáveis Curtas para o Bloco de Notas não cortar
        calc_lat = lat_b + (hora_simulada*0.01) + np.random.normal(0, 0.05)
        calc_lon = lon_b + (hora_simulada*0.01) + np.random.normal(0, 0.05)
        chassi_num = np.random.randint(10000,99999)
        temp_nrm = np.random.randint(85, 115)
        temp_crt = np.random.randint(110, 130)
        temp_final = temp_nrm if status != "CRÍTICO" else temp_crt
        dias_rev = np.random.randint(5, 200)
        data_rev = (datetime.today() - timedelta(days=dias_rev)).strftime("%d/%m/%Y")
        
        lista_frota.append({
            "ID Ativo": f"MAQ-{i:03d}",
            "Modelo": np.random.choice(modelos),
            "Chassi (VIN)": f"9B9{chassi_num}BR",
            "Operador": np.random.choice(operadores),
            "Lat": calc_lat,
            "Lon": calc_lon,
            "Status IA": status,
            "OEE (%)": round(np.random.uniform(40, 95), 1),
            "Tanque Diesel (%)": np.random.randint(10, 100),
            "Temp. Motor (°C)": temp_final,
            "RPM Atual": np.random.randint(1500, 2400),
            "Ociosidade (h)": round(np.random.uniform(0, 5), 1),
            "Última Revisão": data_rev,
            "Size_Map": 12 if status != "CRÍTICO" else 30
        })
    return pd.DataFrame(lista_frota)

df_lavoura, df_pecuaria, df_rotas = gerar_dados_densos()

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
    
    # KPIs SUPERIORES
    c1, c2, c3, c4 = st.columns(4)
    total_ha = df_lavoura["Hectares"].sum()
    total_lote = len(df_lavoura)
    c1.markdown(f'<div class="glass-card"><div class="metric-title">Área Mapeada</div><div class="metric-value">{total_ha:,.0f} ha</div><div class="metric-delta">{total_lote} Talhões</div></div>', unsafe_allow_html=True)
    
    total_cab = df_pecuaria["Cabeças"].sum()
    lotes_pec = len(df_pecuaria)
    c2.markdown(f'<div class="glass-card"><div class="metric-title">Rebanho Ativo</div><div class="metric-value">{total_cab:,.0f} Cab</div><div class="metric-delta">{lotes_pec} Lotes</div></div>', unsafe_allow_html=True)
    
    total_ton = df_rotas["Carga (Ton)"].sum()
    ctes = len(df_rotas)
    c3.markdown(f'<div class="glass-card"><div class="metric-title">Carga em Trânsito</div><div class="metric-value">{total_ton:,.0f} Ton</div><div class="metric-delta">{ctes} CT-es</div></div>', unsafe_allow_html=True)
    
    criticos = len(df_frota[df_frota["Status IA"] == "CRÍTICO"])
    c4.markdown(f'<div class="glass-card"><div class="metric-title">🚨 Máquinas Críticas</div><div class="metric-value metric-alert">{criticos}</div><div class="metric-delta">Ação requerida</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab_frota, tab_lavoura, tab_pecuaria, tab_logistica = st.tabs([
        "🚜 Frota & Telemetria", "🌾 Agronomia & Solos", "🐄 Gestão Pecuária", "🚛 Logística & Escoamento"
    ])

    # ABA 1: FROTA 
    with tab_frota:
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            cores_mapa = {"Operacional": "#10B981", "Atenção": "#F59E0B", "CRÍTICO": "#EF4444"}
            fig_mapa = px.scatter_mapbox(
                df_frota, lat="Lat", lon="Lon", color="Status IA", size="Size_Map", 
                hover_name="ID Ativo", color_discrete_map=cores_mapa, 
                zoom=9.5, center={"lat": -12.8, "lon": -55.8}, title="Radar GPS"
            )
            fig_mapa.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":40,"l":0,"b":0}, paper_bgcolor="#050810")
            st.plotly_chart(fig_mapa, use_container_width=True, height=400)
            
        with col_m2:
            fig_oee = px.scatter(
                df_frota, x="OEE (%)", y="Temp. Motor (°C)", color="Status IA", size="Tanque Diesel (%)", 
                hover_name="ID Ativo", hover_data=["Operador", "RPM Atual"], title="Matriz de Desgaste",
                color_discrete_map=cores_mapa
            )
            fig_oee.update_layout(template="plotly_dark", paper_bgcolor="#050810", plot_bgcolor="#050810")
            st.plotly_chart(fig_oee, use_container_width=True, height=400)
        
        st.markdown("##### 📋 Datagrid de Telemetria (Rastreio Individual)")
        st.dataframe(df_frota.drop(columns=["Lat", "Lon", "Size_Map"]), use_container_width=True, height=250)

    # ABA 2: LAVOURA 
    with tab_lavoura:
        col_l1, col_l2 = st.columns([1, 2])
        with col_l1:
            fig_cult = px.pie(df_lavoura, names="Cultura", values="Hectares", hole=0.6, title="Culturas")
            fig_cult.update_layout(template="plotly_dark", paper_bgcolor="#050810")
            st.plotly_chart(fig_cult, use_container_width=True)
        with col_l2:
            st.markdown("##### 📋 Book Agronômico")
            st.dataframe(df_lavoura.style.background_gradient(subset=['NDVI (Saúde)'], cmap='YlGn'), use_container_width=True, height=350)

    # ABA 3: PECUÁRIA 
    with tab_pecuaria:
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            fig_gado = px.box(df_pecuaria, x="Raça", y="Peso Médio (@)", color="Raça", title="Peso por Raça")
            fig_gado.update_layout(template="plotly_dark", paper_bgcolor="#050810", showlegend=False)
            st.plotly_chart(fig_gado, use_container_width=True)
        with col_p2:
            st.markdown("##### 📋 Inventário de Rebanho")
            st.dataframe(df_pecuaria.style.highlight_max(subset=['Mortalidade (%)'], color='#7F1D1D'), use_container_width=True, height=350)

    # ABA 4: LOGÍSTICA 
    with tab_logistica:
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            fig_rotas = go.Figure()
            for _, row in df_rotas.iterrows():
                cor_linha = "#EF4444" if row['Espera Porto (h)'] > 24 else "#3B82F6"
                fig_rotas.add_trace(go.Scattermapbox(
                    mode="lines+markers", lon=[row['Lon_O'], row['Lon_D']], lat=[row['Lat_O'], row['Lat_D']],
                    marker={'size': 10}, line=dict(width=3, color=cor_linha),
                    name=row['Destino'], text=f"Placa: {row['Placa']} | Motorista: {row['Motorista']}"
                ))
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
        
        if st.form_submit_button("Sincronizar com ERP Cloud", type="primary"):
            if id_ativo:
                novo_dict = {"ID": id_ativo, "Tipo": tipo, "Fabricante": fabricante, "Chassi": chassi, "Operador": operador}
                novo_dado = pd.DataFrame([novo_dict])
                st.session_state['frota_cadastrada'] = pd.concat([st.session_state['frota_cadastrada'], novo_dado], ignore_index=True)
                st.success("Registro inserido com sucesso!")
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
        
        st.sidebar.markdown("---")
        csv_export = df_frota.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 Extrair Log de Telemetria", data=csv_export, file_name='telemetria.csv', mime='text/csv', use_container_width=True)
        
    elif menu == "🗂️ Inserção de Dados (Data Entry)":
        tela_cadastro()

    st.sidebar.markdown("---")
    if st.sidebar.button("Encerrar Sessão", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['usuario'] = ""
        st.rerun()