
import tkinter as tk  # Für die GUI
from tkinter import ttk  # Für schönere Tabellen
import mariadb  # Für die Datenbankverbindung
import sys  # Für Systemfunktionen
from datetime import datetime  # Für Datumsüberprüfung

# Klasse für Bestellungen - speichert alle Infos zu einer Bestellung
class Bestellung:
    def __init__(self, anrede, vorname, nachname, bestelldatum, artikelname):
        self.anrede = anrede  
        self.vorname = vorname  
        self.nachname = nachname  
        self.bestelldatum = bestelldatum  
        self.artikelname = artikelname  

# Verbindung zur Datenbank herstellen
try:
    conn = mariadb.connect(
        user="horstMueller",  
        password="Pommes1",  # Passwort (lecker Pommes!)
        host="localhost",  
        port=3306,  
        database="schlumpfshop3"  # Name der Datenbank
    )
except mariadb.Error as e:
    print("Fehler bei der Verbindung zur Datenbank:", e)  # Fehlermeldung wenn was schiefgeht
    sys.exit()  # Programm beenden

cur = conn.cursor()  # Cursor erstellen (zum Ausführen von SQL-Befehlen)

# Abfragefunktion
def bestellungen_abfragen():
    datum = eingabe_feld.get()  # Holt das eingegebene Datum
    
    try:
        # Überprüfen, ob das Datum gültig ist
        datetime.strptime(datum, '%Y-%m-%d')
        
        # Alte Tabelle löschen
        for eintrag in tabelle.get_children():
            tabelle.delete(eintrag)
            
        # MySQL-Abfrage
        cur.execute(f"""
         SELECT anrede.Anrede, kunden.Vorname, kunden.name, 
           bestellungen.Bestelldatum, artikel.Artikelname
    FROM ((bestellungen
    INNER JOIN kunden ON bestellungen.ID_Kunde = kunden.IDKunde)
    INNER JOIN artikel ON bestellungen.ID_Bestellung = artikel.Artikelnummer)
    INNER JOIN anrede on kunden.Anrede = anrede.ID_Anrede
    WHERE bestellungen.Bestelldatum >= '{datum}'
    ORDER BY bestellungen.Bestelldatum DESC
        """)

        bestellungen = []
        
        for (anrede, vorname, nachname, bestelldatum, artikelname) in cur:
            bestellung = Bestellung(anrede, vorname, nachname, bestelldatum, artikelname)
            bestellungen.append(bestellung)

        # Bestellungen in die Tabelle einfügen
        for bestellung in bestellungen:
            tabelle.insert("", tk.END, values=(
                bestellung.anrede,
                bestellung.vorname,
                bestellung.nachname,
                bestellung.bestelldatum,
                bestellung.artikelname
            ))

    except ValueError:
        print("Bitte ein gültiges Datum im Format YYYY-MM-DD eingeben.")
    except mariadb.Error as e:
        print("Datenbankfehler:", e)




# Fenster erstellen
fenster = tk.Tk()
fenster.title("Kundenbestellungen ab Datum")

# Eingabefeld für Datum
label = tk.Label(fenster, text="Datum (YYYY-MM-DD):")
label.pack(pady=5)

eingabe_feld = tk.Entry(fenster)
eingabe_feld.pack(pady=5)

# Button erstellen
button = tk.Button(fenster, text="Bestellungen anzeigen", command=bestellungen_abfragen)
button.pack(pady=5)

# Tabelle erstellen
tabelle = ttk.Treeview(fenster, columns=("Anrede", "Vorname", "Name", "Bestelldatum", "Artikel"), show="headings")
tabelle.heading("Anrede", text="Anrede")
tabelle.heading("Vorname", text="Vorname")
tabelle.heading("Name", text="Name")
tabelle.heading("Bestelldatum", text="Bestelldatum")
tabelle.heading("Artikel", text="Artikel")

for spalte in tabelle["columns"]:
    tabelle.column(spalte, anchor="center")

tabelle.pack(fill=tk.BOTH, expand=True, pady=10)

# Fenster starten
fenster.mainloop()

# Verbindung schließen
cur.close()
conn.close()