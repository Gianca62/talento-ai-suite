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
    ["Dashboard", "Gestione Clienti", "Gestione Preventivi", "Analytics", "Reports & Export", "Amministrazione", "Demo"]
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
                    if db.add_cliente(nuovo_cliente):
                        st.success(f"Cliente '{nome}' aggiunto con successo!")
                        st.session_state.clienti = db.get_clienti()
                        st.rerun()
                    else:
                        st.error("Errore nell'aggiungere il cliente")
                else:
                    st.error("Il nome è obbligatorio!")
    
    with tab2:
        st.subheader("Lista Clienti")
        
        # Carica clienti dal database
        st.session_state.clienti = db.get_clienti()
        
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
        
        # Carica clienti dal database
        st.session_state.clienti = db.get_clienti()
        
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
                        if db.add_preventivo(nuovo_preventivo):
                            st.success(f"Preventivo '{numero}' creato con successo!")
                            st.session_state.preventivi = db.get_preventivi()
                            st.rerun()
                        else:
                            st.error("Errore nel creare il preventivo")
                    else:
                        st.error("Numero preventivo e cliente sono obbligatori!")
    
    with tab2:
        st.subheader("Lista Preventivi")
        
        # Carica preventivi dal database
        st.session_state.preventivi = db.get_preventivi()
        
        if st.session_state.preventivi:
            df_preventivi = pd.DataFrame(st.session_state.preventivi)
            st.dataframe(df_preventivi, use_container_width=True)
        else:
            st.info("Nessun preventivo creato. Crea il primo preventivo!")

# ANALYTICS
elif menu == "Analytics":
    st.header("📈 Analytics Avanzate")
    
    preventivi = db.get_preventivi()
    spese = db.get_spese()
    
    if not preventivi:
        st.info("Carica alcuni preventivi per vedere le analytics!")
    else:
        df_preventivi = pd.DataFrame(preventivi)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Preventivi per stato
            stati_count = df_preventivi['stato'].value_counts()
            fig_stati = px.pie(values=stati_count.values, names=stati_count.index,
                              title="Distribuzione Preventivi per Stato")
            st.plotly_chart(fig_stati, use_container_width=True)
        
        with col2:
            # Valore per cliente
            if 'totale' in df_preventivi.columns:
                valore_cliente = df_preventivi.groupby('cliente')['totale'].sum().reset_index()
                fig_clienti = px.bar(valore_cliente, x='cliente', y='totale',
                                   title="Valore Totale per Cliente")
                st.plotly_chart(fig_clienti, use_container_width=True)

# REPORTS & EXPORT  
elif menu == "Reports & Export":
    st.header("📊 Reports & Export")
    
    preventivi = db.get_preventivi()
    spese = db.get_spese()
    
    if preventivi or spese:
        col1, col2, col3 = st.columns(3)
        
        # Calcola metriche
        if preventivi:
            df_prev = pd.DataFrame(preventivi)
            entrate = df_prev[df_prev['stato'] == 'ACCETTATO']['totale'].sum() if 'totale' in df_prev.columns else 0
            pipeline = df_prev[df_prev['stato'].isin(['BOZZA', 'INVIATO'])]['totale'].sum() if 'totale' in df_prev.columns else 0
        else:
            entrate = 0
            pipeline = 0
            
        if spese:
            df_spese = pd.DataFrame(spese)
            uscite = df_spese['importo'].sum()
        else:
            uscite = 0
        
        with col1:
            st.metric("Entrate Confermate", f"€{entrate:,.2f}")
        with col2:
            st.metric("Pipeline", f"€{pipeline:,.2f}") 
        with col3:
            st.metric("Spese Totali", f"€{uscite:,.2f}")
        
        # Report riassuntivo
        st.subheader("Report Finanziario")
        utile = entrate - uscite
        st.metric("Utile Stimato", f"€{utile:,.2f}", delta=f"{(utile/entrate*100):.1f}%" if entrate > 0 else "0%")
        
        if st.button("Esporta Report (CSV)"):
            st.success("Funzione export - in una versione completa genererebbe un file CSV")
    else:
        st.info("Aggiungi alcuni dati per generare reports!")

# AMMINISTRAZIONE
elif menu == "Amministrazione":
    st.header("🏢 Amministrazione")
    
    # Tabs per le diverse funzioni amministrative
    tab1, tab2, tab3 = st.tabs(["💼 Nota Spese", "⏰ Scadenze", "📅 Calendario"])
    
    with tab1:
        st.subheader("Gestione Nota Spese")
        
        if st.button("Aggiungi Spesa Test"):
            spesa_test = {
                "data": "28/12/2024",
                "categoria": "Ufficio", 
                "descrizione": "Test spesa",
                "importo": 50.0,
                "progetto": "Generale",
                "detraibile": True,
                "ricevuta": "Si"
            }
            if db.add_spesa(spesa_test):
                st.success("Spesa test aggiunta!")
            else:
                st.error("Errore")
        
        spese = db.get_spese()
        if spese:
            df_spese = pd.DataFrame(spese)
            st.dataframe(df_spese)
            
            if len(df_spese) > 0:
                totale = df_spese['importo'].sum()
                st.metric("Totale Spese", f"€{totale:.2f}")
        else:
            st.info("Nessuna spesa registrata")
    
    with tab2:
        st.subheader("Scadenze")
        st.info("Sezione scadenze - in sviluppo")
    
    with tab3:
        st.subheader("Calendario")
        st.info("Sezione calendario - in sviluppo")
        
# DEMO
elif menu == "Demo":
    st.header("🎯 Demo e Test")
    
    st.markdown("### Test Connessione Supabase")
    
    if st.button("Test Connessione"):
        if db.test_connection():
            st.success("Connessione a Supabase funziona!")
        else:
            st.error("Errore connessione")
    
    st.markdown("### Carica Dati Demo")
    
    if st.button("Aggiungi Cliente Demo"):
        cliente_demo = {
            "nome": "Rossi Costruzioni SRL",
            "email": "info@rossicost.it", 
            "telefono": "0421-123456",
            "note": "Cliente di test",
            "data_creazione": "28/12/2024"
        }
        if db.add_cliente(cliente_demo):
            st.success("Cliente demo aggiunto!")
            st.session_state.clienti = db.get_clienti()
        else:
            st.error("Errore nell'aggiungere cliente")
    
    if st.button("Aggiungi Preventivo Demo"):
        if st.session_state.clienti:
            preventivo_demo = {
                "numero": "PREV-001",
                "cliente": "Rossi Costruzioni SRL",
                "note": "Preventivo di test",
                "stato": "BOZZA",
                "data_creazione": "28/12/2024",
                "totale": 1500.0
            }
            if db.add_preventivo(preventivo_demo):
                st.success("Preventivo demo aggiunto!")
                st.session_state.preventivi = db.get_preventivi()
            else:
                st.error("Errore nell'aggiungere preventivo")
        else:
            st.warning("Aggiungi prima un cliente!")
    
    if st.button("Ricarica Dati dal Database"):
        st.session_state.clienti = db.get_clienti()
        st.session_state.preventivi = db.get_preventivi()
        st.success(f"Caricati: {len(st.session_state.clienti)} clienti, {len(st.session_state.preventivi)} preventivi")

# Footer
st.markdown("""
---
**TALENTO AI SUITE** - Versione con Supabase | Creato da Giancarlo Tonon
""")