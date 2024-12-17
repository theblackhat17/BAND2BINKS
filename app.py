from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import zipfile
import threading
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join("static", "downloads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Fonction pour générer automatiquement le JSON ===
def generate_json(folder_url, download_path):
    driver = webdriver.Chrome()
    driver.get(folder_url)
    try:
        # Récupérer le nom du dossier
        folder_name = driver.find_element(By.XPATH, '//*[@id="name-section"]/h2').text.strip().replace(" ", "_")
        output_folder = os.path.join(download_path, folder_name)
        os.makedirs(output_folder, exist_ok=True)

        # Récupérer les titres des musiques
        titles_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.track-title'))
        )
        titles = [{"title": title.text.strip()} for title in titles_elements if title.text.strip()]
        json_path = os.path.join(output_folder, f"{folder_name}.json")
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(titles, json_file, ensure_ascii=False, indent=4)

        # Lancer le téléchargement des musiques
        download_music(folder_url, folder_name, output_folder, json_path)

    except Exception as e:
        print(f"Erreur lors de la génération du JSON : {e}")
    finally:
        driver.quit()

# === Fonction pour télécharger les musiques et l'image de couverture ===
def download_music(folder_url, folder_name, download_path, json_path):
    driver = webdriver.Chrome()
    driver.get(folder_url)
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            file_names = json.load(file)

        play_buttons = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.play_status'))
        )

        # Télécharger et sauvegarder l'image de couverture
        cover_element = driver.find_element(By.XPATH, '//*[@id="tralbumArt"]/a/img')
        cover_url = cover_element.get_attribute('src')
        cover_path = os.path.join(download_path, "cover.jpg")
        with open(cover_path, 'wb') as img_file:
            img_file.write(requests.get(cover_url).content)

        # Télécharger chaque musique
        for index, button in enumerate(play_buttons, start=1):
            driver.execute_script("arguments[0].click();", button)
            time.sleep(2)
            audio_element = driver.find_element(By.CSS_SELECTOR, 'audio')
            audio_url = audio_element.get_attribute('src')
            filename = file_names[index-1]['title'] + ".mp3"
            file_path = os.path.join(download_path, filename)

            audio_response = requests.get(audio_url)
            with open(file_path, 'wb') as file:
                file.write(audio_response.content)

            add_cover_to_mp3(file_path, requests.get(cover_url).content)

        # Supprimer le fichier JSON après téléchargement
        os.remove(json_path)

    except Exception as e:
        print(f"Erreur téléchargement : {e}")
    finally:
        driver.quit()

# === Fonction pour ajouter la cover dans les fichiers MP3 ===
def add_cover_to_mp3(file_path, cover_data):
    audio = MP3(file_path, ID3=ID3)
    if audio.tags is None:
        audio.add_tags()
    audio.tags.add(
        APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=cover_data)
    )
    audio.save()

# === Fonction pour lister les dossiers et fichiers sans root ===
def list_folders_and_files():
    folder_structure = {}
    for foldername, _, filenames in os.walk(UPLOAD_FOLDER):
        rel_path = os.path.relpath(foldername, UPLOAD_FOLDER)
        if rel_path == "." or rel_path == "root":
            continue  # Ignorer le dossier root
        folder_structure[rel_path] = filenames
    return folder_structure

# === Route principale ===
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        folder_url = request.form["url"]
        threading.Thread(target=generate_json, args=(folder_url, UPLOAD_FOLDER), daemon=True).start()
        return redirect(url_for("index"))

    folders = list_folders_and_files()
    return render_template("index.html", folders=folders)

# === Route pour télécharger un fichier spécifique ===
@app.route("/downloads/<path:filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# === Route pour télécharger un dossier entier au format ZIP ===
@app.route("/download_zip/<path:folder>")
def download_zip(folder):
    folder_path = os.path.join(UPLOAD_FOLDER, folder)
    zip_path = os.path.join(UPLOAD_FOLDER, f"{folder}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    return send_from_directory(UPLOAD_FOLDER, f"{folder}.zip", as_attachment=True)

# === Lancer l'application Flask ===
if __name__ == "__main__":
    app.run(debug=True)
