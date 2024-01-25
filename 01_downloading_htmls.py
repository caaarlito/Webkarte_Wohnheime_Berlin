#!/usr/bin/env python
# coding: utf-8

# In[71]:


import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import random

file_path = "https://www.stw.berlin/wohnen/wohnheime/"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

response = requests.get(file_path, headers=headers)


# In[72]:


# Überprüfe, ob die Anfrage erfolgreich war (Status-Code 200)
if response.status_code == 200:
    # Der HTML-Code der Webseite ist in response.text enthalten
    html_code = response.text
    
    # Verwende BeautifulSoup, um den HTML-Code zu analysieren
    soup = BeautifulSoup(html_code, 'html.parser')
    
    # Beispiel: Extrahiere alle div-Elemente mit der Klasse "list-children-teaser"
    divs = soup.find_all('div', class_='list-children-teaser')
    
    # Erstelle eine Liste für alle Links
    all_links = []
    
    # Erstelle eine Liste für alle h2-Elemente
    all_h2_elements = []
    
    # Iteriere über jedes div-Element und finde alle Links und h2-Elemente
    for div in divs:
        # Finde alle Links innerhalb des div-Elements
        links = div.find_all('a')
        
        # Extrahiere den Link aus jedem gefundenen a-Tag und füge ihn zur Gesamtliste hinzu
        for link in links:
            # Füge den modifizierten Link zur Liste hinzu
            all_links.append("https://www.stw.berlin/" + link.get('href'))
        
        # Finde alle h2-Elemente innerhalb des div-Elements
        h2_elements = div.find_all('h2')
        
        # Füge die gefundenen h2-Elemente zur Gesamtliste hinzu
        all_h2_elements.extend(h2_elements)
    
    # Überprüfe ob beide Listen gleich viele Elemente haben
    if len(all_h2_elements) == len(all_links):
        
        # Entferne "WH " aus jedem Element in der all_h2_elements-Liste
        all_h2_elements = [element.text.replace("WH ", "") for element in all_h2_elements]
        
        # Ersetze Leerzeichen durch Unterstriche in jedem Element der all_h2_elements-Liste
        all_h2_elements = [element.replace(" ", "_") for element in all_h2_elements]
        
        # Ersetze Kommas durch Unterstriche in jedem Element der all_h2_elements-Liste
        all_h2_elements = [element.replace(",", "") for element in all_h2_elements]
        
        # Entferne Informationen in Klammern aus jedem Element der all_h2_elements-Liste
        all_h2_elements = [re.sub(r'\([^)]*\)', '', element) for element in all_h2_elements]
        
        # Drucke die aktualisierte Liste der h2-Elemente
        print("Die Listen 'all_h2_elements' und 'all_links' haben gleich viele Elemente")
        
    else:
        print("Fehler: Liste ist nicht gleich groß")
else:
    print(f"Fehler beim Abrufen der Webseite. Statuscode: {response.status_code}")


# In[ ]:


# Set the base directory where the files will be saved
base_directory = r"C:\Users\lucae\Nextcloud\wohnheim_map\wh_webscraping\html_wohnheim"

for link, h2_element in zip(all_links, all_h2_elements):
    try:
        # Download the page
        response = requests.get(link, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        # Determine the file path and name for the HTML file
        filename = os.path.join(base_directory, f"{h2_element}.html")

        # Write the HTML code to a file
        with open(filename, "w", encoding="utf-8") as html_file:
            html_file.write(response.text)

        print(f"HTML code for {h2_element} successfully saved at: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the page for {h2_element}: {e}")

    # Add a pause between requests
    random_time = round(random.uniform(1.0, 5.0), 2)
    time.sleep(random_time)  # Add an appropriate delay to avoid overloading the server


# In[ ]:




