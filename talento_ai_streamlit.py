import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configurazione pagina
st.set_page_config(
    page_title="TALENTO AI Suite", 
    page_icon="⭐", 
    layout="wide"
)

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
    ["Dashboard", "Gestione Clienti", "Gestione Preventivi", "Analytics", "Amministrazione", "Reports & Export", "Demo"]
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
    
    # Calcola spese totali
    total_spese = sum(s['importo'] for s in st.session_state.spese) if st.session_state.spese else 0
    
    return total_preventivi, total_clienti, valore_accettato, tasso_successo, total_spese

def carica_dati_demo():
    # Clienti demo
    st.session_state.clienti = [
        {
            "nome": "Rossi Costruzioni SRL",
            "email": "info@rossicost.it",
            "telefono": "0421-123456",
            "talenti": "Costruzioni, Ristrutturazioni, Edilizia",
            "note": "Cliente storico, sempre puntuale nei pagamenti",
            "data_creazione": "15/12/2024"
        },
        {
            "nome": "Studio Legale Bianchi",
            "email": "avv.bianchi@legal.it",
            "telefono": "339-987654",
            "talenti": "Consulenza Legale, Contrattualistica",
            "note": "Specialisti in diritto commerciale",
            "data_creazione": "10/12/2024"
        },
        {
            "nome": "Verdi Impianti",
            "email": "m.verdi@email.com",
            "telefono": "347-555777",
            "talenti": "Elettrico, Domotica, Fotovoltaico",
            "note": "Azienda innovativa, interessata a nuove tecnologie",
            "data_creazione": "08/12/2024"
        }
    ]
    # Eventi calendario demo
    st.session_state.eventi_calendario = [
        {
            "titolo": "Sopralluogo Rossi Costruzioni",
            "data": "02/01/2025",
            "data_obj": datetime(2025, 1, 2).date(),
            "ora_inizio": "09:00",
            "ora_fine": "11:00",
            "tipo": "Sopralluogo",
            "cliente": "Rossi Costruzioni SRL",
            "preventivo": "PREV-001",
            "priorita": "Alta",
            "luogo": "Via Roma 123, Milano",
            "note": "Prima visita per valutare lavori bagno",
            "stato": "Programmato"
        },
        {
            "titolo": "Riunione Studio Legale Bianchi",
            "data": "29/12/2024",
            "data_obj": datetime(2024, 12, 29).date(),
            "ora_inizio": "15:00",
            "ora_fine": "16:30",
            "tipo": "Riunione",
            "cliente": "Studio Legale Bianchi",
            "preventivo": "OFF-002",
            "priorita": "Media",
            "luogo": "Via Giustizia 45, Roma",
            "note": "Presentazione proposta consulenza privacy",
            "stato": "Programmato"
        },
        {
            "titolo": "Consegna Progetto Verdi Impianti",
            "data": "15/01/2025",
            "data_obj": datetime(2025, 1, 15).date(),
            "ora_inizio": "10:00",
            "ora_fine": "12:00",
            "tipo": "Consegna",
            "cliente": "Verdi Impianti",
            "preventivo": "PROG-003",
            "priorita": "Alta",
            "luogo": "Sede Verdi Impianti",
            "note": "Consegna finale piano digitalizzazione",
            "stato": "Programmato"
        },
        {
            "titolo": "Corso Aggiornamento CAD",
            "data": "08/01/2025",
            "data_obj": datetime(2025, 1, 8).date(),
            "ora_inizio": "09:00",
            "ora_fine": "17:00",
            "tipo": "Formazione",
            "cliente": "",
            "preventivo": "",
            "priorita": "Bassa",
            "luogo": "Centro Formazione TechPro",
            "note": "Aggiornamento competenze software progettazione",
            "stato": "Programmato"
        },
        {
            "titolo": "Deadline Preventivo Studio Legale",
            "data": "31/12/2024",
            "data_obj": datetime(2024, 12, 31).date(),
            "ora_inizio": "23:59",
            "ora_fine": "23:59",
            "tipo": "Deadline",
            "cliente": "Studio Legale Bianchi",
            "preventivo": "OFF-002",
            "priorita": "Alta",
            "luogo": "",
            "note": "Scadenza risposta al preventivo consulenza",
            "stato": "Programmato"
        },
        {
            "titolo": "Appuntamento Nuovo Cliente",
            "data": "03/01/2025",
            "data_obj": datetime(2025, 1, 3).date(),
            "ora_inizio": "14:00",
            "ora_fine": "15:00",
            "tipo": "Appuntamento",
            "cliente": "",
            "preventivo": "",
            "priorita": "Media",
            "luogo": "Ufficio",
            "note": "Primo incontro per possibile collaborazione",
            "stato": "Programmato"
        }
    ]
    
    # Preventivi demo
    st.session_state.preventivi = [
        {
            "numero": "PREV-001",
            "cliente": "Rossi Costruzioni SRL",
            "validita": 30,
            "iva": 22,
            "talenti": "Progettazione, Coordinamento, Direzione Lavori",
            "note": "Ristrutturazione bagno completa",
            "stato": "ACCETTATO",
            "data_creazione": "18/12/2024",
            "totale": 1970
        },
        {
            "numero": "OFF-002",
            "cliente": "Studio Legale Bianchi",
            "validita": 15,
            "iva": 22,
            "talenti": "Consulenza Specialistica, Formazione",
            "note": "Consulenza privacy per studio legale",
            "stato": "INVIATO",
            "data_creazione": "20/12/2024",
            "totale": 1540
        },
        {
            "numero": "PROG-003",
            "cliente": "Verdi Impianti",
            "validita": 45,
            "iva": 10,
            "talenti": "Strategia Digitale, Innovazione, Change Management",
            "note": "Consulenza digitalizzazione processi aziendali",
            "stato": "BOZZA",
            "data_creazione": "22/12/2024",
            "totale": 6000
        }
    ]
    
    # Spese demo
    st.session_state.spese = [
        {
            "data": "20/12/2024",
            "categoria": "Trasporti",
            "descrizione": "Trasferta cantiere Rossi Costruzioni",
            "importo": 45.50,
            "progetto": "PREV-001",
            "detraibile": True,
            "ricevuta": "Si"
        },
        {
            "data": "21/12/2024",
            "categoria": "Materiali",
            "descrizione": "Acquisto software progettazione",
            "importo": 299.00,
            "progetto": "PROG-003",
            "detraibile": True,
            "ricevuta": "Si"
        },
        {
            "data": "22/12/2024",
            "categoria": "Formazione",
            "descrizione": "Corso aggiornamento professionale",
            "importo": 150.00,
            "progetto": "Generale",
            "detraibile": True,
            "ricevuta": "Si"
        },
        {
            "data": "23/12/2024",
            "categoria": "Ufficio",
            "descrizione": "Cancelleria e materiale ufficio",
            "importo": 75.30,
            "progetto": "Generale",
            "detraibile": False,
            "ricevuta": "No"
        }
    ]
    
    # Scadenze demo
    st.session_state.scadenze = [
        {
            "titolo": "Scadenza Preventivo PREV-001",
            "data": "05/01/2025",
            "tipo": "Preventivo",
            "cliente": "Rossi Costruzioni SRL",
            "preventivo": "PREV-001",
            "priorita": "Alta",
            "descrizione": "Il preventivo per la ristrutturazione bagno scade",
            "importo": 1970.0,
            "giorni_rimanenti": 8,
            "stato": "Attiva"
        },
        {
            "titolo": "Pagamento Fattura Studio Legale",
            "data": "31/12/2024",
            "tipo": "Pagamento",
            "cliente": "Studio Legale Bianchi",
            "preventivo": "",
            "priorita": "Media",
            "descrizione": "Pagamento consulenza privacy",
            "importo": 1540.0,
            "giorni_rimanenti": 3,
            "stato": "Attiva"
        },
        {
            "titolo": "Rinnovo Certificazione Professionale",
            "data": "15/01/2025",
            "tipo": "Certificazione",
            "cliente": "",
            "preventivo": "",
            "priorita": "Alta",
            "descrizione": "Rinnovo certificazione per progettazione",
            "importo": 250.0,
            "giorni_rimanenti": 18,
            "stato": "Attiva"
        },
        {
            "titolo": "Appuntamento Verdi Impianti",
            "data": "30/12/2024",
            "tipo": "Appuntamento",
            "cliente": "Verdi Impianti",
            "preventivo": "PROG-003",
            "priorita": "Media",
            "descrizione": "Incontro per definire dettagli digitalizzazione",
            "importo": 0.0,
            "giorni_rimanenti": 2,
            "stato": "Attiva"
        },
        {
            "titolo": "Rinnovo Contratto Software",
            "data": "25/12/2024",
            "tipo": "Rinnovo",
            "cliente": "",
            "preventivo": "",
            "priorita": "Bassa",
            "descrizione": "Rinnovo licenza software progettazione CAD",
            "importo": 299.0,
            "giorni_rimanenti": -3,
            "stato": "Attiva"
        }
    ]

# DASHBOARD
if menu == "Dashboard":
    st.header("📊 Dashboard Principale")
    
    # Calcola statistiche
    total_preventivi, total_clienti, valore_accettato, tasso_successo, total_spese = calcola_statistiche()
    
    # Metriche principali
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Preventivi Totali", total_preventivi)
    
    with col2:
        st.metric("Clienti Attivi", total_clienti)
    
    with col3:
        st.metric("Valore Accettato", f"€{valore_accettato:,.0f}")
    
    with col4:
        st.metric("Tasso Successo", f"{tasso_successo:.0f}%")
    
    with col5:
        st.metric("Spese Totali", f"€{total_spese:,.2f}")
    
    # Grafici se ci sono dati
    if st.session_state.preventivi:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Preventivi per Stato")
            df_stati = pd.DataFrame(st.session_state.preventivi)
            fig_stati = px.pie(df_stati, names='stato', title="Distribuzione Stati")
            st.plotly_chart(fig_stati, use_container_width=True)
        
        with col2:
            st.subheader("Valore per Cliente")
            df_valori = df_stati.groupby('cliente')['totale'].sum().reset_index()
            fig_valori = px.bar(df_valori, x='cliente', y='totale', title="Valore per Cliente")
            st.plotly_chart(fig_valori, use_container_width=True)

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
            talenti = st.text_input("Talenti Principali")
            note = st.text_area("Note Personali")
            
            if st.form_submit_button("Aggiungi Cliente", type="primary"):
                if nome:
                    nuovo_cliente = {
                        "nome": nome,
                        "email": email,
                        "telefono": telefono,
                        "talenti": talenti,
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
                
                col1, col2 = st.columns(2)
                with col1:
                    validita = st.number_input("Giorni Validità", value=30, min_value=1)
                with col2:
                    iva = st.number_input("IVA %", value=22.0, min_value=0.0)
                
                talenti = st.text_input("Talenti Coinvolti")
                note = st.text_area("Note per Cliente")
                totale = st.number_input("Valore Totale €", min_value=0.0, step=0.01)
                
                if st.form_submit_button("Crea Preventivo", type="primary"):
                    if numero and cliente:
                        nuovo_preventivo = {
                            "numero": numero,
                            "cliente": cliente,
                            "validita": validita,
                            "iva": iva,
                            "talenti": talenti,
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
            
            # Filtri
            col1, col2 = st.columns(2)
            with col1:
                stati_filtro = st.multiselect("Filtra per stato:", 
                                            ["BOZZA", "INVIATO", "ACCETTATO", "RIFIUTATO"],
                                            default=["BOZZA", "INVIATO", "ACCETTATO", "RIFIUTATO"])
            
            df_filtrato = df_preventivi[df_preventivi['stato'].isin(stati_filtro)]
            st.dataframe(df_filtrato, use_container_width=True)
            
            # Cambio stato
            if st.session_state.preventivi:
                st.subheader("Cambia Stato Preventivo")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    preventivo_sel = st.selectbox("Preventivo:", [p["numero"] for p in st.session_state.preventivi])
                with col2:
                    nuovo_stato = st.selectbox("Nuovo Stato:", ["BOZZA", "INVIATO", "ACCETTATO", "RIFIUTATO", "SCADUTO"])
                with col3:
                    if st.button("Cambia Stato"):
                        for p in st.session_state.preventivi:
                            if p["numero"] == preventivo_sel:
                                p["stato"] = nuovo_stato
                                st.success(f"Stato cambiato a {nuovo_stato}")
                                st.rerun()
                                break
        else:
            st.info("Nessun preventivo creato. Crea il primo preventivo!")

# ANALYTICS
elif menu == "Analytics":
    st.header("📈 Analytics Avanzate")
    
    if not st.session_state.preventivi:
        st.info("Carica i dati demo o crea alcuni preventivi per vedere le analytics!")
    else:
        df_preventivi = pd.DataFrame(st.session_state.preventivi)
        
        # Analisi temporale
        st.subheader("Analisi Temporale")
        df_preventivi['data_creazione'] = pd.to_datetime(df_preventivi['data_creazione'], format='%d/%m/%Y')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Preventivi nel tempo
            preventivi_tempo = df_preventivi.groupby(df_preventivi['data_creazione'].dt.date).size().reset_index()
            preventivi_tempo.columns = ['Data', 'Numero Preventivi']
            
            fig_tempo = px.line(preventivi_tempo, x='Data', y='Numero Preventivi', 
                               title="Preventivi Creati nel Tempo")
            st.plotly_chart(fig_tempo, use_container_width=True)
        
        with col2:
            # Valore per stato
            valore_stato = df_preventivi.groupby('stato')['totale'].sum().reset_index()
            fig_valore = px.bar(valore_stato, x='stato', y='totale', 
                               title="Valore Totale per Stato")
            st.plotly_chart(fig_valore, use_container_width=True)
        
        # Tabella riassuntiva
        st.subheader("Riassunto per Cliente")
        riassunto = df_preventivi.groupby('cliente').agg({
            'numero': 'count',
            'totale': ['sum', 'mean'],
            'stato': lambda x: (x == 'ACCETTATO').sum()
        }).round(2)
        
        riassunto.columns = ['Num. Preventivi', 'Valore Totale', 'Valore Medio', 'Preventivi Accettati']
        st.dataframe(riassunto, use_container_width=True)

# AMMINISTRAZIONE - NUOVA SEZIONE
elif menu == "Amministrazione":
    st.header("🏢 Amministrazione")
    
    # Tabs per le diverse funzioni amministrative
    tab1, tab2, tab3 = st.tabs(["📝 Nota Spese", "⏰ Scadenze", "📅 Calendario"])
    
    with tab1:
        st.subheader("Gestione Nota Spese")
        
        # Sottotabs per organizzare meglio
        subtab1, subtab2, subtab3 = st.tabs(["Aggiungi Spesa", "Lista Spese", "Analisi Spese"])
        
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
                    if st.session_state.preventivi:
                        progetti_disponibili.extend([p["numero"] for p in st.session_state.preventivi])
                    
                    progetto = st.selectbox("Progetto/Preventivo", progetti_disponibili)
                    detraibile = st.checkbox("Detraibile/Deducibile", value=True)
                    ricevuta = st.selectbox("Ricevuta", ["Si", "No"])
                
                descrizione = st.text_area("Descrizione Spesa")
                
                if st.form_submit_button("Aggiungi Spesa", type="primary"):
    if importo > 0 and descrizione:
        
        # Converitiamo la data nel formato richiesto dal database (YYYY-MM-DD)
        data_db = data_spesa.strftime("%Y-%m-%d")
        
        # NUOVO SALVATAGGIO: Chiama la funzione di salvataggio sul database
        if save_nuova_spesa(
            descrizione, 
            importo, 
            categoria, 
            data_db
        ):
            st.success(f"Spesa di €{importo:.2f} salvata in modo permanente!")
            st.rerun()
    else:
        st.error("Importo e descrizione sono obbligatori!")

        
        with subtab2:
            st.subheader("Lista Spese")
            
            if st.session_state.spese:
                df_spese = pd.DataFrame(st.session_state.spese)
                
                # Filtri
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    categorie_filtro = st.multiselect("Filtra per categoria:", 
                                                    df_spese['categoria'].unique(),
                                                    default=df_spese['categoria'].unique())
                
                with col2:
                    progetti_filtro = st.multiselect("Filtra per progetto:", 
                                                   df_spese['progetto'].unique(),
                                                   default=df_spese['progetto'].unique())
                
                with col3:
                    solo_detraibili = st.checkbox("Solo spese detraibili")
                
                # Applica filtri
                df_filtrato = df_spese[
                    (df_spese['categoria'].isin(categorie_filtro)) &
                    (df_spese['progetto'].isin(progetti_filtro))
                ]
                
                if solo_detraibili:
                    df_filtrato = df_filtrato[df_filtrato['detraibile'] == True]
                
                # Mostra totale filtrato
                totale_filtrato = df_filtrato['importo'].sum()
                st.metric("Totale Spese (Filtrate)", f"€{totale_filtrato:.2f}")
                
                # Tabella
                st.dataframe(df_filtrato, use_container_width=True)
                
            else:
                st.info("Nessuna spesa registrata. Aggiungi la prima spesa!")
        
        with subtab3:
            st.subheader("Analisi Spese")
            
            if st.session_state.spese:
                df_spese = pd.DataFrame(st.session_state.spese)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Spese per categoria
                    spese_categoria = df_spese.groupby('categoria')['importo'].sum().reset_index()
                    fig_cat = px.pie(spese_categoria, values='importo', names='categoria', 
                                   title="Spese per Categoria")
                    st.plotly_chart(fig_cat, use_container_width=True)
                
                with col2:
                    # Spese per progetto
                    spese_progetto = df_spese.groupby('progetto')['importo'].sum().reset_index()
                    fig_prog = px.bar(spese_progetto, x='progetto', y='importo', 
                                    title="Spese per Progetto")
                    st.plotly_chart(fig_prog, use_container_width=True)
                
                # Statistiche
                st.subheader("Statistiche Spese")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    totale_spese = df_spese['importo'].sum()
                    st.metric("Totale Spese", f"€{totale_spese:.2f}")
                
                with col2:
                    spese_detraibili = df_spese[df_spese['detraibile'] == True]['importo'].sum()
                    st.metric("Spese Detraibili", f"€{spese_detraibili:.2f}")
                
                with col3:
                    spesa_media = df_spese['importo'].mean()
                    st.metric("Spesa Media", f"€{spesa_media:.2f}")
                
                with col4:
                    num_spese = len(df_spese)
                    st.metric("Numero Spese", num_spese)
            else:
                st.info("Aggiungi alcune spese per vedere le analisi!")
    
    with tab2:
        st.subheader("Scadenze & Promemoria")
        
        # Inizializza scadenze se non esistono
        if 'scadenze' not in st.session_state:
            st.session_state.scadenze = []
        
        # Sottotabs per organizzare
        subtab1, subtab2, subtab3 = st.tabs(["Aggiungi Scadenza", "Lista Scadenze", "Dashboard Scadenze"])
        
        with subtab1:
            st.subheader("Nuova Scadenza")
            
            with st.form("form_scadenza"):
                col1, col2 = st.columns(2)
                
                with col1:
                    titolo = st.text_input("Titolo Scadenza *")
                    data_scadenza = st.date_input("Data Scadenza", 
                                                value=datetime.now())
                    tipo_scadenza = st.selectbox("Tipo", 
                                               ["Preventivo", "Pagamento", "Contratto", 
                                                "Certificazione", "Rinnovo", "Appuntamento", "Altro"])
                
                with col2:
                    if st.session_state.clienti:
                        clienti_disponibili = ["Nessuno"] + [c["nome"] for c in st.session_state.clienti]
                        cliente_collegato = st.selectbox("Cliente Collegato", clienti_disponibili)
                    else:
                        cliente_collegato = "Nessuno"
                    
                    if st.session_state.preventivi:
                        preventivi_disponibili = ["Nessuno"] + [p["numero"] for p in st.session_state.preventivi]
                        preventivo_collegato = st.selectbox("Preventivo Collegato", preventivi_disponibili)
                    else:
                        preventivo_collegato = "Nessuno"
                    
                    priorita = st.selectbox("Priorità", ["Alta", "Media", "Bassa"])
                
                descrizione = st.text_area("Descrizione/Note")
                importo = st.number_input("Importo (se applicabile) €", min_value=0.0, step=0.01)
                
                if st.form_submit_button("Aggiungi Scadenza", type="primary"):
                    if titolo:
                        # Calcola giorni rimanenti
                        giorni_rimanenti = (data_scadenza - datetime.now().date()).days
                        
                        nuova_scadenza = {
                            "titolo": titolo,
                            "data": data_scadenza.strftime("%d/%m/%Y"),
                            "tipo": tipo_scadenza,
                            "cliente": cliente_collegato if cliente_collegato != "Nessuno" else "",
                            "preventivo": preventivo_collegato if preventivo_collegato != "Nessuno" else "",
                            "priorita": priorita,
                            "descrizione": descrizione,
                            "importo": importo,
                            "giorni_rimanenti": giorni_rimanenti,
                            "stato": "Attiva"
                        }
                        st.session_state.scadenze.append(nuova_scadenza)
                        st.success(f"Scadenza '{titolo}' aggiunta con successo!")
                        st.rerun()
                    else:
                        st.error("Il titolo è obbligatorio!")
        
        with subtab2:
            st.subheader("Lista Scadenze")
            
            if st.session_state.scadenze:
                # Aggiorna giorni rimanenti
                for scadenza in st.session_state.scadenze:
                    data_scad = datetime.strptime(scadenza["data"], "%d/%m/%Y").date()
                    scadenza["giorni_rimanenti"] = (data_scad - datetime.now().date()).days
                
                df_scadenze = pd.DataFrame(st.session_state.scadenze)
                
                # Filtri
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    tipi_filtro = st.multiselect("Filtra per tipo:", 
                                               df_scadenze['tipo'].unique(),
                                               default=df_scadenze['tipo'].unique())
                
                with col2:
                    priorita_filtro = st.multiselect("Filtra per priorità:", 
                                                   df_scadenze['priorita'].unique(),
                                                   default=df_scadenze['priorita'].unique())
                
                with col3:
                    stato_scadenze = st.selectbox("Mostra:", 
                                                ["Tutte", "Solo Attive", "Solo Scadute", "Prossime (7 giorni)"])
                
                # Applica filtri
                df_filtrato = df_scadenze[
                    (df_scadenze['tipo'].isin(tipi_filtro)) &
                    (df_scadenze['priorita'].isin(priorita_filtro))
                ]
                
                if stato_scadenze == "Solo Attive":
                    df_filtrato = df_filtrato[df_filtrato['giorni_rimanenti'] >= 0]
                elif stato_scadenze == "Solo Scadute":
                    df_filtrato = df_filtrato[df_filtrato['giorni_rimanenti'] < 0]
                elif stato_scadenze == "Prossime (7 giorni)":
                    df_filtrato = df_filtrato[(df_filtrato['giorni_rimanenti'] >= 0) & 
                                            (df_filtrato['giorni_rimanenti'] <= 7)]
                
                # Ordina per giorni rimanenti
                df_filtrato = df_filtrato.sort_values('giorni_rimanenti')
                
                # Mostra tabella con colori
                for _, scadenza in df_filtrato.iterrows():
                    giorni = scadenza['giorni_rimanenti']
                    
                    # Determina colore
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
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Data:** {scadenza['data']}")
                            st.write(f"**Tipo:** {scadenza['tipo']}")
                            st.write(f"**Priorità:** {scadenza['priorita']}")
                        with col2:
                            st.write(f"**Cliente:** {scadenza['cliente'] or 'N/A'}")
                            st.write(f"**Preventivo:** {scadenza['preventivo'] or 'N/A'}")
                            if scadenza['importo'] > 0:
                                st.write(f"**Importo:** €{scadenza['importo']:.2f}")
                        
                        if scadenza['descrizione']:
                            st.write(f"**Note:** {scadenza['descrizione']}")
                
            else:
                st.info("Nessuna scadenza registrata. Aggiungi la prima scadenza!")
        
        with subtab3:
            st.subheader("Dashboard Scadenze")
            
            if st.session_state.scadenze:
                # Aggiorna giorni rimanenti
                for scadenza in st.session_state.scadenze:
                    data_scad = datetime.strptime(scadenza["data"], "%d/%m/%Y").date()
                    scadenza["giorni_rimanenti"] = (data_scad - datetime.now().date()).days
                
                df_scadenze = pd.DataFrame(st.session_state.scadenze)
                
                # Metriche riassuntive
                col1, col2, col3, col4 = st.columns(4)
                
                scadute = len(df_scadenze[df_scadenze['giorni_rimanenti'] < 0])
                urgenti = len(df_scadenze[(df_scadenze['giorni_rimanenti'] >= 0) & 
                                        (df_scadenze['giorni_rimanenti'] <= 3)])
                prossime = len(df_scadenze[(df_scadenze['giorni_rimanenti'] > 3) & 
                                         (df_scadenze['giorni_rimanenti'] <= 7)])
                future = len(df_scadenze[df_scadenze['giorni_rimanenti'] > 7])
                
                with col1:
                    st.metric("🔴 Scadute", scadute)
                with col2:
                    st.metric("🟠 Urgenti (≤3gg)", urgenti)
                with col3:
                    st.metric("🟡 Prossime (4-7gg)", prossime)
                with col4:
                    st.metric("🟢 Future (>7gg)", future)
                
                # Grafici
                col1, col2 = st.columns(2)
                
                with col1:
                    # Scadenze per tipo
                    tipo_count = df_scadenze['tipo'].value_counts().reset_index()
                    tipo_count.columns = ['Tipo', 'Conteggio']
                    fig_tipo = px.pie(tipo_count, values='Conteggio', names='Tipo', 
                                    title="Scadenze per Tipo")
                    st.plotly_chart(fig_tipo, use_container_width=True)
                
                with col2:
                    # Scadenze per priorità
                    priorita_count = df_scadenze['priorita'].value_counts().reset_index()
                    priorita_count.columns = ['Priorità', 'Conteggio']
                    colors = {'Alta': 'red', 'Media': 'orange', 'Bassa': 'green'}
                    fig_priorita = px.bar(priorita_count, x='Priorità', y='Conteggio', 
                                        title="Scadenze per Priorità",
                                        color='Priorità', color_discrete_map=colors)
                    st.plotly_chart(fig_priorita, use_container_width=True)
                
                # Prossime scadenze importanti
                st.subheader("⚠️ Scadenze Urgenti (Prossimi 7 giorni)")
                prossime_urgenti = df_scadenze[
                    (df_scadenze['giorni_rimanenti'] >= 0) & 
                    (df_scadenze['giorni_rimanenti'] <= 7)
                ].sort_values('giorni_rimanenti')
                
                if len(prossime_urgenti) > 0:
                    for _, scadenza in prossime_urgenti.iterrows():
                        giorni = scadenza['giorni_rimanenti']
                        if giorni <= 1:
                            st.error(f"🔥 **{scadenza['titolo']}** - Scade {'oggi' if giorni == 0 else 'domani'}!")
                        elif giorni <= 3:
                            st.warning(f"⚠️ **{scadenza['titolo']}** - Scade in {giorni} giorni")
                        else:
                            st.info(f"📅 **{scadenza['titolo']}** - Scade in {giorni} giorni")
                else:
                    st.success("🎉 Nessuna scadenza urgente nei prossimi 7 giorni!")
                
            else:
                st.info("Aggiungi alcune scadenze per vedere la dashboard!")

    
    with tab3:
        st.subheader("Calendario Lavori")
        
        # Inizializza eventi calendario se non esistono
        if 'eventi_calendario' not in st.session_state:
            st.session_state.eventi_calendario = []
        
        # Sottotabs per organizzare
        subtab1, subtab2, subtab3 = st.tabs(["Aggiungi Evento", "Vista Calendario", "Planning Progetti"])
        
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
                    
                    if st.session_state.clienti:
                        clienti_disponibili = ["Nessuno"] + [c["nome"] for c in st.session_state.clienti]
                        cliente_evento = st.selectbox("Cliente Collegato", clienti_disponibili)
                    else:
                        cliente_evento = "Nessuno"
                    
                    if st.session_state.preventivi:
                        preventivi_disponibili = ["Nessuno"] + [p["numero"] for p in st.session_state.preventivi]
                        preventivo_evento = st.selectbox("Preventivo Collegato", preventivi_disponibili)
                    else:
                        preventivo_evento = "Nessuno"
                    
                    priorita_evento = st.selectbox("Priorità", ["Alta", "Media", "Bassa"])
                
                luogo = st.text_input("Luogo/Indirizzo")
                note_evento = st.text_area("Note/Descrizione")
                
                if st.form_submit_button("Aggiungi Evento", type="primary"):
                    if titolo_evento:
                        nuovo_evento = {
                            "titolo": titolo_evento,
                            "data": data_evento.strftime("%d/%m/%Y"),
                            "data_obj": data_evento,
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
                        st.session_state.eventi_calendario.append(nuovo_evento)
                        st.success(f"Evento '{titolo_evento}' aggiunto al calendario!")
                        st.rerun()
                    else:
                        st.error("Il titolo dell'evento è obbligatorio!")
        
        with subtab2:
            st.subheader("Vista Calendario")
            
            # Selettore mese/anno
            col1, col2, col3 = st.columns([2, 2, 3])
            
            with col1:
                mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
                       "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
                mese_selezionato = st.selectbox("Mese", mesi, index=datetime.now().month - 1)
                mese_num = mesi.index(mese_selezionato) + 1
            
            with col2:
                anno_selezionato = st.selectbox("Anno", range(2024, 2027), index=1)
            
            with col3:
                if st.button("🏠 Vai a Oggi"):
                    oggi = datetime.now()
                    mese_selezionato = mesi[oggi.month - 1]
                    anno_selezionato = oggi.year
                    st.rerun()
            
            # Genera calendario del mese
            import calendar
            cal = calendar.monthcalendar(anno_selezionato, mese_num)
            
            # Filtra eventi per il mese selezionato
            eventi_mese = []
            if st.session_state.eventi_calendario:
                for evento in st.session_state.eventi_calendario:
                    data_evento = datetime.strptime(evento["data"], "%d/%m/%Y")
                    if data_evento.month == mese_num and data_evento.year == anno_selezionato:
                        eventi_mese.append(evento)
            
            # Mostra calendario
            st.markdown(f"### 📅 {mese_selezionato} {anno_selezionato}")
            
            # Header giorni settimana
            col_headers = st.columns(7)
            giorni_settimana = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
            for i, giorno in enumerate(giorni_settimana):
                col_headers[i].markdown(f"**{giorno}**")
            
            # Righe calendario
            for settimana in cal:
                cols = st.columns(7)
                for i, giorno in enumerate(settimana):
                    if giorno == 0:
                        cols[i].write("")  # Giorno vuoto
                    else:
                        # Trova eventi per questo giorno
                        eventi_giorno = [e for e in eventi_mese 
                                       if datetime.strptime(e["data"], "%d/%m/%Y").day == giorno]
                        
                        # Crea contenuto cella
                        contenuto = f"**{giorno}**"
                        
                        # Aggiungi indicatori eventi
                        for evento in eventi_giorno:
                            if evento["priorita"] == "Alta":
                                contenuto += "\n🔴"
                            elif evento["priorita"] == "Media":
                                contenuto += "\n🟡"
                            else:
                                contenuto += "\n🟢"
                        
                        # Evidenzia oggi
                        oggi = datetime.now()
                        if (giorno == oggi.day and mese_num == oggi.month and 
                            anno_selezionato == oggi.year):
                            cols[i].markdown(f"🎯 {contenuto}")
                        else:
                            cols[i].markdown(contenuto)
            
            # Lista eventi del mese
            if eventi_mese:
                st.markdown("---")
                st.subheader(f"📋 Eventi di {mese_selezionato}")
                
                # Ordina eventi per data
                eventi_mese_ord = sorted(eventi_mese, 
                                       key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"))
                
                for evento in eventi_mese_ord:
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
            else:
                st.info(f"Nessun evento programmato per {mese_selezionato} {anno_selezionato}")
        
        with subtab3:
            st.subheader("Planning Progetti")
            
            if st.session_state.preventivi and st.session_state.eventi_calendario:
                # Timeline progetti
                st.markdown("### 📊 Timeline Progetti")
                
                # Raggruppa eventi per preventivo
                eventi_per_progetto = {}
                for evento in st.session_state.eventi_calendario:
                    if evento['preventivo']:
                        if evento['preventivo'] not in eventi_per_progetto:
                            eventi_per_progetto[evento['preventivo']] = []
                        eventi_per_progetto[evento['preventivo']].append(evento)
                
                # Mostra timeline per ogni progetto
                for preventivo, eventi in eventi_per_progetto.items():
                    with st.expander(f"📋 Progetto: {preventivo}"):
                        # Trova cliente del preventivo
                        cliente_progetto = next((p['cliente'] for p in st.session_state.preventivi 
                                              if p['numero'] == preventivo), "N/A")
                        st.write(f"**Cliente:** {cliente_progetto}")
                        
                        # Ordina eventi per data
                        eventi_ord = sorted(eventi, 
                                          key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"))
                        
                        # Mostra eventi timeline
                        for i, evento in enumerate(eventi_ord):
                            if i == 0:
                                st.write(f"🟢 **INIZIO** - {evento['data']}: {evento['titolo']}")
                            elif i == len(eventi_ord) - 1:
                                st.write(f"🏁 **FINE** - {evento['data']}: {evento['titolo']}")
                            else:
                                st.write(f"⚡ {evento['data']}: {evento['titolo']}")
                
                # Statistiche planning
                st.markdown("### 📈 Statistiche Planning")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    progetti_attivi = len(eventi_per_progetto)
                    st.metric("Progetti Attivi", progetti_attivi)
                
                with col2:
                    eventi_totali = len(st.session_state.eventi_calendario)
                    st.metric("Eventi Totali", eventi_totali)
                
                with col3:
                    # Prossimo evento
                    oggi = datetime.now().date()
                    eventi_futuri = [e for e in st.session_state.eventi_calendario 
                                   if datetime.strptime(e["data"], "%d/%m/%Y").date() >= oggi]
                    if eventi_futuri:
                        prossimo = min(eventi_futuri, 
                                     key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"))
                        giorni_prossimo = (datetime.strptime(prossimo["data"], "%d/%m/%Y").date() - oggi).days
                        st.metric("Prossimo Evento", f"{giorni_prossimo} giorni")
                    else:
                        st.metric("Prossimo Evento", "Nessuno")
                
            else:
                st.info("Aggiungi alcuni eventi collegati ai preventivi per vedere il planning!")


# REPORTS & EXPORT - NUOVA SEZIONE
elif menu == "Reports & Export":
    st.header("📊 Reports & Export")
    
    # Tabs per le diverse funzioni di reporting
    tab1, tab2, tab3 = st.tabs(["📊 Reports Finanziari", "📄 Export PDF", "📧 Email Automatiche"])
    
    with tab1:
        st.subheader("Reports Finanziari")
        
        # Verifica che ci siano dati
        if not (st.session_state.preventivi or st.session_state.spese):
            st.info("Carica i dati demo o aggiungi preventivi e spese per generare reports finanziari!")
        else:
            # Sezione filtri periodo
            st.markdown("### 📅 Periodo di Analisi")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                data_inizio = st.date_input("Data Inizio", value=datetime(2024, 1, 1))
            with col2:
                data_fine = st.date_input("Data Fine", value=datetime(2025, 12, 31))
            with col3:
                tipo_report = st.selectbox("Tipo Report", 
                                         ["Completo", "Solo Preventivi", "Solo Spese", "Per Cliente"])
            
            # Calcola dati per il periodo
            df_preventivi = pd.DataFrame(st.session_state.preventivi) if st.session_state.preventivi else pd.DataFrame()
            df_spese = pd.DataFrame(st.session_state.spese) if st.session_state.spese else pd.DataFrame()
            
            # Filtra per periodo se ci sono dati
            if not df_preventivi.empty:
                df_preventivi['data_creazione_dt'] = pd.to_datetime(df_preventivi['data_creazione'], format='%d/%m/%Y')
                df_preventivi_filtrato = df_preventivi[
                    (df_preventivi['data_creazione_dt'].dt.date >= data_inizio) &
                    (df_preventivi['data_creazione_dt'].dt.date <= data_fine)
                ]
            else:
                df_preventivi_filtrato = df_preventivi
            
            if not df_spese.empty:
                df_spese['data_dt'] = pd.to_datetime(df_spese['data'], format='%d/%m/%Y')
                df_spese_filtrato = df_spese[
                    (df_spese['data_dt'].dt.date >= data_inizio) &
                    (df_spese['data_dt'].dt.date <= data_fine)
                ]
            else:
                df_spese_filtrato = df_spese
            
            # Calcola metriche principali
            if not df_preventivi_filtrato.empty:
                entrate_totali = df_preventivi_filtrato[df_preventivi_filtrato['stato'] == 'ACCETTATO']['totale'].sum()
                preventivi_accettati = len(df_preventivi_filtrato[df_preventivi_filtrato['stato'] == 'ACCETTATO'])
                valore_pipeline = df_preventivi_filtrato[df_preventivi_filtrato['stato'].isin(['INVIATO', 'BOZZA'])]['totale'].sum()
            else:
                entrate_totali = 0
                preventivi_accettati = 0
                valore_pipeline = 0
            
            if not df_spese_filtrato.empty:
                uscite_totali = df_spese_filtrato['importo'].sum()
                spese_detraibili = df_spese_filtrato[df_spese_filtrato['detraibile'] == True]['importo'].sum()
            else:
                uscite_totali = 0
                spese_detraibili = 0
            
            utile_lordo = entrate_totali - uscite_totali
            margine_percentuale = (utile_lordo / entrate_totali * 100) if entrate_totali > 0 else 0
            
            # Dashboard finanziaria
            st.markdown("### 💰 Dashboard Finanziaria")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Entrate Totali", f"€{entrate_totali:,.2f}")
            with col2:
                st.metric("💸 Uscite Totali", f"€{uscite_totali:,.2f}")
            with col3:
                delta_color = "normal" if utile_lordo >= 0 else "inverse"
                st.metric("📈 Utile Lordo", f"€{utile_lordo:,.2f}", delta=f"{margine_percentuale:.1f}%")
            with col4:
                st.metric("📋 Preventivi Vinti", preventivi_accettati)
            
            # Riga aggiuntiva metriche
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔄 Pipeline", f"€{valore_pipeline:,.2f}")
            with col2:
                st.metric("📊 Spese Detraibili", f"€{spese_detraibili:,.2f}")
            with col3:
                risparmio_fiscale = spese_detraibili * 0.22  # Stima 22% IVA
                st.metric("💡 Risparmio Fiscale", f"€{risparmio_fiscale:,.2f}")
            with col4:
                ticket_medio = entrate_totali / preventivi_accettati if preventivi_accettati > 0 else 0
                st.metric("🎯 Ticket Medio", f"€{ticket_medio:,.2f}")
            
            # Grafici analitici
            if not df_preventivi_filtrato.empty or not df_spese_filtrato.empty:
                st.markdown("### 📈 Analisi Grafiche")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Grafico entrate vs uscite
                    categorie = ['Entrate', 'Uscite']
                    valori = [entrate_totali, uscite_totali]
                    colori = ['#2E8B57', '#DC143C']  # Verde per entrate, rosso per uscite
                    
                    fig_entrate_uscite = go.Figure(data=[
                        go.Bar(x=categorie, y=valori, marker_color=colori,
                               text=[f'€{v:,.0f}' for v in valori], textposition='auto')
                    ])
                    fig_entrate_uscite.update_layout(
                        title="💰 Entrate vs Uscite",
                        yaxis_title="Euro (€)",
                        showlegend=False
                    )
                    st.plotly_chart(fig_entrate_uscite, use_container_width=True)
                
                with col2:
                    # Grafico distribuzione preventivi per stato
                    if not df_preventivi_filtrato.empty:
                        stati_count = df_preventivi_filtrato['stato'].value_counts()
                        fig_stati = px.pie(values=stati_count.values, names=stati_count.index,
                                          title="📊 Distribuzione Preventivi per Stato")
                        st.plotly_chart(fig_stati, use_container_width=True)
                    else:
                        st.info("Nessun preventivo nel periodo selezionato")
                
                # Analisi per cliente
                if not df_preventivi_filtrato.empty:
                    st.markdown("### 👥 Analisi per Cliente")
                    
                    cliente_stats = df_preventivi_filtrato.groupby('cliente').agg({
                        'totale': ['sum', 'count', 'mean'],
                        'stato': lambda x: (x == 'ACCETTATO').sum()
                    }).round(2)
                    
                    cliente_stats.columns = ['Valore Totale', 'Num. Preventivi', 'Valore Medio', 'Preventivi Vinti']
                    cliente_stats['Tasso Successo %'] = (cliente_stats['Preventivi Vinti'] / cliente_stats['Num. Preventivi'] * 100).round(1)
                    
                    st.dataframe(cliente_stats, use_container_width=True)
                    
                    # Grafico top clienti
                    top_clienti = cliente_stats.nlargest(5, 'Valore Totale')
                    fig_clienti = px.bar(x=top_clienti.index, y=top_clienti['Valore Totale'],
                                        title="🏆 Top 5 Clienti per Valore")
                    fig_clienti.update_layout(xaxis_title="Cliente", yaxis_title="Valore Totale (€)")
                    st.plotly_chart(fig_clienti, use_container_width=True)
                
                # Analisi spese per categoria
                if not df_spese_filtrato.empty:
                    st.markdown("### 💸 Analisi Spese per Categoria")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        spese_categoria = df_spese_filtrato.groupby('categoria')['importo'].sum().sort_values(ascending=False)
                        fig_spese_cat = px.bar(x=spese_categoria.index, y=spese_categoria.values,
                                              title="📊 Spese per Categoria")
                        fig_spese_cat.update_layout(xaxis_title="Categoria", yaxis_title="Importo (€)")
                        st.plotly_chart(fig_spese_cat, use_container_width=True)
                    
                    with col2:
                        # Grafico spese detraibili vs non detraibili
                        detraibili = df_spese_filtrato[df_spese_filtrato['detraibile'] == True]['importo'].sum()
                        non_detraibili = df_spese_filtrato[df_spese_filtrato['detraibile'] == False]['importo'].sum()
                        
                        fig_detraibili = go.Figure(data=[
                            go.Pie(labels=['Detraibili', 'Non Detraibili'], 
                                  values=[detraibili, non_detraibili],
                                  marker_colors=['#32CD32', '#FF6347'])
                        ])
                        fig_detraibili.update_layout(title="💡 Spese Detraibili vs Non Detraibili")
                        st.plotly_chart(fig_detraibili, use_container_width=True)
                
                # Trend temporale
                st.markdown("### 📅 Trend Temporale")
                
                if not df_preventivi_filtrato.empty:
                    # Raggruppa per mese
                    df_preventivi_filtrato['mese'] = df_preventivi_filtrato['data_creazione_dt'].dt.to_period('M')
                    trend_preventivi = df_preventivi_filtrato[df_preventivi_filtrato['stato'] == 'ACCETTATO'].groupby('mese')['totale'].sum()
                    
                    if not trend_preventivi.empty:
                        fig_trend = px.line(x=trend_preventivi.index.astype(str), y=trend_preventivi.values,
                                           title="📈 Trend Entrate Mensili")
                        fig_trend.update_layout(xaxis_title="Mese", yaxis_title="Entrate (€)")
                        st.plotly_chart(fig_trend, use_container_width=True)
                
                # Report riassuntivo scaricabile
                st.markdown("### 📋 Report Riassuntivo")
                
                report_data = {
                    'Periodo': [f"{data_inizio.strftime('%d/%m/%Y')} - {data_fine.strftime('%d/%m/%Y')}"],
                    'Entrate Totali': [f"€{entrate_totali:,.2f}"],
                    'Uscite Totali': [f"€{uscite_totali:,.2f}"],
                    'Utile Lordo': [f"€{utile_lordo:,.2f}"],
                    'Margine %': [f"{margine_percentuale:.1f}%"],
                    'Preventivi Vinti': [preventivi_accettati],
                    'Pipeline': [f"€{valore_pipeline:,.2f}"],
                    'Spese Detraibili': [f"€{spese_detraibili:,.2f}"]
                }
                
                df_report = pd.DataFrame(report_data)
                st.dataframe(df_report, use_container_width=True)
                
                # Pulsante per "download" (simulato)
                if st.button("📥 Esporta Report (CSV)", type="primary"):
                    csv = df_report.to_csv(index=False)
                    st.success("Report generato! (In una versione completa, questo scaricherebbe un file CSV)")
                    st.code(csv, language="csv")
    
    with tab2:
        st.subheader("Export PDF")
        st.info("🚧 Funzionalità in sviluppo - Richiede libreria reportlab")
        
        st.markdown("""
        ### Funzionalità Previste:
        - Export preventivi in formato PDF professionale
        - Template personalizzabili con logo aziendale
        - Generazione automatica fatture
        - Download diretto dal browser
        
        ### Per Implementare:
        ```bash
        pip install reportlab
        ```
        """)
    
    with tab3:
        st.subheader("Email Automatiche")
        st.info("🚧 Funzionalità in sviluppo - Richiede configurazione SMTP")
        
        st.markdown("""
        ### Funzionalità Previste:
        - Invio automatico preventivi via email
        - Template email personalizzabili
        - Allegati PDF automatici
        - Promemoria scadenze clienti
        
        ### Per Implementare:
        - Configurazione server SMTP (Gmail/Outlook)
        - Gestione credenziali sicure
        - Template HTML per email
        """)

# DEMO
elif menu == "Demo":
    st.header("🎯 Demo e Test")
    
    st.markdown("""
    ### Carica Dati Demo
    
    Clicca il pulsante per caricare dati di esempio e testare tutte le funzionalità:
    - 3 clienti di esempio (costruzioni, legale, impianti)
    - 3 preventivi con stati diversi
    - 4 spese di esempio con categorie diverse
    - Statistiche realistiche
    """)
    
    if st.button("🎮 Carica Dati Demo", type="primary"):
        carica_dati_demo()
        st.success("Dati demo caricati con successo!")
        st.balloons()
        st.rerun()
    
    # Info su Streamlit
    st.markdown("""
    ### Nuove Funzionalità Aggiunte:
    
    - **📝 Nota Spese**: Gestione completa delle spese aziendali
    - **📊 Analytics Spese**: Grafici per categoria e progetto
    - **⏰ Scadenze & Promemoria**: Sistema completo di gestione scadenze
    - **📈 Dashboard Scadenze**: Alert colorati e priorità
    - **📅 Calendario Lavori**: Vista calendario mensile e planning progetti
    - **🎯 Timeline Progetti**: Organizzazione eventi per preventivo
    - **🏢 Sezione Amministrazione**: Organizzazione modulare completa
    - **🔄 Dashboard Aggiornata**: Include totale spese
    
    ### Prossimi Sviluppi:
    - 📄 Export PDF automatico
    - 📧 Invio email preventivi
    - 💾 Database persistente
    """)

# Footer
st.markdown("""
---
**TALENTO AI SUITE** - Versione Streamlit Plus | Creato da Giancarlo Tonon

""")
