import streamlit as st # type: ignore
import sqlite3
import pandas as pd # type: ignore
import random

# Funções do Banco de Dados
def conectar():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    criar_tabelas(conn, cursor)
    return conn, cursor


def criar_tabelas(conn, cursor):
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            email TEXT,
            senha TEXT)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS filmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT UNIQUE,
            categoria TEXT)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            filme_id INTEGER,
            avaliacao INTEGER,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(filme_id) REFERENCES filmes(id))"""
    )

    carregar_filmes_iniciais(conn, cursor)


def carregar_filmes_iniciais(conn, cursor):
    try:
        filmes_df = pd.read_csv("movies (1).csv")
        for _, row in filmes_df.iterrows():
            titulo = row["title"]
            categoria = row["genres"]
            cursor.execute(
                "INSERT OR IGNORE INTO filmes (titulo, categoria) VALUES (?, ?)",
                (titulo, categoria),
            )
        conn.commit()
    except FileNotFoundError:
        st.warning("Arquivo movies (1).csv não encontrado. Nenhum filme inicial foi carregado.")
    except KeyError as e:
        st.error(f"Coluna não encontrada no CSV: {e}")
        st.stop()


def adicionar_usuario(nome, email, senha):
    conn, cursor = conectar()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
        (nome, email, senha),
    )
    conn.commit()
    conn.close()


def verificar_usuario(nome, senha):
    conn, cursor = conectar()
    cursor.execute("SELECT * FROM usuarios WHERE nome = ? AND senha = ?", (nome, senha))
    user = cursor.fetchone()
    conn.close()
    return user


def adicionar_filme(titulo, categoria="Desconhecida"):
    conn, cursor = conectar()
    cursor.execute(
        "INSERT OR IGNORE INTO filmes (titulo, categoria) VALUES (?, ?)",
        (titulo, categoria),
    )
    cursor.execute("SELECT id FROM filmes WHERE titulo = ?", (titulo,))
    filme_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return filme_id


def adicionar_historico(usuario_id, filme_id, avaliacao=None):
    conn, cursor = conectar()
    cursor.execute(
        "INSERT INTO historico (usuario_id, filme_id, avaliacao) VALUES (?, ?, ?)",
        (usuario_id, filme_id, avaliacao),
    )
    conn.commit()
    conn.close()


def obter_historico(usuario_id):
    conn, cursor = conectar()
    cursor.execute(
        "SELECT titulo, avaliacao FROM filmes JOIN historico ON filmes.id = historico.filme_id WHERE historico.usuario_id = ?",
        (usuario_id,),
    )
    historico = cursor.fetchall()
    conn.close()
    return historico


def recomendar_filmes(usuario_id):
    conn, cursor = conectar()
    cursor.execute(
        """
        SELECT titulo FROM filmes 
        WHERE id NOT IN (SELECT filme_id FROM historico WHERE usuario_id = ?)
        """,
        (usuario_id,),
    )
    filmes_disponiveis = [filme[0] for filme in cursor.fetchall()]
    conn.close()
    return random.sample(filmes_disponiveis, min(5, len(filmes_disponiveis))) if filmes_disponiveis else ["Nenhuma recomendação disponível no momento."]

# Interface do Streamlit
st.sidebar.title("Sistema de Recomendações de Filmes")
opcao = st.sidebar.selectbox(
    "Escolha uma página",
    ["Autenticação", "Cadastro", "Perfil", "Histórico de Filmes", "Recomendação", "Logout"],
)

# Página de Cadastro
if opcao == "Cadastro":
    st.title("Cadastro")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        try:
            adicionar_usuario(nome, email, senha)
            st.success("Usuário cadastrado com sucesso!")
        except sqlite3.IntegrityError:
            st.error("O nome de usuário já está cadastrado.")

# Página de Autenticação
elif opcao == "Autenticação":
    st.title("Autenticação")
    nome = st.text_input("Nome")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        usuario = verificar_usuario(nome, senha)
        if usuario:
            st.session_state["usuario"] = usuario
            st.success("Login bem-sucedido!")
        else:
            st.error("Credenciais inválidas")

# Página de Perfil
elif opcao == "Perfil":
    st.title("Perfil do Usuário")
    if "usuario" in st.session_state:
        usuario = st.session_state["usuario"]
        st.write(f"Nome: {usuario[1]}")
        st.write(f"Email: {usuario[2]}")
    else:
        st.warning("Faça login para acessar seu perfil.")

# Página de Histórico de Filmes
elif opcao == "Histórico de Filmes":
    st.title("Filmes Assistidos")
    if "usuario" in st.session_state:
        filme = st.text_input("Digite o nome do filme que você assistiu:")
        avaliacao = st.slider("Avalie o filme", 1, 5)
        if st.button("Adicionar ao Histórico"):
            filme_id = adicionar_filme(filme)
            adicionar_historico(st.session_state["usuario"][0], filme_id, avaliacao)
            st.success(f"{filme} adicionado ao seu histórico com avaliação {avaliacao}.")
        historico = obter_historico(st.session_state["usuario"][0])
        st.write("Seu histórico de filmes:")
        for titulo, avaliacao in historico:
            st.write(f"- {titulo} (Avaliação: {avaliacao})")
    else:
        st.warning("Faça login para acessar seu histórico de filmes.")

# Página de Recomendações
elif opcao == "Recomendação":
    st.title("Recomendações Personalizadas")
    if "usuario" in st.session_state:
        usuario_id = st.session_state["usuario"][0]
        recomendacoes = recomendar_filmes(usuario_id)
        st.write("Aqui estão algumas recomendações para você:")
        for filme in recomendacoes:
            st.write(f"- {filme}")
    else:
        st.warning("Faça login para ver recomendações")

# Página de Logout
elif opcao == "Logout":
    if "usuario" in st.session_state:
        del st.session_state["usuario"]
        st.success("Logout realizado com sucesso!")
    else:
        st.warning("Você já está desconectado.")