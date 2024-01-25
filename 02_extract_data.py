#!/usr/bin/env python
# coding: utf-8

# In[83]:

import os
import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
# Bibliothek für Webscraping
# import requests

# Echten Web HTML Dokument bekommen
## response = requests.get(file_path)

def wh_scraping(file_path_):
    # BeautifulSoup verwenden, um die HTML-Daten zu extrahieren
    with open(file_path_, 'r', encoding='utf-8') as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')

    # schreibe ein passenderes Kommentar
    tr = soup.find_all('tr')

    # GET
    # list[ Anzahl, Personen, Wohnfläche, Mietpreis, Verfügbarkeit]
    # Konvertiere die gefundenen <td>-Elemente in eine Liste
    tr_list = [tr.text for tr in tr]

    # Extrahiere die Zeilen zu den einzelnen Zimmertypen
    tr_extract = [i for i in tr_list if "Wartezeit" in i]

    # Zerteile die Zeilen
    tr_split_extract = [i.split('\n') for i in tr_extract]

    # Entferne leere Elemente aus den Unterlisten
    tr_split_extract_cleaned = [[item for item in sublist if item.strip()] for sublist in tr_split_extract]

    # Entferne leere Listen aus der Hauptliste
    tr_split_extract_cleaned = [sublist for sublist in tr_split_extract_cleaned if sublist]

    # Spaltennamen definieren
    columns = ['Anzahl', 'Personen', 'Wohnfläche', 'Mietpreis', 'Verfügbarkeit']

    # Erstelle eine Liste von Dictionaries
    data_list = [dict(zip(columns, sublist)) for sublist in tr_split_extract_cleaned]

    # Erstelle den DataFrame
    df = pd.DataFrame(data_list)

    # Spaltennamen definieren
    bool_columns = ['Internet', 'Dusche', 'Küche', 'möbliert', 'behindertengerecht']

    # Liste für die Zeilen des DataFrames erstellen
    data = []

    div_appartments = soup.find_all('div', class_='apartment')
    for div_appartment in div_appartments:
        # Möbliert, Dusche, Küche, Behindertengerecht extrahieren
        moebliert = div_appartment.find('img', title=re.compile('.*möbliert.*')) is not None
        dusche = div_appartment.find('img', title=re.compile('.*Dusche.*')) is not None
        kueche = div_appartment.find('img', title=re.compile('.*Küche.*')) is not None
        behindertengerecht = div_appartment.find('img', title=re.compile('.*behindertengerecht.*')) is not None

        # Internet-Informationen extrahieren (hier musst du die entsprechende Bedingung anpassen)
        # Internet 100 Mbit/s
        # internet = div_appartment.find('img', title='Internet 100 Mbit/s') is not None
        internet = div_appartment.find('img', title=re.compile('.*nternet.*')) is not None

        # Informationen in eine Liste speichern
        info_list = [internet, dusche, kueche, moebliert, behindertengerecht]

        # Liste zur Data-Liste hinzufügen
        data.append(info_list)

    # DataFrame erstellen
    df_bool = pd.DataFrame(data, columns=bool_columns)

    # Zusammenführen der DataFrames
    merged_df = pd.concat([df, df_bool], axis=1)

    # Erstelle eine neue Spalte "ID" mit Werten von 1 bis zur Anzahl der Zeilen
    merged_df['id_typ'] = range(1, len(df) + 1)

    # "fremdschlüssel" hinzufügen (Name des Wohnheims)
    h1 = soup.find_all('h1')
    # Extrahiere den Wohnheimname des ersten Elements in der Liste h1
    wh_name = h1[0].text.strip().replace('WH ', '')
    
    # Hinzufügen der 'wh_name'-Spalte
    merged_df.insert(0, 'wh_name', wh_name)

    return merged_df


# In[84]:


# Pfad zum Verzeichnis mit den HTML-Dateien
verzeichnis_pfad = "C:/Users/lucae/Nextcloud/wohnheim_map/wh_webscraping/html_wohnheim"
# verzeichnis_pfad = "D:/Programme/NextCloud/wohnheim_map/wh_webscraping/html_wohnheim"

# Liste, um die Datenframes zu speichern
df_liste = []

# Durchlaufe alle Dateien im Verzeichnis
for datei_name in os.listdir(verzeichnis_pfad):
    if datei_name.endswith(".html"):
        # Hier füge deine Funktion zum Verarbeiten der HTML-Datei hinzu und erhalte ein DataFrame zurück
        df = wh_scraping(os.path.join(verzeichnis_pfad, datei_name))
        df_liste.append(df)

# Merge alle DataFrames in der Liste
ergebnis_df = pd.concat(df_liste, ignore_index=True)
# Jetzt hast du ein DataFrame, das aus der Fusion aller Einzel-DataFrames besteht
# ergebnis_df

# Manuelle Sortierung nach 'wh_name'
df_sorted = ergebnis_df.sort_values(by='wh_name')

# Füge eine neue Spalte 'id_wh' hinzu, die die Ränge mit führenden Nullen enthält
df_sorted['id_wh'] = "wh" + df_sorted['wh_name'].rank(method='dense').astype(int).astype(str).str.zfill(2)

column_order = ['id_wh'] + ['id_typ'] + [col for col in df_sorted.columns if col != 'id_wh' and col != 'id_typ']

df_final = df_sorted[['id_wh', 'id_typ', 'wh_name', 'Anzahl', 'Personen', 'Wohnfläche', 'Mietpreis', 'Verfügbarkeit', 'Internet', 'Dusche', 'Küche', 'möbliert', 'behindertengerecht']]


# Aktualisierung der Variable Verfügbarkeit
df_final['Verfügbarkeit'] = df_final['Verfügbarkeit'].str.replace('Wartezeit ', '')

# Aktualisiere/Trenne den Mietpreis
# Regulärer Ausdruck, um Mindest- und Maximalwerte zu extrahieren
pattern = r'(\d+)\xa0–\xa0(\d+)\xa0€'
# Extrahiere die Werte in einen DataFrame mit zwei Spalten
extracted_values = df_final['Mietpreis'].str.extract(pattern)
# Konvertiere die extrahierten Werte in Integer (optional)
extracted_values = extracted_values.apply(pd.to_numeric)
# Füge die extrahierten Werte in das DataFrame df_final ein
df_final[['Mietpreis_min', 'Mietpreis_max']] = extracted_values

# Aktualisiere/Trenne den Wohnfläche
# Reguläre Ausdrücke, um Mindest- und Maximalwerte zu extrahieren
pattern_2 = r'(\d+)\xa0–\xa0(\d+)\xa0qm|(\d+)\xa0qm'
# Extrahiere die Werte in einen DataFrame mit zwei Spalten
extracted_values = df_final['Wohnfläche'].str.extract(pattern_2)
# Konvertiere die extrahierten Werte in Integer (optional)
extracted_values = extracted_values.apply(pd.to_numeric)
# Füge die extrahierten Werte in das DataFrame df_final ein
df_final[['Wohnfläche_min', 'Wohnfläche_max', 'Wohnfläche_']] = extracted_values
# Fülle NaN-Werte in 'Mietpreis_min' mit Werten aus 'Mietpreis_'
df_final['Wohnfläche_min'] = df_final['Wohnfläche_min'].fillna(df_final['Wohnfläche_'])
# Fülle NaN-Werte in 'Mietpreis_max' mit Werten aus 'Mietpreis_'
df_final['Wohnfläche_max'] = df_final['Wohnfläche_max'].fillna(df_final['Wohnfläche_'])

# Aktualisiere/Trenne den Personen
# Reguläre Ausdrücke, um Mindest- und Maximalwerte zu extrahieren
pattern_3 = r'(\d+)-(\d+)|(\d+)'
# Extrahiere die Werte in einen DataFrame mit zwei Spalten
extracted_values = df_final['Personen'].str.extract(pattern_3)
# Konvertiere die extrahierten Werte in Integer (optional)
extracted_values = extracted_values.apply(pd.to_numeric)
# Füge die extrahierten Werte in das DataFrame df_final ein
df_final[['Personen_min', 'Personen_max', 'Personen_']] = extracted_values
# Fülle NaN-Werte in 'Mietpreis_min' mit Werten aus 'Mietpreis_'
df_final['Personen_min'] = df_final['Personen_min'].fillna(df_final['Personen_'])
# Fülle NaN-Werte in 'Mietpreis_max' mit Werten aus 'Mietpreis_'
df_final['Personen_max'] = df_final['Personen_max'].fillna(df_final['Personen_'])

df_final = df_final[['id_wh', 'id_typ', 'wh_name', 'Anzahl', 
                      'Personen_min', 'Personen_max', 
                      'Wohnfläche_min', 'Wohnfläche_max', 
                      'Mietpreis_min', 'Mietpreis_max', 
                      'Verfügbarkeit', 'Internet', 'Dusche', 'Küche', 'möbliert', 'behindertengerecht']]


# In[85]:


# Pfad, unter dem die Excel-Datei gespeichert werden soll
excel_datei_pfad = "C:/Users/lucae/Nextcloud/wohnheim_map/wh_webscraping/excel_table/zimmertypen.xlsx"
# excel_datei_pfad = "D:/Programme/NextCloud/wohnheim_map/wh_webscraping/excel_table/zimmertypen.xlsx"

# Exportiere das DataFrame als Excel-Datei
df_final.to_excel(excel_datei_pfad, index=False)


csv_datei_pfad = "C:/Users/lucae/Nextcloud/wohnheim_map/wh_webscraping/excel_table/zimmertypen.csv"
df_final.to_csv(csv_datei_pfad, index=False)

# In[86]:


# Stichproben überprüfen
## Spalte 'Name' eindeutige Werte als Liste erhalten

# unique_names = ergebnis_df['wh_name'].unique().tolist()
# random_name = unique_names[random.randint(0, 30)]
# ergebnis_df.loc[ergebnis_df['wh_name'] == random_name]

