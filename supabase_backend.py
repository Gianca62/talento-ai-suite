import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

class SupabaseManager:
    """Gestisce tutte le operazioni con Supabase"""
    
    def __init__(self):
        """Inizializza la connessione a Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devono essere configurati")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    def test_connection(self):
        """Testa la connessione a Supabase"""
        try:
            response = self.supabase.table("clienti").select("count", count="exact").execute()
            return True
        except Exception as e:
            print(f"Errore connessione: {e}")
            return False
    
    # ==================== CLIENTI ====================
    
    def add_cliente(self, cliente):
        """Aggiunge un nuovo cliente"""
        try:
            response = self.supabase.table("clienti").insert(cliente).execute()
            return True
        except Exception as e:
            print(f"Errore add_cliente: {e}")
            return False
    
    def get_clienti(self):
        """Recupera tutti i clienti"""
        try:
            response = self.supabase.table("clienti").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Errore get_clienti: {e}")
            return []
    
    def update_cliente(self, cliente_id, updates):
        """Aggiorna un cliente esistente"""
        try:
            response = self.supabase.table("clienti").update(updates).eq("id", cliente_id).execute()
            return True
        except Exception as e:
            print(f"Errore update_cliente: {e}")
            return False
    
    def delete_cliente(self, cliente_id):
        """Elimina un cliente"""
        try:
            response = self.supabase.table("clienti").delete().eq("id", cliente_id).execute()
            return True
        except Exception as e:
            print(f"Errore delete_cliente: {e}")
            return False
    
    # ==================== PREVENTIVI ====================
    
    def add_preventivo(self, preventivo):
        """Aggiunge un nuovo preventivo"""
        try:
            response = self.supabase.table("preventivi").insert(preventivo).execute()
            return True
        except Exception as e:
            print(f"Errore add_preventivo: {e}")
            return False
    
    def get_preventivi(self):
        """Recupera tutti i preventivi"""
        try:
            response = self.supabase.table("preventivi").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Errore get_preventivi: {e}")
            return []
    
    def update_preventivo(self, preventivo_id, updates):
        """Aggiorna un preventivo esistente"""
        try:
            response = self.supabase.table("preventivi").update(updates).eq("id", preventivo_id).execute()
            return True
        except Exception as e:
            print(f"Errore update_preventivo: {e}")
            return False
    
    def delete_preventivo(self, preventivo_id):
        """Elimina un preventivo"""
        try:
            response = self.supabase.table("preventivi").delete().eq("id", preventivo_id).execute()
            return True
        except Exception as e:
            print(f"Errore delete_preventivo: {e}")
            return False
    
    # ==================== SPESE ====================
    
    def add_spesa(self, spesa):
        """Aggiunge una nuova spesa"""
        try:
            response = self.supabase.table("spese").insert(spesa).execute()
            return True
        except Exception as e:
            print(f"Errore add_spesa: {e}")
            return False
    
    def get_spese(self):
        """Recupera tutte le spese"""
        try:
            response = self.supabase.table("spese").select("*").order("data", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Errore get_spese: {e}")
            return []
    
    def update_spesa(self, spesa_id, updates):
        """Aggiorna una spesa esistente"""
        try:
            response = self.supabase.table("spese").update(updates).eq("id", spesa_id).execute()
            return True
        except Exception as e:
            print(f"Errore update_spesa: {e}")
            return False
    
    def delete_spesa(self, spesa_id):
        """Elimina una spesa"""
        try:
            response = self.supabase.table("spese").delete().eq("id", spesa_id).execute()
            return True
        except Exception as e:
            print(f"Errore delete_spesa: {e}")
            return False
    
    # ==================== SCADENZE ====================
    
    def add_scadenza(self, scadenza):
        """Aggiunge una nuova scadenza"""
        try:
            response = self.supabase.table("scadenze").insert(scadenza).execute()
            return True
        except Exception as e:
            print(f"Errore add_scadenza: {e}")
            return False
    
    def get_scadenze(self):
        """Recupera tutte le scadenze"""
        try:
            response = self.supabase.table("scadenze").select("*").order("data", desc=False).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Errore get_scadenze: {e}")
            return []
    
    def update_scadenza(self, scadenza_id, updates):
        """Aggiorna una scadenza esistente"""
        try:
            response = self.supabase.table("scadenze").update(updates).eq("id", scadenza_id).execute()
            return True
        except Exception as e:
            print(f"Errore update_scadenza: {e}")
            return False
    
    def delete_scadenza(self, scadenza_id):
        """Elimina una scadenza"""
        try:
            response = self.supabase.table("scadenze").delete().eq("id", scadenza_id).execute()
            return True
        except Exception as e:
            print(f"Errore delete_scadenza: {e}")
            return False
    
    # ==================== EVENTI CALENDARIO ====================
    
    def add_evento_calendario(self, evento):
        """Aggiunge un evento al calendario"""
        try:
            response = self.supabase.table("eventi_calendario").insert(evento).execute()
            return True
        except Exception as e:
            print(f"Errore add_evento_calendario: {e}")
            return False
    
    def get_eventi_calendario(self):
        """Recupera tutti gli eventi dal calendario"""
        try:
            response = self.supabase.table("eventi_calendario").select("*").order("data", desc=False).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Errore get_eventi_calendario: {e}")
            return []
    
    def update_evento_calendario(self, evento_id, updates):
        """Aggiorna un evento del calendario"""
        try:
            response = self.supabase.table("eventi_calendario").update(updates).eq("id", evento_id).execute()
            return True
        except Exception as e:
            print(f"Errore update_evento_calendario: {e}")
            return False
    
    def delete_evento_calendario(self, evento_id):
        """Elimina un evento dal calendario"""
        try:
            response = self.supabase.table("eventi_calendario").delete().eq("id", evento_id).execute()
            return True
        except Exception as e:
            print(f"Errore delete_evento_calendario: {e}")
            return False
    
    # ==================== UTILITY ====================
    
    def get_statistiche(self):
        """Recupera statistiche generali"""
        try:
            clienti = len(self.get_clienti())
            preventivi = len(self.get_preventivi())
            spese_totali = sum(s.get('importo', 0) for s in self.get_spese())
            scadenze_attive = len([s for s in self.get_scadenze() if s.get('stato') == 'Attiva'])
            eventi_programmati = len(self.get_eventi_calendario())
            
            return {
                "clienti": clienti,
                "preventivi": preventivi,
                "spese_totali": spese_totali,
                "scadenze_attive": scadenze_attive,
                "eventi_programmati": eventi_programmati
            }
        except Exception as e:
            print(f"Errore get_statistiche: {e}")
            return {}