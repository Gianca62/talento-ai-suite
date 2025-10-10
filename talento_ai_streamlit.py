import streamlit as st
import pandas as pd
from datetime import datetime
import psycopg2
from urllib.parse import urlparse

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(layout="wide", page_title="Talento AI Suite", page_icon="💼")

# --- CONNESSIONE DATABASE ---

@st.cache_resource
def get_db_connection():
    """Stabilisce e restituisce la connessione al database PostgreSQL."""
    try:
        # Usa la SECRET 'DATABASE_URL' di Streamlit (che contiene la stringa di connessione)
        url = st.secrets["database"]["url"]
        
        # Analizza l'URL per estrarre i componenti
        result = urlparse(url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        # Connessione
        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        return conn
    except Exception as e:
        # st.error(f"Errore di connessione al database: {e}")
        return None

def initialize_database():
    """Crea le tabelle del database se non esistono."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            # Tabella Clienti
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clienti (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    referente TEXT,
                    email TEXT,
                    telefono TEXT,
                    data_creazione DATE DEFAULT CURRENT_DATE
                );
            """)
            
            # Tabella Preventivi
            cur.execute("""
                CREATE TABLE IF NOT EXISTS preventivi (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER REFERENCES clienti(id),
                    titolo TEXT NOT NULL,
                    valore NUMERIC(10, 2),
                    stato TEXT,
                    probabilita NUMERIC(3, 2),
                    data_creazione DATE DEFAULT CURRENT_DATE
                );
            """)

            # Tabella Spese
            cur.execute("""
                CREATE TABLE IF NOT EXISTS spese (
                    id SERIAL PRIMARY KEY,
                    descrizione TEXT NOT NULL,
                    importo NUMERIC(10, 2),
                    categoria TEXT,
                    data_spesa DATE,
                    data_registrazione DATE DEFAULT CURRENT_DATE
                );
            """)
            
            conn.commit()
            # st.success("Database inizializzato con successo.")
        except Exception as e:
            st.error(f"Errore durante l'inizializzazione del database: {e}")
        finally:
            conn.close()

# Inizializza il database all'avvio dell'app
initialize_database()

# --- FUNZIONI FETCH (Lettura Dati) ---

@st.cache_data(ttl=60) # Caching dei risultati per 60 secondi
def fetch_clienti():
    """Recupera tutti i clienti dal database e li restituisce come DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql("SELECT * FROM clienti ORDER BY id DESC", conn)
            return df
        except Exception as e:
            st.error(f"Errore SQL recupero clienti: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_preventivi():
    """Recupera tutti i preventivi (con nome cliente) e li restituisce come DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            query = """
                SELECT 
                    p.id, 
                    c.nome AS nome_cliente, 
                    p.titolo, 
                    p.valore, 
                    p.stato, 
                    p.probabilita, 
                    p.data_creazione
                FROM 
                    preventivi p
                JOIN 
                    clienti c ON p.cliente_id = c.id
                ORDER BY 
                    p.data_creazione DESC;
            """
            df = pd.read_sql(query, conn)
            # Conversione della probabilità da float a percentuale
            if 'probabilita' in df.columns:
                 df['probabilita'] = df['probabilita'].apply(lambda x: f"{x*100:.0f}%" if pd.notna(x) else "0%")
            return df
        except Exception as e:
            st.error(f"Errore SQL recupero preventivi: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_spese():
    """Recupera tutte le spese dal database e le restituisce come DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql("SELECT * FROM spese ORDER BY data_spesa DESC", conn)
            # Rinomina la colonna data_spesa in 'data' per la visualizzazione
            if 'data_spesa' in df.columns:
                df.rename(columns={'data_spesa': 'data'}, inplace=True)
            return df
        except Exception as e:
            st.error(f"Errore SQL recupero spese: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

# --- FUNZIONI SAVE (Scrittura Dati) ---

def save_nuovo_cliente(nome, referente, email, telefono):
    """Salva un nuovo cliente nel database."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO clienti (nome, referente, email, telefono) 
                   VALUES (%s, %s, %s, %s)""", 
                (nome, referente, email, telefono)
            )
            conn.commit()
            # Invalida la cache per forzare il ricaricamento dei clienti
            fetch_clienti.clear() 
            return True
        except Exception as e:
            st.error(f"Errore SQL salvataggio cliente: {e}")
            return False
        finally:
            conn.close()
    return False

def save_nuovo_preventivo(cliente_id, titolo, valore, stato, probabilita):
    """Salva un nuovo preventivo nel database."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # La probabilità viene salvata come decimale (es. 0.50)
            probabilita_decimale = probabilita 
            cur.execute(
                """INSERT INTO preventivi (cliente_id, titolo, valore, stato, probabilita) 
                   VALUES (%s, %s, %s, %s, %s)""", 
                (cliente_id, titolo, valore, stato, probabilita_decimale)
            )
            conn.commit()
            fetch_preventivi.clear()
            return True
        except Exception as e:
            st.error(f"Errore SQL salvataggio preventivo: {e}")
            return False
        finally:
            conn.close()
    return False

def save_nuova_spesa(descrizione, importo, categoria, data_spesa_str):
    """Salva una nuova spesa nel database. data_spesa_str è in formato YYYY-MM-DD."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO spese (descrizione, importo, categoria, data_spesa) 
                   VALUES (%s, %s, %s, %s)""", 
                (descrizione, importo, categoria, data_spesa_str)
            )
            conn.commit()
            fetch_spese.clear()
            return True
        except Exception as e:
            st.error(f"Errore SQL salvataggio spesa: {e}")
            return False
        finally:
            conn.close()
    return False

def save_aggiorna_stato_preventivo(preventivo_id, nuovo_stato):
    """Aggiorna lo stato di un preventivo nel database."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """UPDATE preventivi 
                   SET stato = %s 
                   WHERE id = %s""", 
                (nuovo_stato, int(preventivo_id))
            )
            conn.commit()
            fetch_preventivi.clear() # Invalida la cache
            return True
        except Exception as e:
            st.error(f"Errore SQL aggiornamento stato: {e}")
            return False
        finally:
            conn.close()
    return False


# --- FUNZIONE DEMO (Aggiornata per usare il DB) ---

def carica_dati_demo():
    """Carica dati demo direttamente nel database."""
    
    # Pulizia dati vecchi (opzionale, ma utile per i demo)
    # Per semplicità non implementiamo il truncate qui, ma inseriamo solo i dati
    
    # CLIENTE DEMO 1: Rossi Costruzioni
    save_nuovo_cliente(
        "Rossi Costruzioni SRL",
        "Marco Rossi",
        "info@rossicost.it",
        "0421-123456"
    )
    
    # CLIENTE DEMO 2: Studio Legale Bianchi
    save_nuovo_cliente(
        "Studio Legale Bianchi",
        "Avv. Bianchi",
        "avv.bianchi@legal.it",
        "339-987654"
    )

    # PREVENTIVI DEMO (Assumiamo che i primi due clienti abbiano ID 1 e 2)
    # Questa parte richiede che i clienti ID 1 e 2 esistano.
    save_nuovo_preventivo(1, "Progetto Ristrutturazione Uffici", 55000.00, "ACCETTATO", 0.35)
    save_nuovo_preventivo(2, "Consulenza Contrattuale", 8200.00, "INVIATO", 0.70)
    
    # SPESE DEMO
    save_nuova_spesa("Caffè e fornitura ufficio", 120.50, "Ufficio", datetime.now().strftime("%Y-%m-%d"))
    save_nuova_spesa("Hosting Supabase", 25.00, "Software", datetime.now().strftime("%Y-%m-%d"))

    st.success("Dati demo caricati nel database con successo!")
    st.rerun()

# --- CARICAMENTO DATI PERMANENTI ---

# Carica i dati dal DB all'avvio o al refresh dell'app.
clienti_df = fetch_clienti()
preventivi_df = fetch_preventivi()
spese_df = fetch_spese()

# --- INTERFACCIA UTENTE ---

# SIDEBAR (Menu e Statistiche)
with st.sidebar:
    st.title("💼 Talento AI Suite")
    
    # Menu di Navigazione
    menu = st.radio("Navigazione", ["Dashboard", "Gestione Clienti", "Gestione Preventivi", "Gestione Spese"])
    
    st.markdown("---")
    
    st.subheader("Statistiche Rapide")
    
    # Statistiche Clienti
    num_clienti = len(clienti_df)
    st.metric("Clienti Totali", num_clienti)
    
    # Statistiche Preventivi
    valore_totale = preventivi_df['valore'].sum() if not preventivi_df.empty else 0
    st.metric("Valore Preventivi Totale", f"€ {valore_totale:,.2f}")
    
    # Statistiche Demo
    st.markdown("---")
    if st.button("Carica Dati Demo"):
        carica_dati_demo()

# --- LOGICA DASHBOARD ---
if menu == "Dashboard":
    st.header("Dashboard Aziendale")
    
    col1, col2, col3 = st.columns(3)
    
    # Card 1: Valore in Pipeline
    valore_pipeline = preventivi_df[preventivi_df['stato'] == 'INVIATO']['valore'].sum() if not preventivi_df.empty else 0
    col1.metric("Valore in Pipeline", f"€ {valore_pipeline:,.0f}", delta_color="normal")
    
    # Card 2: Preventivi Accettati
    valore_accettato = preventivi_df[preventivi_df['stato'] == 'ACCETTATO']['valore'].sum() if not preventivi_df.empty else 0
    col2.metric("Valore Accettato", f"€ {valore_accettato:,.0f}", delta_color="inverse")
    
    # Card 3: Spese Mensili
    # (Per semplicità, usiamo le spese totali)
    spese_totali = spese_df['importo'].sum() if not spese_df.empty else 0
    col3.metric("Spese Totali (dal DB)", f"€ {spese_totali:,.0f}", delta_color="inverse")
    
    st.markdown("---")
    
    # Grafico Preventivi per Stato
    st.subheader("Ripartizione Preventivi per Stato")
    
    if not preventivi_df.empty:
        stati_count = preventivi_df.groupby('stato')['valore'].sum().reset_index()
        stati_count.columns = ['Stato', 'Valore']
        
        # Mappa per colori coerenti
        color_map = {
            'BOZZA': '#adb5bd',
            'INVIATO': '#495057',
            'ACCETTATO': '#28a745',
            'RIFIUTATO': '#dc3545'
        }
        
        st.bar_chart(stati_count.set_index('Stato'), color=['#42494F'])
    else:
        st.info("Nessun dato sui preventivi da visualizzare.")

# --- LOGICA GESTIONE CLIENTI ---
elif menu == "Gestione Clienti":
    st.header("Gestione Clienti")
    
    tab1, tab2 = st.tabs(["Lista Clienti", "Aggiungi Cliente"])
    
    with tab1:
        st.subheader("Elenco Clienti")
        if not clienti_df.empty:
            # Selezione e visualizzazione colonne
            clienti_df_display = clienti_df[['nome', 'referente', 'email', 'telefono', 'data_creazione']].copy()
            st.dataframe(clienti_df_display, use_container_width=True)
        else:
            st.info("Nessun cliente registrato.")
            
    with tab2:
        st.subheader("Nuovo Cliente")
        with st.form("nuovo_cliente_form"):
            col_a, col_b = st.columns(2)
            nome = col_a.text_input("Nome Azienda/Cliente*")
            referente = col_b.text_input("Nome Referente")
            email = col_a.text_input("Email")
            telefono = col_b.text_input("Telefono")
            
            if st.form_submit_button("Salva Cliente", type="primary"):
                if nome:
                    if save_nuovo_cliente(nome, referente, email, telefono):
                        st.success(f"Cliente '{nome}' salvato con successo nel database!")
                        st.rerun()
                    else:
                        st.error("Errore nel salvataggio del cliente. Controlla la connessione al DB.")
                else:
                    st.error("Il nome del cliente è obbligatorio.")

# --- LOGICA GESTIONE PREVENTIVI ---
elif menu == "Gestione Preventivi":
    st.header("Gestione Preventivi")
    
    tab1, tab2 = st.tabs(["Lista Preventivi", "Crea Nuovo Preventivo"])
    
    with tab1:
        st.subheader("Lista Completa")
        
        if not preventivi_df.empty:
            # Mappatura per rinominare le colonne per la visualizzazione
            colonne_display = {
                'nome_cliente': 'Cliente',
                'titolo': 'Titolo Preventivo',
                'valore': 'Valore (€)',
                'stato': 'Stato',
                'probabilita': 'Probabilità',
                'data_creazione': 'Data Creazione'
            }
            preventivi_df_display = preventivi_df.rename(columns=colonne_display)

            # Aggiungi un selettore per filtrare per stato
            stati_filtro = st.multiselect(
                "Filtra per Stato",
                preventivi_df_display['Stato'].unique().tolist(),
                default=preventivi_df_display['Stato'].unique().tolist()
            )

            df_filtrato = preventivi_df_display[preventivi_df_display['Stato'].isin(stati_filtro)]
            
            # Funzionalità di aggiornamento stato (nuova logica DB)
            if not df_filtrato.empty:
                # Mostra il DataFrame con la colonna per il pulsante
                edited_df = st.data_editor(
                    df_filtrato,
                    column_config={
                        "azione": st.column_config.SelectboxColumn(
                            "Aggiorna Stato",
                            help="Seleziona il nuovo stato e premi invio",
                            options=["ACCETTATO", "RIFIUTATO", "INVIATO", "BOZZA"],
                            required=True,
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    num_rows="dynamic"
                )
                
                # Logica di salvataggio aggiornata per il DB
                # Troviamo la riga che è stata modificata (Streamlit non lo fa automaticamente con data_editor)
                stati_originali = df_filtrato['Stato'].tolist()
                stati_modificati = edited_df['azione'].tolist() if 'azione' in edited_df.columns else edited_df['Stato'].tolist()

                # Controlla se una riga è stata modificata e se lo stato è cambiato
                for i in range(len(stati_originali)):
                    nuovo_stato = stati_modificati[i]
                    id_preventivo = edited_df.loc[edited_df.index[i], 'id']
                    
                    # Se lo stato è stato effettivamente modificato dall'utente
                    if 'azione' in edited_df.columns and nuovo_stato != stati_originali[i] and nuovo_stato != edited_df.loc[edited_df.index[i], 'Stato']:
                         
                        if save_aggiorna_stato_preventivo(id_preventivo, nuovo_stato):
                            st.success(f"Stato preventivo ID {id_preventivo} aggiornato a '{nuovo_stato}' nel database!")
                            st.rerun()
                        else:
                            st.error("Errore nell'aggiornamento dello stato del preventivo.")
                        break # Processa una modifica alla volta per evitare errori di concorrenza
                
            else:
                 st.info("Nessun preventivo corrisponde ai filtri.")

        else:
            st.info("Nessun preventivo registrato.")

    with tab2:
        st.subheader("Nuovo Preventivo")
        
        if clienti_df.empty:
            st.warning("Devi prima aggiungere un cliente nella sezione 'Gestione Clienti'.")
        else:
            # Mappa i nomi dei clienti ai loro ID per il salvataggio
            clienti_map = dict(zip(clienti_df['nome'], clienti_df['id']))
            clienti_nomi = clienti_df['nome'].tolist()
            
            with st.form("nuovo_preventivo_form"):
                
                cliente_selezionato = st.selectbox("Seleziona Cliente*", clienti_nomi)
                titolo = st.text_input("Titolo / Descrizione Breve*")
                
                col_c, col_d, col_e = st.columns(3)
                
                valore = col_c.number_input("Valore (€)*", min_value=0.0, step=100.0)
                stato = col_d.selectbox("Stato", ["BOZZA", "INVIATO", "ACCETTATO", "RIFIUTATO"])
                probabilita_perc = col_e.slider("Probabilità di Chiusura (%)", 0, 100, 50)
                
                if st.form_submit_button("Crea Preventivo", type="primary"):
                    if titolo and valore > 0:
                        cliente_id = clienti_map[cliente_selezionato]
                        probabilita_decimale = probabilita_perc / 100.0
                        
                        if save_nuovo_preventivo(cliente_id, titolo, valore, stato, probabilita_decimale):
                            st.success(f"Preventivo '{titolo}' creato con successo!")
                            st.rerun()
                        else:
                            st.error("Errore nel salvataggio del preventivo. Controlla la connessione al DB.")
                    else:
                        st.error("Titolo e Valore sono obbligatori.")

# --- LOGICA GESTIONE SPESE ---
elif menu == "Gestione Spese":
    st.header("Gestione Spese e Cash Flow")
    
    col_vis, col_add = st.columns([2, 1])

    with col_vis:
        st.subheader("Lista Spese")
        
        if not spese_df.empty:
            df_filtrato = spese_df.copy() # Usiamo il DataFrame permanente caricato dal DB

            # Filtri
            col_f, col_g = st.columns(2)
            with col_f:
                categorie_filtro = st.multiselect("Filtra per categoria:", 
                                                 df_filtrato['categoria'].unique().tolist(),
                                                 default=df_filtrato['categoria'].unique().tolist())
            
            df_filtrato = df_filtrato[df_filtrato['categoria'].isin(categorie_filtro)]
            
            st.dataframe(df_filtrato, use_container_width=True, hide_index=True)

        else:
            st.info("Nessuna spesa registrata. Aggiungi la prima spesa!")

    with col_add:
        st.subheader("Aggiungi Spesa")
        
        with st.form("form_spesa"):
            
            data_spesa = st.date_input("Data Spesa", value=datetime.now())
            categoria = st.selectbox("Categoria", 
                                     ["Trasporti", "Materiali", "Formazione", "Ufficio", 
                                      "Software", "Hardware", "Consulenze", "Marketing", "Altro"])
            importo = st.number_input("Importo €", min_value=0.0, step=0.01)
            
            # Dati aggiuntivi (non salvati nel DB per semplicità, ma lasciati per il form)
            progetti_disponibili = ["Generale"]
            if not preventivi_df.empty:
                progetti_disponibili.extend(preventivi_df['titolo'].tolist())
            
            progetto = st.selectbox("Progetto/Preventivo", progetti_disponibili)
            detraibile = st.checkbox("Detraibile/Deducibile", value=True)
            ricevuta = st.selectbox("Ricevuta", ["Si", "No"])
            
            descrizione = st.text_area("Descrizione Spesa")
            
            # Logica di salvataggio (Indentazione corretta e chiamata al DB)
            if st.form_submit_button("Aggiungi Spesa", type="primary"):
                if importo > 0 and descrizione:
                    
                    # Converitiamo la data nel formato richiesto dal database (YYYY-MM-DD)
                    data_db = data_spesa.strftime("%Y-%m-%d")
                    
                    # Call the function to save the new expense to the database
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


