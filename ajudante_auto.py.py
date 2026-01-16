import streamlit as st
import requests
import unicodedata
import os

st.set_page_config(page_title="Termo Pro Solver", page_icon="🎯")

def remover_acentos(txt):
    return ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')

def filtrar(lista, tentativa, resultado):
    nova_lista = []
    for palavra in lista:
        manter = True
        for i in range(5):
            l_t = tentativa[i]; res = resultado[i]
            if res == 'v' and palavra[i] != l_t: manter = False; break
            elif res == 'a' and (l_t not in palavra or palavra[i] == l_t): manter = False; break
            elif res == 'c' and l_t in palavra:
                if tentativa.count(l_t) == 1: manter = False; break
        if manter: nova_lista.append(palavra)
    return nova_lista

def carregar_dicionario():
    url = "https://raw.githubusercontent.com/pythonprobr/palavras/master/palavras.txt"
    extras_fixos = ["podam", "fuzil", "trens", "bicho", "golfe", "ambos"]
    
    # AJUSTE AQUI: Procura o arquivo na mesma pasta do script
    caminho_pasta = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(caminho_pasta, "minhas_palavras.txt")
    
    extras_arquivo = []
    if os.path.exists(caminho_completo):
        try:
            with open(caminho_completo, "r", encoding="utf-8") as f:
                extras_arquivo = [remover_acentos(l.strip().lower()) for l in f if len(l.strip()) == 5]
        except: pass
    try:
        resposta = requests.get(url)
        lista = [remover_acentos(p.lower()) for p in resposta.text.split() if len(p) == 5]
        return sorted(list(set(lista + extras_fixos + extras_arquivo)))
    except: 
        return sorted(list(set(extras_fixos + extras_arquivo)))

def limpar_cores():
    for key in list(st.session_state.keys()):
        if key.startswith("cor_"):
            del st.session_state[key]

# --- INICIALIZAÇÃO SIMPLES ---
if 'lista_mestra' not in st.session_state:
    st.session_state.lista_mestra = carregar_dicionario()
    st.session_state.filtradas = st.session_state.lista_mestra.copy()
    st.session_state.historico = []
    st.session_state.input_palavra = ""

st.title("🎯 Termo Pro Solver")

# Botões de Controle
c1, c2 = st.columns(2)
if c1.button("♻️ NOVO JOGO", use_container_width=True, type="primary"):
    # Atualiza a lista mestra lendo o arquivo de novo
    st.session_state.lista_mestra = carregar_dicionario()
    st.session_state.filtradas = st.session_state.lista_mestra.copy()
    st.session_state.historico = []
    st.session_state.input_palavra = ""
    limpar_cores()
    st.rerun()

if c2.button("↩️ APAGAR ÚLTIMA", use_container_width=True):
    if st.session_state.historico:
        st.session_state.historico.pop()
        nova_lista = st.session_state.lista_mestra.copy()
        for item in st.session_state.historico:
            nova_lista = filtrar(nova_lista, item['p'], item['r'])
        st.session_state.filtradas = nova_lista
        st.rerun()

st.write("### ⚡ Atalhos Rápidos")
col1, col2, col3, col4 = st.columns(4)
if col1.button("PODAM", use_container_width=True): st.session_state.input_palavra = "podam"; limpar_cores(); st.rerun()
if col2.button("FUZIL", use_container_width=True): st.session_state.input_palavra = "fuzil"; limpar_cores(); st.rerun()
if col3.button("TRENS", use_container_width=True): st.session_state.input_palavra = "trens"; limpar_cores(); st.rerun()
if col4.button("BICHO", use_container_width=True): st.session_state.input_palavra = "bicho"; limpar_cores(); st.rerun()

st.divider()

tentativa = st.text_input("Qual palavra usaste?", value=st.session_state.input_palavra, max_chars=5).lower()

if len(tentativa) == 5:
    st.write("Cores:")
    cols = st.columns(5)
    res_atual = ""
    icones = {0: "⬛", 1: "🟨", 2: "🟩"}
    for i in range(5):
        key = f"cor_{i}"
        if key not in st.session_state: st.session_state[key] = 0
        if cols[i].button(f"{icones[st.session_state[key]]} {tentativa[i].upper()}", key=f"b_{i}"):
            st.session_state[key] = (st.session_state[key] + 1) % 3
            st.rerun()
        res_atual += "c" if st.session_state[key] == 0 else "a" if st.session_state[key] == 1 else "v"

    if st.button("🚀 FILTRAR AGORA", use_container_width=True):
        st.session_state.filtradas = filtrar(st.session_state.filtradas, tentativa, res_atual)
        visual = "".join([icones[st.session_state[f"cor_{j}"]] for j in range(5)])
        st.session_state.historico.append({'txt': f"{visual} {tentativa.upper()}", 'p': tentativa, 'r': res_atual})
        st.session_state.input_palavra = ""
        limpar_cores()
        st.rerun()

if st.session_state.historico:
    with st.expander("📜 Histórico", expanded=True):
        for item in st.session_state.historico:
            st.write(item['txt'])

st.divider()
st.subheader(f"Opções: {len(st.session_state.filtradas)}")
st.write(", ".join([p.upper() for p in st.session_state.filtradas[:100]]))