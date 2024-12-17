from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import json
import threading
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Dossier pour les téléchargements
UPLOAD_FOLDER = os.path.join("static", "downloads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Mode headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Initialise ChromeDriver sans spécifier de chemin explicite
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Fonction pour générer le JSON
def generate_json(folder_url, json_path):
    driver = create_chrome_driver()  # Utilise la fonction pour le driver
    driver.get(folder_url)
    try:
        titles_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.track-title'))
        )
        titles = [{"title": title.text.strip()} for title in titles_elements if title.text.strip()]
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(titles, json_file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erreur lors de la génération du JSON : {e}")
    finally:
        driver.quit()

# Fonction pour télécharger la musique
def download_music(folder_url, folder_name):
    driver = create_chrome_driver()  # Utilise correctement la fonction
    driver.get(folder_url)
    try:
        json_path = os.path.join(UPLOAD_FOLDER, f"{folder_name}.json")
        with open(json_path, "r", encoding="utf-8") as file:
            file_names = json.load(file)

        play_buttons = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.play_status'))
        )

        cover_element = driver.find_element(By.XPATH, '//*[@id="tralbumArt"]/a/img')
        cover_url = cover_element.get_attribute('src')
        cover_data = requests.get(cover_url).content

        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Sauvegarder l'image de couverture
        with open(os.path.join(folder_path, "cover.jpg"), "wb") as cover_file:
            cover_file.write(cover_data)

        for index, button in enumerate(play_buttons, start=1):
            driver.execute_script("arguments[0].click();", button)
            audio_element = driver.find_element(By.CSS_SELECTOR, 'audio')
            audio_url = audio_element.get_attribute('src')

            filename = file_names[index-1]['title'] + ".mp3"
            file_path = os.path.join(folder_path, filename)

            audio_response = requests.get(audio_url)
            with open(file_path, "wb") as file:
                file.write(audio_response.content)
            
            add_cover_to_mp3(file_path, cover_data)

    except Exception as e:
        print(f"Erreur téléchargement : {e}")
    finally:
        driver.quit()

def add_cover_to_mp3(file_path, cover_data):
    try:
        audio = MP3(file_path, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()
        audio.tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover_data))
        audio.save()
    except Exception as e:
        print(f"Erreur ajout de cover : {e}")

# Route principale
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        folder_name = url.split("/")[-1].replace(" ", "_")
        json_path = os.path.join(UPLOAD_FOLDER, f"{folder_name}.json")

        threading.Thread(target=generate_json, args=(url, json_path)).start()
        threading.Thread(target=download_music, args=(url, folder_name)).start()

        return redirect(url_for("index"))
    
    # Lister les dossiers et fichiers
    folders = {}
    if os.path.exists(UPLOAD_FOLDER):
        for folder in os.listdir(UPLOAD_FOLDER):
            folder_path = os.path.join(UPLOAD_FOLDER, folder)
            if os.path.isdir(folder_path):
                folders[folder] = os.listdir(folder_path)
    return render_template("index.html", folders=folders)

# Télécharger un fichier individuel
@app.route("/download/<folder>/<filename>")
def download_file(folder, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder), filename, as_attachment=True)

# Télécharger tout le dossier en zip
@app.route("/download-zip/<folder>")
def download_zip(folder):
    folder_path = os.path.join(UPLOAD_FOLDER, folder)
    zip_path = os.path.join(UPLOAD_FOLDER, f"{folder}.zip")
    if not os.path.exists(zip_path):
        import shutil
        shutil.make_archive(zip_path.replace(".zip", ""), "zip", folder_path)
    return send_from_directory(UPLOAD_FOLDER, f"{folder}.zip", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
