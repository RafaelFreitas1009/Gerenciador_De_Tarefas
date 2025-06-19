import streamlit as st
import psutil
import pandas as pd

# --- Configuração Inicial da Página ---
st.set_page_config(page_title="Gerenciador de Tarefas", layout="wide")

# --- Tema: Escolha entre Dark ou Light ---
tema = st.sidebar.radio("🎨 Escolha o Tema", ("Claro", "Escuro"))

# Definir cores dinâmicas
if tema == "Claro":
    fundo = "#FFFFFF"
    texto = "#000000"
    cor_card = "#F0F2F6"
    cor_metrica = "#000000"
    cor_tabela = "#FFFFFF"
else:
    fundo = "#0E1117"
    texto = "#FAFAFA"
    cor_card = "#262730"
    cor_metrica = "#FAFAFA"
    cor_tabela = "#1E1E1E"

# --- Aplicar estilo global corrigido ---
st.markdown(
    f"""
    <style>
    /* Fundo geral da aplicação */
    .stApp {{
        background-color: {fundo};
        color: {texto};
    }}

    /* Containers e abas */
    .css-1d391kg, .stTabs [data-baseweb="tab"] {{
        background-color: {cor_card};
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }}

    /* Texto geral */
    .css-10trblm, .css-1cpxqw2, .css-1v3fvcr {{
        color: {texto} !important;
    }}

    /* Labels de métricas */
    .stMetricLabel {{
        color: {texto} !important;
        font-size: 16px !important;
    }}

    /* Valores das métricas */
    div[data-testid="stMetricValue"] {{
        color: {texto} !important;
        font-size: 32px !important;
        font-weight: bold;
    }}

    /* Input PID */
    .stTextInput input {{
        color: {texto} !important;
        background-color: {cor_card} !important;
        border: 1px solid #555 !important;
    }}

    /* Labels dos inputs */
    label, .stNumberInput label {{
        color: {texto} !important;
    }}

    /* Tabelas de dados */
    .stDataFrame {{
        background-color: {cor_tabela};
        color: {texto};
    }}

    /* Containers gerais */
    .st-cg {{
        background-color: {cor_card};
        color: {texto};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Título ---
st.title("🚀 Gerenciador de Tarefas - Monitoramento em Tempo Real")

# --- Funções de Sistema ---
def get_system_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return cpu_percent, memory.percent, disk.percent, memory

def get_battery_info():
    battery = psutil.sensors_battery()
    if battery:
        minutos_restantes = battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
        return battery.percent, battery.power_plugged, minutos_restantes
    else:
        return None, None, None

def get_processes_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    if processes:
        df = pd.DataFrame(processes)
        return df.sort_values(by='cpu_percent', ascending=False).head(10)
    else:
        return pd.DataFrame(columns=['pid', 'name', 'cpu_percent', 'memory_percent'])

def get_process_detail(pid):
    try:
        p = psutil.Process(pid)
        with p.oneshot():
            info = {
                "Nome": p.name(),
                "Status": p.status(),
                "Usuário": p.username(),
                "Uso de CPU (%)": p.cpu_percent(interval=0.1),
                "Uso de Memória (MB)": p.memory_info().rss / 1024 / 1024
            }
        return info
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

# --- Coleta dos Dados ---
cpu_percent, memory_percent, disk_percent, memory = get_system_info()
battery_percent, plugged, minutos_restantes = get_battery_info()

# --- Páginas com Tabs ---
aba1, aba2, aba3 = st.tabs(["🏠 Visão Geral", "📋 Processos", "🔍 Detalhar Processo"])

with aba1:
    with st.container():
        st.subheader("📊 Resumo do Sistema")

        col1, col2, col3, col4 = st.columns(4)

        cpu_color = "normal"
        if cpu_percent > 80:
            cpu_color = "inverse"
        col1.metric(label="🖥️ Uso de CPU", value=f"{cpu_percent}%", delta_color=cpu_color)

        mem_color = "normal"
        if memory_percent > 80:
            mem_color = "inverse"
        col2.metric(label="💾 Uso de Memória", value=f"{memory_percent}%", delta_color=mem_color)

        disk_color = "normal"
        if disk_percent > 80:
            disk_color = "inverse"
        col3.metric(label="📀 Uso de Disco", value=f"{disk_percent}%", delta_color=disk_color)

        if battery_percent is not None:
            status = "🔌 Na tomada" if plugged else "🔋 Na bateria"
            if minutos_restantes is not None:
                delta_text = f"{minutos_restantes} min restantes"
            else:
                delta_text = "Tempo ilimitado"
            bat_color = "normal"
            if battery_percent < 30:
                bat_color = "inverse"
            col4.metric(label="🔋 Bateria", value=f"{battery_percent}%", delta=f"{status} • {delta_text}", delta_color=bat_color)
        else:
            col4.metric(label="🔋 Bateria", value="Não disponível", delta="💻 Desktop?")

    st.divider()
    st.subheader("🖥️ Informações Detalhadas do Sistema")

    col5, col6 = st.columns(2)

    cpu_count = psutil.cpu_count(logical=True)
    cpu_count_fisicos = psutil.cpu_count(logical=False)
    col5.metric("🧠 Núcleos Lógicos", cpu_count)
    col5.metric("🧠 Núcleos Físicos", cpu_count_fisicos)

    memoria_total = memory.total / (1024 ** 3)
    memoria_usada = memory.used / (1024 ** 3)
    memoria_livre = memory.available / (1024 ** 3)

    col6.metric("💾 Memória Total (GB)", f"{memoria_total:.2f}")
    col6.metric("💾 Memória Usada (GB)", f"{memoria_usada:.2f}")
    col6.metric("💾 Memória Livre (GB)", f"{memoria_livre:.2f}")

with aba2:
    st.subheader("📋 Top 10 Processos por Uso de CPU")
    df_processes = get_processes_info()

    if not df_processes.empty:
        st.dataframe(df_processes, use_container_width=True)
    else:
        st.info("Nenhum processo disponível para exibir.")

with aba3:
    st.subheader("🔍 Detalhamento de Processo por PID")
    pid_input = st.number_input("Digite o PID do processo:", min_value=0, step=1)

    if pid_input:
        processo_info = get_process_detail(pid_input)
        if processo_info:
            st.write(processo_info)
        else:
            st.warning("Processo não encontrado ou acesso negado.")