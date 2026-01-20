#!/usr/bin/env python3
"""
Script per scaricare i dati sulla qualità dell'aria dalla provincia di Varese.
Fonte: Open Data Regione Lombardia (API Socrata)

Datasets utilizzati:
- Stazioni: https://www.dati.lombardia.it/resource/ib47-atvt.json
- Dati sensori: https://www.dati.lombardia.it/resource/nicp-bhqi.json
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configurazione
BASE_URL = "https://www.dati.lombardia.it/resource"
STAZIONI_ENDPOINT = f"{BASE_URL}/ib47-atvt.json"
DATI_ENDPOINT = f"{BASE_URL}/nicp-bhqi.json"
PROVINCIA = "VA"

# Mapping nomi inquinanti dall'API ai nomi standard
INQUINANTI_NORMALIZZATI = {
    "PM10": "PM10",
    "PM2.5": "PM2.5",
    "Particelle sospese PM2.5": "PM2.5",
    "Biossido di Azoto": "NO2",
    "Ossidi di Azoto": "NO2"
}

# Soglie per i colori
SOGLIE = {
    "PM10": {"verde": 35, "giallo": 50},
    "PM2.5": {"verde": 20, "giallo": 25},
    "NO2": {"verde": 100, "giallo": 200}
}

# Directory di output
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DOCS_DIR = SCRIPT_DIR.parent / "docs"
DATA_DIR.mkdir(exist_ok=True)


def fetch_stazioni():
    """Scarica l'elenco delle stazioni della provincia di Varese."""
    print(f"Scaricamento stazioni provincia {PROVINCIA}...")
    
    params = {
        "$where": f"provincia='{PROVINCIA}'",
        "$limit": 1000
    }
    
    response = requests.get(STAZIONI_ENDPOINT, params=params, timeout=60)
    response.raise_for_status()
    stazioni = response.json()
    
    stazioni_filtrate = []
    for s in stazioni:
        tipo_sensore = s.get("nometiposensore", "")
        
        inquinante_norm = None
        for key, value in INQUINANTI_NORMALIZZATI.items():
            if key in tipo_sensore:
                inquinante_norm = value
                break
        
        if inquinante_norm:
            stazioni_filtrate.append({
                "idsensore": s.get("idsensore"),
                "idstazione": s.get("idstazione"),
                "nomestazione": s.get("nomestazione"),
                "comune": s.get("comune"),
                "provincia": s.get("provincia"),
                "inquinante": inquinante_norm,
                "unitamisura": s.get("unitamisura", "µg/m³"),
                "lat": s.get("lat"),
                "lng": s.get("lng")
            })
    
    print(f"Trovate {len(stazioni_filtrate)} stazioni/sensori per {PROVINCIA}")
    return stazioni_filtrate


def fetch_dati_sensore(idsensore, data_inizio, data_fine):
    """Scarica i dati di un sensore per un periodo specifico."""
    params = {
        "$where": f"idsensore='{idsensore}' AND data >= '{data_inizio}' AND data <= '{data_fine}'",
        "$order": "data DESC",
        "$limit": 50000
    }
    
    response = requests.get(DATI_ENDPOINT, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def fetch_tutti_dati(stazioni, giorni=30):
    """Scarica i dati per tutte le stazioni."""
    oggi = datetime.now()
    
    data_fine = oggi.strftime("%Y-%m-%dT23:59:59")
    data_inizio_30gg = (oggi - timedelta(days=giorni)).strftime("%Y-%m-%dT00:00:00")
    data_inizio_anno = f"{oggi.year}-01-01T00:00:00"
    
    tutti_dati = []
    dati_anno = []
    
    sensori_ids = list(set(s["idsensore"] for s in stazioni))
    
    print(f"Scaricamento dati per {len(sensori_ids)} sensori...")
    
    for i, idsensore in enumerate(sensori_ids):
        print(f"  [{i+1}/{len(sensori_ids)}] Sensore {idsensore}...")
        
        try:
            dati = fetch_dati_sensore(idsensore, data_inizio_30gg, data_fine)
            tutti_dati.extend(dati)
        except Exception as e:
            print(f"    Errore dati 30gg: {e}")
        
        try:
            dati = fetch_dati_sensore(idsensore, data_inizio_anno, data_fine)
            dati_anno.extend(dati)
        except Exception as e:
            print(f"    Errore dati anno: {e}")
    
    print(f"Scaricati {len(tutti_dati)} record (ultimi {giorni} giorni)")
    print(f"Scaricati {len(dati_anno)} record (da inizio anno)")
    
    return tutti_dati, dati_anno


def calcola_superamenti(dati_anno, stazioni):
    """Calcola il numero di giorni con superamento soglia PM10 > 50 µg/m³."""
    sensore_map = {s["idsensore"]: s for s in stazioni}
    superamenti_per_stazione = {}
    
    for record in dati_anno:
        idsensore = record.get("idsensore")
        if idsensore not in sensore_map:
            continue
        
        info = sensore_map[idsensore]
        if info["inquinante"] != "PM10":
            continue
        
        valore = record.get("valore")
        if valore is None:
            continue
        
        try:
            valore = float(valore)
        except (ValueError, TypeError):
            continue
        
        data_str = record.get("data", "")[:10]
        if not data_str:
            continue
        
        chiave = info["nomestazione"]
        if chiave not in superamenti_per_stazione:
            superamenti_per_stazione[chiave] = {
                "comune": info["comune"],
                "valori_giornalieri": {}
            }
        
        if data_str not in superamenti_per_stazione[chiave]["valori_giornalieri"]:
            superamenti_per_stazione[chiave]["valori_giornalieri"][data_str] = []
        superamenti_per_stazione[chiave]["valori_giornalieri"][data_str].append(valore)
    
    risultati = []
    for stazione, dati in superamenti_per_stazione.items():
        giorni_sup = 0
        for data, valori in dati["valori_giornalieri"].items():
            media = sum(valori) / len(valori)
            if media > 50:
                giorni_sup += 1
        
        risultati.append({
            "stazione": stazione,
            "comune": dati["comune"],
            "giorni_superamento": giorni_sup
        })
    
    risultati.sort(key=lambda x: x["giorni_superamento"], reverse=True)
    return risultati


def prepara_dati_grafici(dati, stazioni):
    """Prepara i dati nel formato richiesto per i grafici."""
    sensore_map = {s["idsensore"]: s for s in stazioni}
    
    dati_grafici = {
        "ultimo_aggiornamento": datetime.now().isoformat(),
        "stazioni": [],
        "comuni": [],
        "serie_temporali": {},
        "confronto_stazioni": {},
        "soglie": SOGLIE
    }
    
    comuni_set = set()
    stazioni_set = set()
    for s in stazioni:
        comuni_set.add(s["comune"])
        stazioni_set.add(s["nomestazione"])
    
    dati_grafici["comuni"] = sorted(list(comuni_set))
    dati_grafici["stazioni"] = sorted(list(stazioni_set))
    
    dati_per_comune = {}
    dati_per_stazione = {}
    
    for record in dati:
        idsensore = record.get("idsensore")
        if idsensore not in sensore_map:
            continue
        
        info = sensore_map[idsensore]
        comune = info["comune"]
        stazione = info["nomestazione"]
        inquinante = info["inquinante"]
        
        valore = record.get("valore")
        if valore is None:
            continue
        
        try:
            valore = float(valore)
        except (ValueError, TypeError):
            continue
        
        data = record.get("data", "")[:10]
        if not data:
            continue
        
        if comune not in dati_per_comune:
            dati_per_comune[comune] = {}
        if inquinante not in dati_per_comune[comune]:
            dati_per_comune[comune][inquinante] = {}
        if data not in dati_per_comune[comune][inquinante]:
            dati_per_comune[comune][inquinante][data] = []
        dati_per_comune[comune][inquinante][data].append(valore)
        
        chiave_stazione = f"{stazione}|{comune}"
        if chiave_stazione not in dati_per_stazione:
            dati_per_stazione[chiave_stazione] = {}
        if inquinante not in dati_per_stazione[chiave_stazione]:
            dati_per_stazione[chiave_stazione][inquinante] = []
        dati_per_stazione[chiave_stazione][inquinante].append(valore)
    
    for comune, inquinanti in dati_per_comune.items():
        dati_grafici["serie_temporali"][comune] = {}
        for inquinante, date_valori in inquinanti.items():
            serie = []
            for data, valori in sorted(date_valori.items()):
                media = sum(valori) / len(valori)
                serie.append({
                    "data": data,
                    "valore": round(media, 1)
                })
            dati_grafici["serie_temporali"][comune][inquinante] = serie
    
    for inquinante in ["PM10", "PM2.5", "NO2"]:
        dati_grafici["confronto_stazioni"][inquinante] = []
        for chiave_stazione, inq_valori in dati_per_stazione.items():
            if inquinante in inq_valori:
                stazione, comune = chiave_stazione.split("|")
                valori = inq_valori[inquinante]
                media = sum(valori) / len(valori)
                dati_grafici["confronto_stazioni"][inquinante].append({
                    "stazione": stazione,
                    "comune": comune,
                    "valore": round(media, 1)
                })
        dati_grafici["confronto_stazioni"][inquinante].sort(
            key=lambda x: x["valore"], reverse=True
        )
    
    return dati_grafici


def salva_dati(stazioni, dati_grafici, superamenti):
    """Salva tutti i dati nei file."""
    with open(DATA_DIR / "stazioni.json", "w", encoding="utf-8") as f:
        json.dump(stazioni, f, ensure_ascii=False, indent=2)
    print(f"Salvato: {DATA_DIR / 'stazioni.json'}")
    
    dati_grafici["superamenti"] = superamenti
    
    with open(DATA_DIR / "dati_grafici.json", "w", encoding="utf-8") as f:
        json.dump(dati_grafici, f, ensure_ascii=False, indent=2)
    print(f"Salvato: {DATA_DIR / 'dati_grafici.json'}")
    
    docs_data_dir = DOCS_DIR / "data"
    docs_data_dir.mkdir(exist_ok=True)
    
    with open(docs_data_dir / "dati_grafici.json", "w", encoding="utf-8") as f:
        json.dump(dati_grafici, f, ensure_ascii=False, indent=2)
    print(f"Salvato: {docs_data_dir / 'dati_grafici.json'}")


def main():
    """Funzione principale."""
    print("=" * 60)
    print("AGGIORNAMENTO DATI QUALITÀ ARIA - PROVINCIA DI VARESE")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    stazioni = fetch_stazioni()
    if not stazioni:
        print("ERRORE: Nessuna stazione trovata!")
        return 1
    
    dati_30gg, dati_anno = fetch_tutti_dati(stazioni, giorni=30)
    dati_grafici = prepara_dati_grafici(dati_30gg, stazioni)
    superamenti = calcola_superamenti(dati_anno, stazioni)
    salva_dati(stazioni, dati_grafici, superamenti)
    
    print("=" * 60)
    print("AGGIORNAMENTO COMPLETATO")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
