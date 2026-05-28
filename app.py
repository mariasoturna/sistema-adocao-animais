import streamlit as st
import sqlite3
import os

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Sistema de Adoção", page_icon="🐾")

if not os.path.exists("fotos"):
    os.makedirs("fotos")

# --- BANCO DE DADOS ---
def criar_tabela():
    conn = sqlite3.connect('ong_animais.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            especie TEXT,
            porte TEXT,
            descricao TEXT,
            contato TEXT,
            caminho_foto TEXT
        )
    ''')
    conn.commit()
    conn.close()

criar_tabela()

# --- SIDEBAR (PAINEL DE ESTATÍSTICAS) ---
st.sidebar.title("📊 Painel da ONG")
st.sidebar.markdown("Acompanhe os nossos números:")

# Função para contar os animais no banco de dados
def buscar_estatisticas():
    conn = sqlite3.connect('ong_animais.db')
    cursor = conn.cursor()
    
    # Conta todos os animais
    cursor.execute("SELECT COUNT(*) FROM animais")
    total = cursor.fetchone()[0]
    
    # Conta só os cachorros
    cursor.execute("SELECT COUNT(*) FROM animais WHERE especie='Cachorro'")
    cachorros = cursor.fetchone()[0]
    
    # Conta só os gatos
    cursor.execute("SELECT COUNT(*) FROM animais WHERE especie='Gato'")
    gatos = cursor.fetchone()[0]
    
    conn.close()
    return total, cachorros, gatos

# Recupera os números e cria os "Cards" na barra lateral
total, cachorros, gatos = buscar_estatisticas()

st.sidebar.metric(label="Total de Animais", value=total)
st.sidebar.metric(label="🐶 Cachorros", value=cachorros)
st.sidebar.metric(label="🐱 Gatos", value=gatos)
st.sidebar.divider()
st.sidebar.caption("Desenvolvido para Projeto Acadêmico")

# --- INTERFACE DO SITE ---
st.title("🐾 Sistema de Adoção")

aba_cadastro, aba_lista = st.tabs(["📝 Cadastrar Animal", "🐶 Ver Animais"])

# --- ABA 1: CADASTRO ---
with aba_cadastro:
    st.header("Cadastre um novo focinho")
    
    with st.form("form_cadastro", clear_on_submit=True):
        nome = st.text_input("Nome do animal*")
        especie = st.selectbox("Espécie*", ["Cachorro", "Gato", "Outro"])
        porte = st.selectbox("Porte*", ["Pequeno", "Médio", "Grande"])
        descricao = st.text_area("Descrição (Personalidade, histórico, etc)*")
        contato = st.text_input("Telefone de Contato (WhatsApp)*")
        foto = st.file_uploader("Foto do animal", type=["jpg", "jpeg", "png"])
        
        botao_salvar = st.form_submit_button("Salvar Cadastro")
        
        if botao_salvar:
            if nome and contato and descricao:
                caminho_foto = ""
                if foto is not None:
                    caminho_foto = os.path.join("fotos", foto.name)
                    with open(caminho_foto, "wb") as f:
                        f.write(foto.getbuffer())
                
                conn = sqlite3.connect('ong_animais.db')
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO animais (nome, especie, porte, descricao, contato, caminho_foto) VALUES (?, ?, ?, ?, ?, ?)",
                    (nome, especie, porte, descricao, contato, caminho_foto)
                )
                conn.commit()
                conn.close()
                
                st.success(f"Excelente! {nome} cadastrado com sucesso! (Atualize a página para ver os números subirem na barra lateral).")
            else:
                st.error("Por favor, preencha pelo menos o nome, descrição e contato.")

# --- ABA 2: LISTA DE ANIMAIS (COM FILTROS) ---
with aba_lista:
    st.header("Focinhos disponíveis para adoção")
    
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        filtro_especie = st.selectbox("Filtrar por Espécie", ["Todos", "Cachorro", "Gato", "Outro"])
    with col_filtro2:
        filtro_porte = st.selectbox("Filtrar por Porte", ["Todos", "Pequeno", "Médio", "Grande"])
        
    conn = sqlite3.connect('ong_animais.db')
    cursor = conn.cursor()
    
    query = "SELECT * FROM animais WHERE 1=1"
    parametros = []
    
    if filtro_especie != "Todos":
        query += " AND especie = ?"
        parametros.append(filtro_especie)
        
    if filtro_porte != "Todos":
        query += " AND porte = ?"
        parametros.append(filtro_porte)
        
    cursor.execute(query, parametros)
    animais = cursor.fetchall()
    conn.close()
    
    if animais:
        for animal in animais:
            id_animal, nome, especie, porte, descricao, contato, caminho_foto = animal
            
            with st.container():
                col_foto, col_info = st.columns([1, 2])
                
                with col_foto:
                    if caminho_foto and os.path.exists(caminho_foto):
                        st.image(caminho_foto, use_container_width=True)
                    else:
                        st.info("🐾 Sem fotografia")
                        
                with col_info:
                    st.subheader(nome)
                    st.markdown(f"**Espécie:** {especie}  |  **Porte:** {porte}")
                    st.markdown(f"**Sobre:** {descricao}")
                    st.markdown(f"📞 **Contato:** {contato}")
                
                st.divider()
    else:
        st.warning("Nenhum focinho encontrado com estas características. 😔")