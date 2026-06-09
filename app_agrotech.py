import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
from sqlalchemy import text

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
# 2. CONTROLO DE SESSÃO
# ==========================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = ""

def com_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ==========================================
# 3. MOTOR DE BASE DE DADOS (SUPABASE NUVEM)
# ==========================================
conn = st.connection("supabase", type="sql")

def inicializar_estruturas_nuvem():
    try:
        with conn.session as s:
            s.execute(text("""
                CREATE TABLE IF NOT EXISTS erp_usuarios (
                    usuario TEXT PRIMARY KEY,
                    senha_hash TEXT,
                    perfil TEXT,
                    data_cadastro TEXT
                );
            """))
            s.execute(text("""
                CREATE TABLE IF NOT EXISTS frota_manual (
                    id TEXT PRIMARY KEY,
                    categoria TEXT,
                    fabricante TEXT,
                    chassi TEXT,
                    operador TEXT
                );
            """))
            s.execute(text(f"""
                INSERT INTO erp_usuarios (usuario, senha_hash, perfil, data_cadastro) 
                VALUES ('admin', '{com_hash('admin')}', 'Administrador', '2026-06-09')
                ON CONFLICT (usuario) DO NOTHING;
            """))
            s.commit()
    except Exception as e:
        st.error(f"⚠️ Erro de inicialização de tabelas: {e}")

inicializar_estruturas_nuvem()

def ler_dados_nuvem():
    df_l = conn.query("SELECT * FROM lavoura;")
    df_p = conn.query("SELECT * FROM pecuaria;")
    df_r = conn.query("SELECT * FROM rotas;")
    
    try:
        df_f = conn.query("SELECT * FROM telemetria_tempo_real;", ttl=0)
        df_f["size_map"] = df_f["status"].apply(lambda x: 30 if x == "CRÍTICO" else 12)
    except:
        df_f = pd.DataFrame(columns=["id_equipamento", "modelo", "lat", "lon", "status", "rpm_motor", "temp_motor_c", "nivel_diesel_lts"])
        
    df_m = conn.query("SELECT * FROM frota_manual;")
    return df_l, df_p, df_r, df_f, df_m

df_lavoura, df_pecuaria, df_rotas, df_frota, df_manual = ler_dados_nuvem()

# ==========================================
# 4. ECRÃS DO SISTEMA
# ==========================================
def tela_autenticacao():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>🛰️ AgroOS Enterprise</h2>", unsafe_allow_html=True)
        
        menu_auth = st.radio("Selecione uma opção", ["Entrar no Sistema", "Criar Nova Conta (Auto-Cadastro)"], horizontal=True)
        st.markdown("---")
        
        if menu_auth == "Entrar no Sistema":
            user = st.text_input("Usuário/E-mail", key="login_user")
            password = st.text_input("Senha", type="password", key="login_pass")
            
            if st.button("Autenticar no ERP", use_container_width=True, type="primary"):
                df_user = conn.query(f"SELECT * FROM erp_usuarios WHERE usuario = '{user}';", ttl=0)
                if not df_user.empty and df_user.iloc[0]['senha_hash'] == com_hash(password):
                    st.session_state['logado'] = True
                    st.session_state['usuario'] = user
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")
                    
        elif menu_auth == "Criar Nova Conta (Auto-Cadastro)":
            st.markdown("##### Formulário de Acesso ao Sistema")
            novo_user = st.text_input("Escolha um Nome de Usuário", placeholder="Ex: joao.silva")
            novo_perfil = st.selectbox("Seu Cargo/Perfil", ["Gestor de Operações", "Agrônomo", "Operador de Máquinas", "Logística"])
            nova_senha = st.text_input("Crie uma Senha Forte", type="password")
            confirma_senha = st.text_input("Confirme a Senha", type="password")
            
            if st.button("Registrar na Nuvem", use_container_width=True, type="primary"):
                if not novo_user or not nova_senha:
                    st.error("⚠️ Todos os campos são obrigatórios.")
                elif nova_senha != confirma_senha:
                    st.error("❌ As senhas não coincidem.")
                else:
                    df_existe = conn.query(f"SELECT * FROM erp_usuarios WHERE usuario = '{novo_user}';", ttl=0)
                    if not df_existe.empty:
                        st.error("❌ Este nome de utilizador já está em uso.")
                    else:
                        hash_db = com_hash(nova_senha)
                        data_atual = datetime.now().strftime("%Y-%m-%d")
                        with conn.session as s:
                            s.execute(text(f"INSERT INTO erp_usuarios (usuario, senha_hash, perfil, data_cadastro) VALUES ('{novo_user}', '{hash_db}', '{novo_perfil}', '{data_atual}');"))
                            s.commit()
                        st.success("🎉 Conta criada com sucesso! Mude para a aba 'Entrar no Sistema'.")
                        
        st.markdown('</div>', unsafe_allow_html=True)

def tela_dashboard():
    st.markdown("<h3>🌐 Centro de Comando Integrado (C4)</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="glass-card"><div class="metric-title">Área Mapeada</div><div class="metric-value">{df_lavoura["Hectares"].sum():,.0f} ha</div><div class="metric-delta">{len(df_lavoura)} Talhões</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="glass-card"><div class="metric-title">Rebanho Ativo</div><div class="metric-value">{df_pecuaria["Cabecas"].sum():,.0f} Cab</div><div class="metric-delta">{len(df_pecuaria)} Lotes</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="glass-card"><div class="metric-title">Carga em Trânsito</div><div class="metric-value">{df_rotas["Carga_Ton"].sum():,.0f} Ton</div><div class="metric-delta">{len(df_rotas)} CT-es</div></div>', unsafe_allow_html=True)
    criticos = len(df_frota[df_frota["status"] == "CRÍTICO"]) if not df_frota.empty else 0
    c4.markdown(f'<div class="glass-card"><div class="metric-title">🚨 Máquinas Críticas (IoT)</div><div class="metric-value metric-alert">{criticos}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab_frota, tab_lavoura, tab_pecuaria, tab_logistica = st.tabs(["🚜 Radar IoT da Frota", "🌾 Agronomia & Solos", "🐄 Gestão Pecuária", "🚛 Logística & Escoamento"])

    with tab_frota:
        if df_frota.empty:
            st.warning("⚠️ A aguardar dados do simulador_iot.py... Ligue o script no seu computador.")
        else:
            col_m1, col_m2 = st.columns([1.2, 1])
            with col_m1:
                cores = {"Operacional": "#10B981", "Atenção": "#F59E0B", "CRÍTICO": "#EF4444"}
                fig_mapa = px.scatter_mapbox(df_frota, lat="lat", lon="lon", color="status", size="size_map", hover_name="id_equipamento", hover_data=["modelo", "rpm_motor", "temp_motor_c"], color_discrete_map=cores, zoom=8.5, center={"lat": -12.8, "lon": -55.8}, title="Radar GPS Transmissão contínua")
                fig_mapa.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":40,"l":0,"b":0}, paper_bgcolor="#050810")
                st.plotly_chart(fig_mapa, use_container_width=True, height=450)
            
            with col_m2:
                fig_oee = px.scatter(df_frota, x="rpm_motor", y="temp_motor_c", color="status", size="nivel_diesel_lts", hover_name="id_equipamento", title="Telemetria CAN Bus em Tempo Real", color_discrete_map=cores)
                fig_oee.update_layout(template="plotly_dark", paper_bgcolor="#050810", plot_bgcolor="#050810")
                st.plotly_chart(fig_oee, use_container_width=True, height=450)
            st.dataframe(df_frota, use_container_width=True, height=200)

    with tab_lavoura:
        st.dataframe(df_lavoura.style.background_gradient(subset=['NDVI_Saude'], cmap='YlGn'), use_container_width=True, height=350)
    with tab_pecuaria:
        st.dataframe(df_pecuaria.style.highlight_max(subset=['Mortalidade_Perc'], color='#7F1D1D'), use_container_width=True, height=350)
    with tab_logistica:
        st.dataframe(df_rotas, use_container_width=True, height=350)

def tela_cadastro():
    st.title("🗂️ Cadastro de Master Data (Nuvem)")
    st.markdown("Insira novos equipamentos diretamente na tabela permanente do Supabase.")
    
    with st.form("form_cadastro_nuvem"):
        col1, col2, col3 = st.columns(3)
        id_ativo = col1.text_input("ID/Código do Ativo", placeholder="Ex: TR-999")
        tipo = col1.selectbox("Categoria", ["Trator de Esteira", "Colheitadeira", "Pulverizador Autopropelido", "Caminhão Graneleiro"])
        fabricante = col2.text_input("Fabricante/Marca", placeholder="Ex: John Deere / Case IH")
        chassi = col2.text_input("Chassi / VIN")
        operador = col3.text_input("Operador Padrão Designado")
        
        if st.form_submit_button("Sincronizar com Banco de Dados Cloud", type="primary"):
            if id_ativo:
                id_clean = id_ativo.replace("'", "")
                try:
                    with conn.session as s:
                        s.execute(text(f"INSERT INTO frota_manual VALUES ('{id_clean}', '{tipo}', '{fabricante}', '{chassi}', '{operador}');"))
                        s.commit()
                    st.success(f"✅ Ativo {id_clean} gravado com sucesso no Supabase!")
                    st.rerun() 
                except Exception as e:
                    st.error(f"❌ Erro ao guardar: {e}")
            else:
                st.error("O campo ID/Código é obrigatório.")
                
    st.markdown("---")
    st.markdown("##### 🗄️ Ativos Cadastrados via Tela (Armazenados no PostgreSQL)")
    st.dataframe(df_manual, use_container_width=True)

# ==========================================
# 5. ROTEAMENTO DO ERP
# ==========================================
if not st.session_state['logado']:
    tela_autenticacao()
else:
    st.sidebar.markdown(f"**👤 Operador:** {st.session_state['usuario'].upper()}")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Módulos do Sistema", ["📊 Monitor C4 (Dashboard)", "🗂️ Inserção de Dados (Data Entry)"])
    st.sidebar.markdown("---")
    
    if menu == "📊 Monitor C4 (Dashboard)":
        if st.sidebar.button("🔄 Atualizar Radar IoT", use_container_width=True):
            st.rerun()
        tela_dashboard()
        
    elif menu == "🗂️ Inserção de Dados (Data Entry)":
        tela_cadastro()

    st.sidebar.markdown("---")
    if st.sidebar.button("Encerrar Sessão", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['usuario'] = ""
        st.rerun()
