# 📊 Qualità dell'Aria - Provincia di Varese

Dashboard automatizzata per il monitoraggio della qualità dell'aria nella provincia di Varese, con dati aggiornati quotidianamente dalle centraline ARPA Lombardia.

## 🌐 Visualizza la Dashboard

**[👉 Apri la dashboard](https://TUOUSER.github.io/qualita-aria-varese/)**

*(Sostituisci `TUOUSER` con il tuo username GitHub)*

## 📈 Cosa mostra

- **Serie temporali (30 giorni)**: Andamento di PM10, PM2.5 e NO₂ con filtro per comune
- **Confronto centraline**: Grafico a barre verticali con valori medi per stazione
- **Superamenti soglia**: Giorni con PM10 > 50 µg/m³ dall'inizio dell'anno

### Scala colori

| Inquinante | 🟢 Buono | 🟡 Moderato | 🔴 Alto |
|------------|----------|-------------|---------|
| PM10 | < 35 µg/m³ | 35-50 µg/m³ | > 50 µg/m³ |
| PM2.5 | < 20 µg/m³ | 20-25 µg/m³ | > 25 µg/m³ |
| NO₂ | < 100 µg/m³ | 100-200 µg/m³ | > 200 µg/m³ |

## 🚀 Setup

### 1. Crea il repository

1. Vai su [github.com/new](https://github.com/new)
2. Nome: `qualita-aria-varese`
3. Seleziona "Public"
4. Clicca "Create repository"

### 2. Carica i file

```bash
# Clona il repository
git clone https://github.com/TUOUSER/qualita-aria-varese.git
cd qualita-aria-varese

# Copia tutti i file del progetto nella cartella
# (scripts/, docs/, .github/, data/, README.md, ecc.)

# Commit e push
git add .
git commit -m "🚀 Setup iniziale"
git push
```

### 3. Attiva GitHub Pages

1. Vai su Settings → Pages
2. Source: **Deploy from a branch**
3. Branch: **main** / **docs**
4. Clicca Save

### 4. Esegui il primo aggiornamento

1. Vai su Actions → "Aggiorna dati qualità aria"
2. Clicca "Run workflow" → "Run workflow"
3. Attendi ~2 minuti per il completamento

La dashboard sarà disponibile su: `https://TUOUSER.github.io/qualita-aria-varese/`

## ⏰ Aggiornamento automatico

Lo script viene eseguito automaticamente ogni giorno alle **6:00** (ora italiana).

Per modificare l'orario, modifica il file `.github/workflows/update-data.yml`:

```yaml
schedule:
  - cron: '0 5 * * *'   # 6:00 CET (inverno)
  - cron: '0 4 * * *'   # 6:00 CEST (estate)
```

## 📁 Struttura progetto

```
qualita-aria-varese/
├── .github/workflows/
│   └── update-data.yml     # GitHub Action per aggiornamento
├── scripts/
│   └── fetch_data.py       # Script Python per download dati
├── data/
│   ├── stazioni.json       # Anagrafica stazioni
│   └── dati_grafici.json   # Dati per i grafici
├── docs/
│   ├── index.html          # Dashboard
│   └── data/
│       └── dati_grafici.json
└── README.md
```

## 🔗 Embed nel tuo sito

Per incorporare la dashboard nel tuo sito:

```html
<iframe 
  src="https://TUOUSER.github.io/qualita-aria-varese/" 
  width="100%" 
  height="800" 
  frameborder="0">
</iframe>
```

## 📊 Fonte dati

- **ARPA Lombardia** via [Open Data Regione Lombardia](https://www.dati.lombardia.it)
- Dataset stazioni: `ib47-atvt`
- Dataset misurazioni: `nicp-bhqi`

## 📝 Licenza

Dati pubblici rilasciati da Regione Lombardia.
Codice rilasciato con licenza MIT.
