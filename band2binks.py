import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import requests
import os
import threading
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import queue

# File download queue
result_queue = queue.Queue()

def generate_json(folder_url, output_file):
    driver = webdriver.Chrome()
    driver.get(folder_url)

    try:
        # Sélecteur des titres des musiques
        titles_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.track-title'))
        )
        # Récupérer les titres
        titles = [{"title": title.text.strip()} for title in titles_elements if title.text.strip()]
        # Sauvegarder dans un fichier JSON
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(titles, json_file, ensure_ascii=False, indent=4)
        result_queue.put(("success", f"Fichier JSON généré : {output_file}"))
    except Exception as e:
        result_queue.put(("error", f"Erreur lors de la génération du JSON : {e}"))
    finally:
        driver.quit()


def download_music(folder_url, folder_name, download_path):
    driver = webdriver.Chrome()
    driver.get(folder_url)

    try:
        # Charger les titres depuis le JSON généré précédemment
        json_path = os.path.join(download_path, f"{folder_name}.json")
        with open(json_path, 'r', encoding='utf-8') as file:
            file_names = json.load(file)

        play_buttons = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.play_status'))
        )

        if len(file_names) != len(play_buttons):
            result_queue.put(("error", "Nombre de titres dans le JSON ne correspond pas aux musiques."))
            return

        # Récupérer l'image de couverture
        cover_element = driver.find_element(By.XPATH, '//*[@id="tralbumArt"]/a/img')
        cover_url = cover_element.get_attribute('src')
        cover_data = requests.get(cover_url).content

        # Télécharger chaque musique
        for index, button in enumerate(play_buttons, start=1):
            driver.execute_script("arguments[0].click();", button)
            time.sleep(2)

            audio_element = driver.find_element(By.CSS_SELECTOR, 'audio')
            audio_url = audio_element.get_attribute('src')
            filename = file_names[index-1]['title'] + ".mp3"
            file_path = os.path.join(download_path, filename)

            # Télécharger l'audio
            audio_response = requests.get(audio_url)
            with open(file_path, 'wb') as file:
                file.write(audio_response.content)

            # Ajouter la cover
            add_cover_to_mp3(file_path, cover_data)

        result_queue.put(("success", "Tous les fichiers ont été téléchargés avec succès."))
    except Exception as e:
        result_queue.put(("error", f"Erreur lors du téléchargement : {e}"))
    finally:
        driver.quit()


def add_cover_to_mp3(file_path, cover_data):
    try:
        audio = MP3(file_path, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()
        audio.tags.add(
            APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=cover_data)
        )
        audio.save()
    except Exception as e:
        print(f"Erreur lors de l'ajout de la cover : {e}")


def process_result():
    """
    Traite les résultats des threads et affiche les messages appropriés.
    """
    try:
        while not result_queue.empty():
            status, message = result_queue.get_nowait()
            if status == "success":
                messagebox.showinfo("Succès", message)
            elif status == "error":
                messagebox.showerror("Erreur", message)
    except queue.Empty:
        pass
    finally:
        # Répéter pour vérifier les nouveaux résultats
        root.after(100, process_result)


def start_process(action):
    folder_url = url_entry.get()
    folder_name = folder_entry.get()
    download_path = os.path.join(os.path.expanduser('~'), 'Downloads', folder_name)

    if not os.path.isdir(download_path):
        os.makedirs(download_path)

    if action == "generate":
        json_path = os.path.join(download_path, f"{folder_name}.json")
        threading.Thread(target=generate_json, args=(folder_url, json_path), daemon=True).start()
    elif action == "download":
        threading.Thread(target=download_music, args=(folder_url, folder_name, download_path), daemon=True).start()


# Interface utilisateur Tkinter
root = tk.Tk()
root.title("BAND2BINKS")
root.geometry("600x400")

url_label = tk.Label(root, text="URL de la page :")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.insert(0, "https://bandcamp.com/nom_de_lartiste")
url_entry.pack(pady=5)

folder_label = tk.Label(root, text="Nom du dossier :")
folder_label.pack(pady=5)
folder_entry = tk.Entry(root, width=50)
folder_entry.insert(0, "PACK_2024")
folder_entry.pack(pady=5)

generate_button = tk.Button(root, text="Générer JSON", command=lambda: start_process("generate"))
generate_button.pack(pady=10)

download_button = tk.Button(root, text="Télécharger musiques", command=lambda: start_process("download"))
download_button.pack(pady=10)

# Lancer le traitement des résultats en arrière-plan
root.after(100, process_result)
root.mainloop()
