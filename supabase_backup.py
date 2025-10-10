import streamlit as st
from supabase import create_client, Client
from typing import List, Dict, Any

class SupabaseManager:
    def __init__(self):
        # Configurazione Supabase
        self.url = st.secrets["SUPABASE_URL"]
        self.key = st.secrets["SUPABASE_ANON_KEY"]
        self.supabase: Client = create_client(self.url, self.key)
    
    # === GESTIONE CLIENTI ===
    def get_clienti(self) -> List[Dict]:
        """Recupera tutti i clienti"""
        try:
            response = self.supabase.table('clienti').select("*").execute()
            return response.data
        except Exception as e:
            st.error(f"Errore nel recuperare clienti: {e}")
            return []
    
    def add_cliente(self, cliente_data: Dict) -> bool:
        """Aggiunge un nuovo cliente"""
        try:
            response = self.supabase.table('clienti').insert(cliente_data).execute()
            return True
        except Exception as e:
            st.error(f"Errore nell'aggiungere cliente: {e}")
            return False
    
    # === GESTIONE PREVENTIVI ===
    def get_preventivi(self) -> List[Dict]:
        """Recupera tutti i preventivi"""
        try:
            response = self.supabase.table('preventivi').select("*").execute()
            return response.data
        except Exception as e:
            st.error(f"Errore nel recuperare preventivi: {e}")
            return []
    
    def add_preventivo(self, preventivo_data: Dict) -> bool:
        """Aggiunge un nuovo preventivo"""
        try:
            response = self.supabase.table('preventivi').insert(preventivo_data).execute()
            return True
        except Exception as e:
            st.error(f"Errore nell'aggiungere preventivo: {e}")
            return False
    
    def update_stato_preventivo(self, preventivo_numero: str, nuovo_stato: str) -> bool:
        """Aggiorna lo stato di un preventivo"""
        try:
            response = self.supabase.table('preventivi').update({'stato': nuovo_stato}).eq('numero', preventivo_numero).execute()
            return True
        except Exception as e:
            st.error(f"Errore nell'aggiornare stato preventivo: {e}")
            return False
    
    # === UTILITY ===
    def test_connection(self) -> bool:
        """Testa la connessione a Supabase"""
        try:
            response = self.supabase.table('clienti').select("count", count="exact").execute()
            return True
        except Exception as e:
            st.error(f"Errore di connessione a Supabase: {e}")
            return False
    
    def init_demo_data(self):
        """Inizializza dati demo nel database"""
        # Clienti demo
        clienti_demo = [
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
        preventivi_demo = [
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
        
        # Inserisci dati demo
        for cliente in clienti_demo:
            self.add_cliente(cliente)
        
        for preventivo in preventivi_demo:
            self.add_preventivo(preventivo)