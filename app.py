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

def buscar_estatisticas():
    conn = sqlite3.connect('ong_animais.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM animais")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM animais WHERE especie='Cachorro'")
    cachorros = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM animais WHERE especie='Gato'")
    gatos = cursor.fetchone()[0]
    
    conn.close()
    return total, cachorros, gatos

total, cachorros, gatos = buscar_estatisticas()

st.sidebar.metric(label="Total de Animais", value=total)
st.sidebar.metric(label="🐶 Cachorros", value=cachorros)
st.sidebar.metric(label="🐱 Gatos", value=gatos)
st.sidebar.divider()
st.sidebar.caption("Desenvolvido para Projeto Acadêmico")

# --- INTERFACE DO SITE ---
st.title("🐾 Sistema de Adoção")

# Adicionamos a terceira aba aqui!
aba_cadastro, aba_lista, aba_gerenciar = st.tabs(["📝 Cadastrar Animal", "🐶 Ver Animais", "⚙️ Gerenciar"])

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
                
                st.success(f"Excelente! {nome} cadastrado com sucesso! (Atualize a página).")
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

# --- ABA 3: GERENCIAR (EDITAR E EXCLUIR) ---
with aba_gerenciar:
    st.header("Gerenciar Animais Cadastrados")
    
    conn = sqlite3.connect('ong_animais.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM animais")
    lista_animais = cursor.fetchall()
    conn.close()
    
    if lista_animais:
        # Cria um dicionário para ligar o nome do animal ao seu ID no banco de dados
        opcoes_animais = {f"{id_animal} - {nome}": id_animal for id_animal, nome in lista_animais}
        
        animal_selecionado = st.selectbox("Selecione o animal que deseja gerenciar:", list(opcoes_animais.keys()))
        id_selecionado = opcoes_animais[animal_selecionado]
        
        # Busca todas as informações do animal selecionado
        conn = sqlite3.connect('ong_animais.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM animais WHERE id = ?", (id_selecionado,))
        animal_dados = cursor.fetchone()
        conn.close()
        
        id_animal, nome, especie, porte, descricao, contato, caminho_foto = animal_dados
        
        st.divider()
        acao = st.radio("O que você deseja fazer com este cadastro?", ["Editar Informações", "Excluir Cadastro"])
        
        if acao == "Editar Informações":
            with st.form("form_editar"):
                st.markdown(f"**Editando:** {nome}")
                novo_nome = st.text_input("Nome", value=nome)
                nova_especie = st.selectbox("Espécie", ["Cachorro", "Gato", "Outro"], index=["Cachorro", "Gato", "Outro"].index(especie))
                novo_porte = st.selectbox("Porte", ["Pequeno", "Médio", "Grande"], index=["Pequeno", "Médio", "Grande"].index(porte))
                nova_descricao = st.text_area("Descrição", value=descricao)
                novo_contato = st.text_input("Telefone de Contato", value=contato)
                
                if st.form_submit_button("Salvar Alterações"):
                    conn = sqlite3.connect('ong_animais.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE animais 
                        SET nome=?, especie=?, porte=?, descricao=?, contato=? 
                        WHERE id=?
                    ''', (novo_nome, nova_especie, novo_porte, nova_descricao, novo_contato, id_selecionado))
                    conn.commit()
                    conn.close()
                    st.success("Cadastro atualizado com sucesso! (Atualize a página apertando F5)")
                    
        elif acao == "Excluir Cadastro":
            st.warning(f"Tem certeza que deseja excluir o cadastro de **{nome}**? Esta ação não pode ser desfeita.")
            if st.button("Sim, Excluir"):
                conn = sqlite3.connect('ong_animais.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM animais WHERE id=?", (id_selecionado,))
                conn.commit()
                conn.close()
                
                # Remove a foto da pasta do computador, se ela existir
                if caminho_foto and os.path.exists(caminho_foto):
                    try:
                        os.remove(caminho_foto)
                    except:
                        pass
                        
                st.success("Cadastro excluído com sucesso! (Atualize a página apertando F5)")
    else:
        st.info("Não há animais cadastrados no momento para gerenciar.")