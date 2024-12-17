from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import json
import threading
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "downloads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Fonction pour configurer Selenium en tâche de fond
def setup_selenium():
    options = Options()
    options.add_argument("--headless")  # Mode sans interface
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

# Fonction pour générer le JSON
def generate_json(folder_url, json_path):
    driver = setup_selenium()
    try:
        driver.get(folder_url)
        titles_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.track-title'))
        )
        titles = [{"title": title.text.strip()} for title in titles_elements if title.text.strip()]
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(titles, json_file, ensure_ascii=False, indent=4)
    finally:
        driver.quit()

# Fonction pour télécharger les musiques
def download_music(folder_url, folder_name):
    driver = setup_selenium()
    try:
        json_path = os.path.join(UPLOAD_FOLDER, f"{folder_name}.json")
        with open(json_path, "r", encoding="utf-8") as file:
            file_names = json.load(file)

        # Récupérer l'image de couverture
        cover_element = driver.find_element(By.XPATH, '//*[@id="tralbumArt"]/a/img')
        cover_url = cover_element.get_attribute('src')
        cover_data = requests.get(cover_url).content

        for index, song in enumerate(file_names, start=1):
            audio_element = driver.find_element(By.CSS_SELECTOR, 'audio')
            audio_url = audio_element.get_attribute('src')

            filename = song['title'].replace(" ", "_") + ".mp3"
            file_path = os.path.join(UPLOAD_FOLDER, folder_name, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            audio_response = requests.get(audio_url)
            with open(file_path, "wb") as file:
                file.write(audio_response.content)
            add_cover_to_mp3(file_path, cover_data)
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
        print(f"Erreur lors de l'ajout de la couverture : {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        folder_url = request.form.get("folder_url")
        folder_name = folder_url.split("/")[-1].replace(" ", "_")
        json_path = os.path.join(UPLOAD_FOLDER, f"{folder_name}.json")

        threading.Thread(target=generate_json, args=(folder_url, json_path)).start()
        threading.Thread(target=download_music, args=(folder_url, folder_name)).start()

        return redirect(url_for("download_page", folder_name=folder_name))
    return render_template("index.html")

@app.route("/downloads/<folder_name>")
def download_page(folder_name):
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    files = os.listdir(folder_path) if os.path.exists(folder_path) else []
    return render_template("downloads.html", files=files, folder_name=folder_name)

@app.route("/download/<folder_name>/<filename>")
def download_file(folder_name, filename):
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    return send_from_directory(folder_path, filename, as_attachment=True)

@app.route("/download-all/<folder_name>")
def download_all(folder_name):
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    zip_path = os.path.join(UPLOAD_FOLDER, f"{folder_name}.zip")
    if not os.path.exists(zip_path):
        import shutil
        shutil.make_archive(zip_path.replace(".zip", ""), "zip", folder_path)
    return send_from_directory(UPLOAD_FOLDER, f"{folder_name}.zip", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
