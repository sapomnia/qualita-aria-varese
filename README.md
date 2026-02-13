# 📊 Qualità dell'Aria - Provincia di Varese

Dashboard automatizzata per il monitoraggio della qualità dell'aria nella provincia di Varese, con dati aggiornati quotidianamente dalle centraline ARPA Lombardia.

## 🌐 Visualizza la Dashboard

**[👉 Apri la dashboard](https://sapomnia.github.io/qualita-aria-varese/)**

## 📈 Cosa mostra

- **Qualità dell'aria giornaliera**: Grafico a barre verticali con valori medi per stazione
- **Serie temporali (30 giorni)**: Andamento di PM10, PM2.5 e NO₂ con filtro per comune
- **Superamenti soglia**: Giorni con PM10 > 50 µg/m³ dall'inizio dell'anno

## ⏰ Aggiornamento automatico

Lo script viene eseguito automaticamente ogni giorno alle **6:00** (ora italiana).

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
  src="https://sapomnia.github.io/qualita-aria-varese/" 
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
