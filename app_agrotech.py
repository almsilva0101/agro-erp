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
        st.markdown("<h2 style='text-align: center;'>🛰️ AgroOS
