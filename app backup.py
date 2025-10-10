import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from supabase_backend import SupabaseManager

# Configurazione pagina
st.set_page_config(
    page_title="TALENTO AI Suite", 
    page_icon="⭐", 
    layout="wide"
)

# Inizializza Supabase
@st.cache_resource
def init_supabase():
    return SupabaseManager()

db = init_supabase()

# Inizializza session state
if 'clienti' not in st.session_state:
    st.session_state.clienti = []
if 'preventivi' not in st.session_state:
    st.session_state.preventivi = []
if 'spese' not in st.session_state:
    st.session_state.spese = []

# Header principale
st.markdown("""
<div style="background: linear-gradient(135deg, #FFD700, #FFA500); padding: 2rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;">
    <h1 style="color: #2c3e50; margin: 0;">⭐ TALENTO AI SUITE ⭐</h1>
    <p style="color: #2c3e50; font-style: italic; margin: 0;">"Non nascondere il tuo talento sotto terra"</p>
</div>
""", unsafe_allow_html=True)

# Sidebar per navigazione
st.sidebar.title("📋 Menu Principale")
menu = st.sidebar.selectbox(
    "Scegli sezione:",
    ["Dashboard", "Gestione Clienti", "Gestione Preventivi", "Demo"]
)

# Funzioni helper
def calcola_statistiche():
    total_preventivi = len(st.session_state.preventivi)
    total_clienti = len(st.session_state.clienti)
    
    if st.session_state.preventivi:
        valore_accettato = sum(p['totale'] for p in st.session_state.preventivi if p['stato'] == 'ACCETTATO')
        preventivi_inviati = len([p for p in st.session_state.preventivi if p['stato'] in ['INVIATO', 'ACCETTATO', 'RIFIUTATO']])
        preventivi_accettati = len([p for p in st.session_state.preventivi if p['stato'] == 'ACCETTATO'])
        tasso_successo = (preventivi_accettati / preventivi_inviati * 100) if preventivi_inviati > 0 else 0
    else:
        valore_accettato = 0
        tasso_successo = 0
    
    return total_preventivi, total_clienti, valore_accettato, tasso_successo

def carica_dati_demo():
    # Clienti demo
    st.session_state.clienti = [
        {
            "nome": "Rossi Costruzioni SRL",
            "email": "info@rossicost.it",
            "telefono": "0421-123456",
            "note": "Cliente storico, sempre puntuale nei pagamenti",
            "data_creazione": "15/12/2024"
        },
        {
            "nome": "Studio Legale Bianchi",
            "email": "avv.bianchi@legal.it",
            "telefono": "339-987654",
            "note": "Specialisti in diritto commerciale",
            "data_creazione": "10/12/2024"
        }
    ]
    
    # Preventivi demo
    st.session_state.preventivi = [
        {
            "numero": "PREV-001",
            "cliente": "Rossi Costruzioni SRL",
            "note": "Ristrutturazione bagno completa",
            "stato": "ACCETTATO",
            "data_creazione": "18/12/2024",
            "totale": 1970
        },
        {
            "numero": "OFF-002",
            "cliente": "Studio Legale Bianchi",
            "note": "Consulenza privacy per studio legale",
            "stato": "INVIATO",
            "data_creazione": "20/12/2024",
            "totale": 1540
        }
    ]

# DASHBOARD
if menu == "Dashboard":
    st.header("📊 Dashboard Principale")
    
    # Calcola statistiche
    total_preventivi, total_clienti, valore_accettato, tasso_successo = calcola_statistiche()
    
    # Metriche principali
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Preventivi Totali", total_preventivi)
    
    with col2:
        st.metric("Clienti Attivi", total_clienti)
    
    with col3:
        st.metric("Valore Accettato", f"€{valore_accettato:,.0f}")
    
    with col4:
        st.metric("Tasso Successo", f"{tasso_successo:.0f}%")
    
    # Grafico se ci sono dati
    if st.session_state.preventivi:
        st.subheader("Preventivi per Stato")
        df_stati = pd.DataFrame(st.session_state.preventivi)
        fig_stati = px.pie(df_stati, names='stato', title="Distribuzione Stati")
        st.plotly_chart(fig_stati, use_container_width=True)

# GESTIONE CLIENTI
elif menu == "Gestione Clienti":
    st.header("👥 Gestione Clienti")
    
    # Tabs per organizzare
    tab1, tab2 = st.tabs(["Aggiungi Cliente", "Lista Clienti"])
    
    with tab1:
        st.subheader("Nuovo Cliente")
        
        with st.form("form_cliente"):
            nome = st.text_input("Nome/Ragione Sociale *")
            email = st.text_input("Email")
            telefono = st.text_input("Telefono")
            note = st.text_area("Note Personali")
            
            if st.form_submit_button("Aggiungi Cliente", type="primary"):
                if nome:
                    nuovo_cliente = {
                        "nome": nome,
                        "email": email,
                        "telefono": telefono,
                        "note": note,
                        "data_creazione": datetime.now().strftime("%d/%m/%Y")
                    }
                    st.session_state.clienti.append(nuovo_cliente)
                    st.success(f"Cliente '{nome}' aggiunto con successo!")
                    st.rerun()
                else:
                    st.error("Il nome è obbligatorio!")
    
    with tab2:
        st.subheader("Lista Clienti")
        
        if st.session_state.clienti:
            df_clienti = pd.DataFrame(st.session_state.clienti)
            st.dataframe(df_clienti, use_container_width=True)
        else:
            st.info("Nessun cliente registrato. Aggiungi il primo cliente!")

# GESTIONE PREVENTIVI
elif menu == "Gestione Preventivi":
    st.header("📄 Gestione Preventivi")
    
    tab1, tab2 = st.tabs(["Crea Preventivo", "Lista Preventivi"])
    
    with tab1:
        st.subheader("Nuovo Preventivo")
        
        if not st.session_state.clienti:
            st.warning("Prima devi aggiungere almeno un cliente!")
        else:
            with st.form("form_preventivo"):
                numero = st.text_input("Numero Preventivo *")
                cliente = st.selectbox("Cliente *", [c["nome"] for c in st.session_state.clienti])
                note = st.text_area("Note per Cliente")
                totale = st.number_input("Valore Totale €", min_value=0.0, step=0.01)
                
                if st.form_submit_button("Crea Preventivo", type="primary"):
                    if numero and cliente:
                        nuovo_preventivo = {
                            "numero": numero,
                            "cliente": cliente,
                            "note": note,
                            "stato": "BOZZA",
                            "data_creazione": datetime.now().strftime("%d/%m/%Y"),
                            "totale": totale
                        }
                        st.session_state.preventivi.append(nuovo_preventivo)
                        st.success(f"Preventivo '{numero}' creato con successo!")
                        st.rerun()
                    else:
                        st.error("Numero preventivo e cliente sono obbligatori!")
    
    with tab2:
        st.subheader("Lista Preventivi")
        
        if st.session_state.preventivi:
            df_preventivi = pd.DataFrame(st.session_state.preventivi)
            st.dataframe(df_preventivi, use_container_width=True)
        else:
            st.info("Nessun preventivo creato. Crea il primo preventivo!")

# DEMO
elif menu == "Demo":
    st.header("🎯 Demo e Test")
    
    st.markdown("""
  ### Carica Dati Demo
    
    Clicca il pulsante per caricare dati di esempio e testare le funzionalità:
    - 2 clienti di esempio
    - 2 preventivi con stati diversi
    """)
    
 if st.button("🎮 Carica Dati Demo", type="primary"):
    try:
        if db.test_connection():
            st.success("Connessione a Supabase riuscita!")
            
            # Aggiungi clienti demo direttamente
            cliente1 = {
                "nome": "Rossi Costruzioni SRL",
                "email": "info@rossicost.it",
                "telefono": "0421-123456",
                "note": "Cliente storico",
                "data_creazione": "15/12/2024"
            }
            db.add_cliente(cliente1)
            
            cliente2 = {
                "nome": "Studio Legale Bianchi", 
                "email": "avv.bianchi@legal.it",
                "telefono": "339-987654",
                "note": "Specialisti diritto commerciale",
                "data_creazione": "10/12/2024"
            }
            db.add_cliente(cliente2)
            
            # Ricarica dati
            st.session_state.clienti = db.get_clienti()
            st.session_state.preventivi = db.get_preventivi()
            
            st.success("Dati demo caricati!")
            st.balloons()
            st.rerun()
        else:
            st.error("Errore connessione Supabase!")
    except Exception as e:
        st.error(f"Errore: {e}")

# Footer
st.markdown("""
---
**TALENTO AI SUITE** - Versione Base | Creato da Giancarlo Tonon
""")