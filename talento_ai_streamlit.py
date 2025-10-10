import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import os

# --- 1. CONFIGURAZIONE DATABASE (DB) ---

# Connessione al database
def get_db_connection():
    try:
        # Recupera le variabili d'ambiente di Supabase (o un altro PostgreSQL DB)
        # Queste variabili d'ambiente devono essere settate nell'ambiente Streamlit Cloud (o .env se locale)
        conn = psycopg2.connect(
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT")
        )
        return conn
    except Exception as e:
        st.error(f"Errore di connessione al database: {e}")
        return None

# --- 2. FUNZIONI DI SALVATAGGIO (CUD) ---

def save_nuovo_cliente(nome, referente, email, telefono):
    conn = get_db_connection()
    if conn is None: return False
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO clienti (nome, referente, email, telefono) VALUES (%s, %s, %s, %s)""",
            (nome, referente, email, telefono)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Errore durante il salvataggio del cliente: {e}")
        conn.rollback()
        return False
    
def save_nuovo_preventivo(cliente_id, descrizione, valore, stato, margine):
    conn = get_db_connection()
    if conn is None: return False
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO preventivi (cliente_id, descrizione, valore, stato, margine, data_creazione) 
            VALUES (%s, %s, %s, %s, %s, NOW())
            """,
            (cliente_id, descrizione, valore, stato, margine)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Errore durante il salvataggio del preventivo: {e}")
        conn.rollback()
        return False

def save_nuova_spesa(descrizione, importo, categoria, data):
    conn = get_db_connection()
    if conn is None: return False
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO spese (descrizione, importo, categoria, data) 
            VALUES (%s, %s, %s, %s)
            """,
            (descrizione, importo, categoria, data)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Errore durante il salvataggio della spesa: {e}")
        conn.rollback()
        return False

# --- 3. FUNZIONI DI CARICAMENTO (READ) ---

def fetch_clienti():
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        return pd.read_sql("SELECT id, nome, referente, email, telefono FROM clienti ORDER BY id DESC", conn)
    except Exception as e:
        st.error(f"Errore durante il caricamento dei clienti: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def fetch_preventivi():
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        query = """
        SELECT 
            p.id, p.cliente_id, c.nome AS nome_cliente, p.descrizione, p.valore, p.stato, p.margine, p.data_creazione
        FROM preventivi p
        JOIN clienti c ON p.cliente_id = c.id
        ORDER BY p.id DESC
        """
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Errore durante il caricamento dei preventivi: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def fetch_spese():
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        return pd.read_sql("SELECT id, descrizione, importo, categoria, data FROM spese ORDER BY id DESC", conn)
    except Exception as e:
        st.error(f"Errore durante il caricamento delle spese: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# --- 4. FUNZIONE DATI DEMO ---

def carica_dati_demo():
    """Carica dati demo direttamente nel database."""
    
    # Per semplicità, i dati demo sono codificati qui. 
    # NOTA: Per un uso reale, si dovrebbe prima pulire le tabelle.

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
    # Questa parte è dipendente dal fatto che i clienti siano stati creati.
    save_nuovo_preventivo(1, "Progetto Ristrutturazione Uffici", 55000.00, "ACCETTATO", 0.35)
    save_nuovo_preventivo(2, "Consulenza Contrattuale", 8200.00, "INVIATO", 0.70)
    
    # SPESE DEMO
    # NOTA: L'import di datetime in questa funzione risolve l'ultimo errore
    save_nuova_spesa("Caffè e fornitura ufficio", 120.50, "Ufficio", datetime.now().strftime("%Y-%m-%d"))
    save_nuova_spesa("Hosting Supabase", 25.00, "Software", datetime.now().strftime("%Y-%m-%d"))

    st.success("Dati demo caricati nel database con successo!")
    st.rerun()

# --- CARICAMENTO DATI PERMANENTI ---

# Carica i dati dal DB all'avvio o al refresh dell'app.
# Utilizza la cache per velocizzare le operazioni
@st.cache_data(ttl=600)
def load_data():
    clienti_df = fetch_clienti()
    preventivi_df = fetch_preventivi()
    spese_df = fetch_spese()
    return clienti_df, preventivi_df, spese_df

clienti_df, preventivi_df, spese_df = load_data()


# --- INTERFACCIA UTENTE ---

st.set_page_config(layout="wide")

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


# --- 5. DASHBOARD ---

if menu == "Dashboard":
    st.header("Dashboard Aziendale")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Preventivi Accettati
        accettati = preventivi_df[preventivi_df['stato'] == 'ACCETTATO']
        valore_accettato = accettati['valore'].sum() if not accettati.empty else 0
        st.metric("Valore Contratti Accettati", f"€ {valore_accettato:,.2f}", delta_color="normal")

    with col2:
        # Margine Medio
        margine_medio = preventivi_df['margine'].mean() if not preventivi_df.empty else 0
        st.metric("Margine Medio", f"{margine_medio*100:.1f}%", delta_color="normal")

    with col3:
        # Spese totali
        spese_totali = spese_df['importo'].sum() if not spese_df.empty else 0
        st.metric("Spese Totali (Anno)", f"- € {spese_totali:,.2f}", delta_color="inverse")
        
    st.markdown("---")
    
    # Visualizzazione Preventivi per Stato
    st.subheader("Ripartizione Preventivi per Stato")
    if not preventivi_df.empty:
        stato_counts = preventivi_df['stato'].value_counts()
        st.bar_chart(stato_counts)
    else:
        st.info("Nessun dato preventivo disponibile. Carica i dati demo!")

# --- 6. GESTIONE CLIENTI ---

elif menu == "Gestione Clienti":
    st.header("Anagrafica Clienti")
    
    # Form per Aggiungere Cliente
    with st.expander("➕ Aggiungi Nuovo Cliente"):
        with st.form("form_cliente"):
            st.subheader("Dettagli Nuovo Cliente")
            
            # Input fields per i dati del cliente
            nome = st.text_input("Nome Azienda *")
            referente = st.text_input("Nome Referente")
            email = st.text_input("Email")
            telefono = st.text_input("Telefono")
            
            # Pulsante di invio del form
            if st.form_submit_button("Salva Cliente", type="primary"):
                if nome:
                    # Chiamata alla funzione di salvataggio DB
                    if save_nuovo_cliente(nome, referente, email, telefono):
                        st.success(f"Cliente '{nome}' salvato in modo permanente!")
                        load_data.clear() # Cancella la cache per forzare il ricaricamento
                        st.rerun()
                else:
                    st.error("Il Nome Azienda è obbligatorio.")
    
    st.markdown("---")
    
    # Visualizzazione Tabella Clienti
    st.subheader("Elenco Clienti")
    if not clienti_df.empty:
        # Visualizzazione interattiva
        st.dataframe(clienti_df.set_index('id'))
    else:
        st.info("Nessun cliente registrato.")


# --- 7. GESTIONE PREVENTIVI ---

elif menu == "Gestione Preventivi":
    st.header("Registro Preventivi")
    
    # Form per Aggiungere Preventivo
    with st.expander("📝 Crea Nuovo Preventivo"):
        if clienti_df.empty:
            st.warning("Devi registrare almeno un cliente prima di creare un preventivo.")
        else:
            with st.form("form_preventivo"):
                st.subheader("Dettagli Preventivo")
                
                # Input per il Cliente (collega al DF dei clienti)
                clienti_map = dict(zip(clienti_df['nome'], clienti_df['id']))
                cliente_selezionato = st.selectbox("Cliente *", options=list(clienti_map.keys()))
                cliente_id = clienti_map.get(cliente_selezionato)

                descrizione = st.text_area("Descrizione Lavoro *")
                valore = st.number_input("Valore Totale € *", min_value=0.0, step=100.0)
                stato = st.selectbox("Stato", ["INVIATO", "ACCETTATO", "RIFIUTATO", "IN LAVORAZIONE"])
                margine = st.slider("Margine Atteso (%)", 0.0, 1.0, 0.4, 0.05, format="%.2f") # Margine 0-1 (0% - 100%)
                
                # Pulsante di invio del form
                if st.form_submit_button("Crea Preventivo", type="primary"):
                    if descrizione and valore > 0 and cliente_id:
                        # Chiamata alla funzione di salvataggio DB
                        if save_nuovo_preventivo(cliente_id, descrizione, valore, stato, margine):
                            st.success("Preventivo creato e salvato in modo permanente!")
                            load_data.clear()
                            st.rerun()
                    else:
                        st.error("Cliente, Descrizione e Valore sono obbligatori.")

    st.markdown("---")

    # Visualizzazione Tabella Preventivi
    st.subheader("Elenco Preventivi")
    if not preventivi_df.empty:
        # Preparazione del DataFrame per la visualizzazione
        display_df = preventivi_df.copy()
        display_df['valore'] = display_df['valore'].apply(lambda x: f"€ {x:,.2f}")
        display_df['margine'] = display_df['margine'].apply(lambda x: f"{x*100:.1f}%")
        
        # Colonne da mostrare
        cols_to_show = ['id', 'nome_cliente', 'descrizione', 'valore', 'stato', 'margine', 'data_creazione']
        
        st.dataframe(display_df[cols_to_show].set_index('id'))
    else:
        st.info("Nessun preventivo registrato.")


# --- 8. GESTIONE SPESE ---

elif menu == "Gestione Spese":
    st.header("Registro Spese")

    # Form per Aggiungere Spesa
    with st.expander("💸 Aggiungi Nuova Spesa"):
        with st.form("form_spesa"):
            st.subheader("Dettagli Spesa")

            col1, col2 = st.columns(2)
            
            with col1:
                data_spesa = st.date_input("Data Spesa", value=datetime.now())
                categoria = st.selectbox("Categoria", 
                                        ["Trasporti", "Materiali", "Formazione", "Ufficio", 
                                         "Software", "Hardware", "Consulenze", "Marketing", "Altro"])
                importo = st.number_input("Importo € *", min_value=0.0, step=0.01)
            
            with col2:
                # Progetto non mappato nel DB, mantenuto per interfaccia utente
                progetti_disponibili = ["Generale"]
                # AGGIORNAMENTO: Usa il DataFrame permanente dei preventivi
                if not preventivi_df.empty:
                    progetti_disponibili.extend([p for p in preventivi_df['descrizione']]) 
                    
                progetto = st.selectbox("Progetto/Preventivo", progetti_disponibili)
                detraibile = st.checkbox("Detraibile/Deducibile", value=True)
                ricevuta = st.selectbox("Ricevuta", ["Si", "No"])
            
            descrizione = st.text_area("Descrizione Spesa *")
            
            if st.form_submit_button("Aggiungi Spesa", type="primary"):
                # Questa riga era la causa dell'errore di indentazione nei tentativi precedenti!
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
                        load_data.clear()
                        st.rerun()
                else:
                    st.error("Importo e descrizione sono obbligatori!")

    st.markdown("---")
    
    # Visualizzazione Tabella Spese
    st.subheader("Elenco Spese")
    if not spese_df.empty:
        display_df = spese_df.copy()
        display_df['importo'] = display_df['importo'].apply(lambda x: f"€ {x:,.2f}")
        
        # Rimuove l'ID che non è essenziale per la visualizzazione finale
        cols_to_show = ['data', 'categoria', 'descrizione', 'importo']
        
        st.dataframe(display_df[cols_to_show].set_index('data'))
    else:
        st.info("Nessuna spesa registrata.")


Esegui il **Commit changes** su GitHub. Sono convinto che questa volta l'app funzionerà perfettamente. Per favore, fammi sapere se riesci ad avviarla e a usare il bottone "Carica Dati Demo".
