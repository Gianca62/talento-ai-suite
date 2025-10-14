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
        
        # Sottotabs per organizzare meglio
        subtab1, subtab2 = st.tabs(["Aggiungi Spesa", "Lista Spese"])
        
        with subtab1:
            st.subheader("Nuova Spesa")
            
            with st.form("form_spesa"):
                col1, col2 = st.columns(2)
                
                with col1:
                    data_spesa = st.date_input("Data Spesa", value=datetime.now())
                    categoria = st.selectbox("Categoria", 
                                           ["Trasporti", "Materiali", "Formazione", "Ufficio", 
                                            "Software", "Hardware", "Consulenze", "Marketing", "Altro"])
                    importo = st.number_input("Importo €", min_value=0.0, step=0.01)
                
                with col2:
                    progetti_disponibili = ["Generale"]
                    preventivi = db.get_preventivi()
                    if preventivi:
                        progetti_disponibili.extend([p["numero"] for p in preventivi])
                    
                    progetto = st.selectbox("Progetto/Preventivo", progetti_disponibili)
                    detraibile = st.checkbox("Detraibile/Deducibile", value=True)
                    ricevuta = st.selectbox("Ricevuta", ["Si", "No"])
                
                descrizione = st.text_area("Descrizione Spesa")
                
                if st.form_submit_button("Aggiungi Spesa", type="primary"):
                    if importo > 0 and descrizione:
                        nuova_spesa = {
                            "data": data_spesa.strftime("%d/%m/%Y"),
                            "categoria": categoria,
                            "descrizione": descrizione,
                            "importo": importo,
                            "progetto": progetto,
                            "detraibile": detraibile,
                            "ricevuta": ricevuta
                        }
                        if db.add_spesa(nuova_spesa):
                            st.success(f"Spesa di €{importo:.2f} aggiunta con successo!")
                            st.rerun()
                        else:
                            st.error("Errore nell'aggiungere la spesa")
                    else:
                        st.error("Importo e descrizione sono obbligatori!")
        
        with subtab2:
            st.subheader("Lista Spese")
            
            spese = db.get_spese()
            if spese:
                df_spese = pd.DataFrame(spese)
                
                # Metriche principali
                col1, col2, col3 = st.columns(3)
                totale_spese = df_spese['importo'].sum()
                spese_detraibili = df_spese[df_spese['detraibile'] == True]['importo'].sum()
                num_spese = len(df_spese)
                
                with col1:
                    st.metric("Totale Spese", f"€{totale_spese:.2f}")
                with col2:
                    st.metric("Spese Detraibili", f"€{spese_detraibili:.2f}")
                with col3:
                    st.metric("Numero Spese", num_spese)
                
                # Tabella
                st.subheader("Dettaglio Spese")
                st.dataframe(df_spese, use_container_width=True)
                
                # Grafici
                col1, col2 = st.columns(2)
                
                with col1:
                    spese_categoria = df_spese.groupby('categoria')['importo'].sum().reset_index()
                    fig_cat = px.pie(spese_categoria, values='importo', names='categoria', 
                                   title="Spese per Categoria")
                    st.plotly_chart(fig_cat, use_container_width=True)
                
                with col2:
                    spese_progetto = df_spese.groupby('progetto')['importo'].sum().reset_index()
                    fig_proj = px.bar(spese_progetto, x='progetto', y='importo',
                                    title="Spese per Progetto")
                    st.plotly_chart(fig_proj, use_container_width=True)
            else:
                st.info("Nessuna spesa registrata. Aggiungi la prima spesa!")
    
    with tab2:
        st.subheader("Scadenze & Promemoria")
        
        subtab1, subtab2 = st.tabs(["Aggiungi Scadenza", "Lista Scadenze"])
        
        with subtab1:
            st.subheader("Nuova Scadenza")
            
            with st.form("form_scadenza"):
                col1, col2 = st.columns(2)
                
                with col1:
                    titolo = st.text_input("Titolo Scadenza *")
                    data_scadenza = st.date_input("Data Scadenza", value=datetime.now())
                    tipo_scadenza = st.selectbox("Tipo", 
                                               ["Preventivo", "Pagamento", "Contratto", 
                                                "Certificazione", "Rinnovo", "Appuntamento", "Altro"])
                
                with col2:
                    clienti = db.get_clienti()
                    clienti_disponibili = ["Nessuno"]
                    if clienti:
                        clienti_disponibili.extend([c["nome"] for c in clienti])
                    cliente_collegato = st.selectbox("Cliente Collegato", clienti_disponibili)
                    
                    preventivi = db.get_preventivi()
                    preventivi_disponibili = ["Nessuno"]
                    if preventivi:
                        preventivi_disponibili.extend([p["numero"] for p in preventivi])
                    preventivo_collegato = st.selectbox("Preventivo Collegato", preventivi_disponibili)
                    
                    priorita = st.selectbox("Priorità", ["Alta", "Media", "Bassa"])
                
                descrizione = st.text_area("Descrizione/Note")
                importo = st.number_input("Importo (se applicabile) €", min_value=0.0, step=0.01)
                
                if st.form_submit_button("Aggiungi Scadenza", type="primary"):
                    if titolo:
                        nuova_scadenza = {
                            "titolo": titolo,
                            "data": data_scadenza.strftime("%d/%m/%Y"),
                            "tipo": tipo_scadenza,
                            "cliente": cliente_collegato if cliente_collegato != "Nessuno" else "",
                            "preventivo": preventivo_collegato if preventivo_collegato != "Nessuno" else "",
                            "priorita": priorita,
                            "descrizione": descrizione,
                            "importo": importo,
                            "stato": "Attiva"
                        }
                        if db.add_scadenza(nuova_scadenza):
                            st.success(f"Scadenza '{titolo}' aggiunta con successo!")
                            st.rerun()
                        else:
                            st.error("Errore nell'aggiungere la scadenza")
                    else:
                        st.error("Il titolo è obbligatorio!")
        
        with subtab2:
            st.subheader("Lista Scadenze")
            
            scadenze = db.get_scadenze()
            if scadenze:
                # Calcola statistiche
                scadute = urgenti = prossime = future = 0
                
                for scadenza in scadenze:
                    try:
                        data_scad = datetime.strptime(scadenza["data"], "%d/%m/%Y").date()
                        giorni = (data_scad - datetime.now().date()).days
                        
                        if giorni < 0:
                            scadute += 1
                        elif giorni <= 3:
                            urgenti += 1
                        elif giorni <= 7:
                            prossime += 1
                        else:
                            future += 1
                    except:
                        continue
                
                # Dashboard scadenze
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🔴 Scadute", scadute)
                with col2:
                    st.metric("🟠 Urgenti (≤3gg)", urgenti)
                with col3:
                    st.metric("🟡 Prossime (4-7gg)", prossime)
                with col4:
                    st.metric("🟢 Future (>7gg)", future)
                
                # Lista scadenze
                st.subheader("Dettaglio Scadenze")
                for scadenza in scadenze:
                    try:
                        data_scad = datetime.strptime(scadenza["data"], "%d/%m/%Y").date()
                        giorni = (data_scad - datetime.now().date()).days
                        
                        if giorni < 0:
                            color = "🔴"
                            status = "SCADUTA"
                        elif giorni <= 3:
                            color = "🟠"
                            status = "URGENTE"
                        elif giorni <= 7:
                            color = "🟡"
                            status = "ATTENZIONE"
                        else:
                            color = "🟢"
                            status = "OK"
                        
                        with st.expander(f"{color} {scadenza['titolo']} - {status} ({giorni} giorni)"):
                            st.write(f"**Data:** {scadenza['data']}")
                            st.write(f"**Tipo:** {scadenza['tipo']}")
                            st.write(f"**Priorità:** {scadenza['priorita']}")
                            if scadenza['cliente']:
                                st.write(f"**Cliente:** {scadenza['cliente']}")
                            if scadenza['preventivo']:
                                st.write(f"**Preventivo:** {scadenza['preventivo']}")
                            if scadenza['importo'] > 0:
                                st.write(f"**Importo:** €{scadenza['importo']:.2f}")
                            if scadenza['descrizione']:
                                st.write(f"**Note:** {scadenza['descrizione']}")
                    except:
                        st.write(f"Errore: {scadenza['titolo']}")
            else:
                st.info("Nessuna scadenza registrata. Aggiungi la prima scadenza!")
    
    with tab3:
        st.subheader("📅 Calendario Lavori")
        
        subtab1, subtab2 = st.tabs(["Aggiungi Evento", "Vista Eventi"])
        
        with subtab1:
            st.subheader("Nuovo Evento Calendario")
            
            with st.form("form_evento"):
                col1, col2 = st.columns(2)
                
                with col1:
                    titolo_evento = st.text_input("Titolo Evento *")
                    data_evento = st.date_input("Data Evento", value=datetime.now())
                    ora_inizio = st.time_input("Ora Inizio", value=datetime.now().time())
                    ora_fine = st.time_input("Ora Fine", value=datetime.now().time())
                
                with col2:
                    tipo_evento = st.selectbox("Tipo Evento", 
                                             ["Appuntamento", "Sopralluogo", "Consegna", 
                                              "Riunione", "Deadline", "Formazione", "Altro"])
                    
                    clienti = db.get_clienti()
                    clienti_disponibili = ["Nessuno"]
                    if clienti:
                        clienti_disponibili.extend([c["nome"] for c in clienti])
                    cliente_evento = st.selectbox("Cliente Collegato", clienti_disponibili)
                    
                    preventivi = db.get_preventivi()
                    preventivi_disponibili = ["Nessuno"]
                    if preventivi:
                        preventivi_disponibili.extend([p["numero"] for p in preventivi])
                    preventivo_evento = st.selectbox("Preventivo Collegato", preventivi_disponibili)
                    
                    priorita_evento = st.selectbox("Priorità", ["Alta", "Media", "Bassa"])
                
                luogo = st.text_input("Luogo/Indirizzo")
                note_evento = st.text_area("Note/Descrizione")
                
                if st.form_submit_button("Aggiungi Evento", type="primary"):
                    if titolo_evento:
                        nuovo_evento = {
                            "titolo": titolo_evento,
                            "data": data_evento.strftime("%d/%m/%Y"),
                            "ora_inizio": ora_inizio.strftime("%H:%M"),
                            "ora_fine": ora_fine.strftime("%H:%M"),
                            "tipo": tipo_evento,
                            "cliente": cliente_evento if cliente_evento != "Nessuno" else "",
                            "preventivo": preventivo_evento if preventivo_evento != "Nessuno" else "",
                            "priorita": priorita_evento,
                            "luogo": luogo,
                            "note": note_evento,
                            "stato": "Programmato"
                        }
                        if db.add_evento_calendario(nuovo_evento):
                            st.success(f"Evento '{titolo_evento}' aggiunto al calendario!")
                            st.rerun()
                        else:
                            st.error("Errore nell'aggiungere l'evento")
                    else:
                        st.error("Il titolo dell'evento è obbligatorio!")
        
        with subtab2:
            st.subheader("Lista Eventi")
            
            eventi = db.get_eventi_calendario()
            if eventi:
                # Ordina eventi per data
                try:
                    eventi_ordinati = sorted(eventi, 
                                           key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"))
                    
                    for evento in eventi_ordinati:
                        # Colore priorità
                        if evento["priorita"] == "Alta":
                            priority_color = "🔴"
                        elif evento["priorita"] == "Media":
                            priority_color = "🟡"
                        else:
                            priority_color = "🟢"
                        
                        with st.expander(f"{priority_color} {evento['data']} - {evento['titolo']} ({evento['ora_inizio']}-{evento['ora_fine']})"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Tipo:** {evento['tipo']}")
                                st.write(f"**Orario:** {evento['ora_inizio']} - {evento['ora_fine']}")
                                st.write(f"**Priorità:** {evento['priorita']}")
                            with col2:
                                st.write(f"**Cliente:** {evento['cliente'] or 'N/A'}")
                                st.write(f"**Luogo:** {evento['luogo'] or 'N/A'}")
                                st.write(f"**Preventivo:** {evento['preventivo'] or 'N/A'}")
                            
                            if evento['note']:
                                st.write(f"**Note:** {evento['note']}")
                except:
                    st.error("Errore nel visualizzare eventi")
            else:
                st.info("Nessun evento programmato. Aggiungi il primo evento!")

# DEMO
elif menu == "Demo":
    st.header("🎯 Demo e Test")
    
    st.markdown("### Test Connessione Supabase")
    
    if st.button("Test Connessione"):
        if db.test_connection():
            st.success("✅ Connessione a Supabase funziona!")
        else:
            st.error("❌ Errore connessione")
    
    st.markdown("### Carica Dati Demo Completi")
    st.markdown("Carica un set completo di dati interconnessi per testare tutte le funzionalità:")
    
    if st.button("🎮 Carica Dati Demo Completi", type="primary"):
        try:
            # Cliente demo
            cliente_demo = {
                "nome": "Rossi Costruzioni SRL",
                "email": "info@rossicost.it", 
                "telefono": "0421-123456",
                "note": "Cliente storico, sempre puntuale nei pagamenti",
                "data_creazione": "15/12/2024"
            }
            db.add_cliente(cliente_demo)
            
            cliente_demo2 = {
                "nome": "Studio Legale Bianchi",
                "email": "avv.bianchi@legal.it", 
                "telefono": "339-987654",
                "note": "Specialisti in diritto commerciale",
                "data_creazione": "10/12/2024"
            }
            db.add_cliente(cliente_demo2)
            
            # Preventivi demo
            preventivo_demo1 = {
                "numero": "PREV-001",
                "cliente": "Rossi Costruzioni SRL",
                "note": "Ristrutturazione bagno completa",
                "stato": "ACCETTATO",
                "data_creazione": "18/12/2024",
                "totale": 1970.0
            }
            db.add_preventivo(preventivo_demo1)
            
            preventivo_demo2 = {
                "numero": "OFF-002",
                "cliente": "Studio Legale Bianchi",
                "note": "Consulenza privacy per studio legale",
                "stato": "INVIATO",
                "data_creazione": "20/12/2024",
                "totale": 1540.0
            }
            db.add_preventivo(preventivo_demo2)
            
            # Spese demo
            spesa_demo1 = {
                "data": "20/12/2024",
                "categoria": "Trasporti",
                "descrizione": "Trasferta cantiere Rossi Costruzioni",
                "importo": 45.50,
                "progetto": "PREV-001",
                "detraibile": True,
                "ricevuta": "Si"
            }
            db.add_spesa(spesa_demo1)
            
            spesa_demo2 = {
                "data": "21/12/2024",
                "categoria": "Software",
                "descrizione": "Acquisto licenza software progettazione",
                "importo": 299.00,
                "progetto": "Generale",
                "detraibile": True,
                "ricevuta": "Si"
            }
            db.add_spesa(spesa_demo2)
            
            spesa_demo3 = {
                "data": "22/12/2024",
                "categoria": "Formazione",
                "descrizione": "Corso aggiornamento professionale",
                "importo": 150.00,
                "progetto": "Generale",
                "detraibile": True,
                "ricevuta": "Si"
            }
            db.add_spesa(spesa_demo3)
            
            # Scadenze demo
            scadenza_demo1 = {
                "titolo": "Scadenza Preventivo PREV-001",
                "data": "05/01/2025",
                "tipo": "Preventivo",
                "cliente": "Rossi Costruzioni SRL",
                "preventivo": "PREV-001",
                "priorita": "Alta",
                "descrizione": "Il preventivo per la ristrutturazione bagno scade",
                "importo": 1970.0,
                "stato": "Attiva"
            }
            db.add_scadenza(scadenza_demo1)
            
            scadenza_demo2 = {
                "titolo": "Pagamento Fattura Studio Legale",
                "data": "31/12/2024",
                "tipo": "Pagamento",
                "cliente": "Studio Legale Bianchi",
                "preventivo": "OFF-002",
                "priorita": "Media",
                "descrizione": "Pagamento consulenza privacy",
                "importo": 1540.0,
                "stato": "Attiva"
            }
            db.add_scadenza(scadenza_demo2)
            
            scadenza_demo3 = {
                "titolo": "Rinnovo Certificazione Professionale",
                "data": "15/01/2025",
                "tipo": "Certificazione",
                "cliente": "",
                "preventivo": "",
                "priorita": "Alta",
                "descrizione": "Rinnovo certificazione per progettazione",
                "importo": 250.0,
                "stato": "Attiva"
            }
            db.add_scadenza(scadenza_demo3)
            
            # Eventi calendario demo
            evento_demo1 = {
                "titolo": "Sopralluogo Rossi Costruzioni",
                "data": "02/01/2025",
                "ora_inizio": "09:00",
                "ora_fine": "11:00",
                "tipo": "Sopralluogo",
                "cliente": "Rossi Costruzioni SRL",
                "preventivo": "PREV-001",
                "priorita": "Alta",
                "luogo": "Via Roma 123, Milano",
                "note": "Prima visita per valutare lavori bagno",
                "stato": "Programmato"
            }
            db.add_evento_calendario(evento_demo1)
            
            evento_demo2 = {
                "titolo": "Riunione Studio Legale Bianchi",
                "data": "03/01/2025",
                "ora_inizio": "15:00",
                "ora_fine": "16:30",
                "tipo": "Riunione",
                "cliente": "Studio Legale Bianchi",
                "preventivo": "OFF-002",
                "priorita": "Media",
                "luogo": "Via Giustizia 45, Roma",
                "note": "Presentazione proposta consulenza privacy",
                "stato": "Programmato"
            }
            db.add_evento_calendario(evento_demo2)
            
            evento_demo3 = {
                "titolo": "Corso Aggiornamento CAD",
                "data": "08/01/2025",
                "ora_inizio": "09:00",
                "ora_fine": "17:00",
                "tipo": "Formazione",
                "cliente": "",
                "preventivo": "",
                "priorita": "Bassa",
                "luogo": "Centro Formazione TechPro",
                "note": "Aggiornamento competenze software progettazione",
                "stato": "Programmato"
            }
            db.add_evento_calendario(evento_demo3)
            
            # Aggiorna session state
            st.session_state.clienti = db.get_clienti()
            st.session_state.preventivi = db.get_preventivi()
            
            st.success("✅ Dati demo completi caricati con successo!")
            st.info("Ora puoi esplorare tutte le sezioni: Dashboard, Analytics, Amministrazione (Spese, Scadenze, Calendario), Reports")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Errore nel caricare dati demo: {e}")
    
    st.markdown("### Gestione Dati")
    
    if st.button("🔄 Ricarica Dati dal Database"):
        st.session_state.clienti = db.get_clienti()
        st.session_state.preventivi = db.get_preventivi()
        st.success(f"✅ Ricaricati: {len(st.session_state.clienti)} clienti, {len(st.session_state.preventivi)} preventivi")
    
    if st.button("🗑️ Elimina Tutti i Dati Demo", type="secondary"):
        st.warning("⚠️ Funzione non implementata per sicurezza. Puoi eliminare i dati manualmente da Supabase se necessario.")
    
    st.markdown("### Informazioni Sistema")
    st.markdown("""
    **TALENTO AI SUITE** - Versione con Supabase integrato
    
    Funzionalità implementate:
    - ✅ Dashboard con metriche
    - ✅ Gestione Clienti completa
    - ✅ Gestione Preventivi con stati
    - ✅ Analytics con grafici
    - ✅ Amministrazione:
        - ✅ Nota Spese con categorie e grafici
        - ✅ Scadenze con alert colorati
        - ✅ Calendario Eventi completo
    - ✅ Reports & Export con metriche finanziarie
    - ✅ Database Supabase persistente
    
    Tutti i dati sono salvati permanentemente e condivisibili.
    """)

# Footer
st.markdown("""
---
**TALENTO AI SUITE** - Versione con Supabase | Creato da Giancarlo Tonon
""")