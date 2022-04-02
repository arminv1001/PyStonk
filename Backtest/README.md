
## General Things
* verfügbare Strategie: Moving Average Strategie
* Sidebar für Backtest Settings ausfüllen
* Bei Periodicity: Daily auswählen
* bis jetzt nur für Daily Timeframe ausgelegt
* bei Source Folder Daten auf verfügbares Startdatum bzw. Enddatum achten
* Size = 0 heißt komplettes Kapital wird investiert

### First Things First
* CSV_DIR in CSVDataPreparer.py ändern
* eigenen Pfad eingeben

``` sh
CSV_DIR = '/Users/mr.kjn/Projects/PyStonk/Backtest/backtest_data'
```
* PATH in toolbox.py ändern
* eigenen Pfad eingeben
``` sh
PATH = '/Users/mr.kjn/Projects/PyStonk/Backtest/'
```

### Run Forest run!
1. env starten
2. streamlit starten
``` sh
streamlit run /Users/mr.kjn/Projects/PyStonk/Backtest/main.py 
```
3. GUI öffnet sich im Webbrowser
