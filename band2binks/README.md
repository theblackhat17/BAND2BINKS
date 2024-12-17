
# **BAND2BINKS** 🎵  
### **Application Flask pour télécharger des musiques depuis une URL Bandcamp**

---

## **Description du Projet** 📖

BAND2BINKS est une application web développée avec Flask permettant de :
- **Télécharger automatiquement des musiques** à partir d'une URL Bandcamp.
- **Générer un dossier organisé** contenant les fichiers MP3 et l'image de couverture associée.
- Proposer le téléchargement **individuel** de chaque musique ou **global** sous forme de fichier **ZIP**.
- Offrir une interface moderne avec des fonctionnalités telles que le **repli/dépli des dossiers**.

---

## **Fonctionnalités** 🚀

1. **Téléchargement Automatique** :
   - L'utilisateur saisit simplement l'URL d'une page Bandcamp.
   - Le JSON nécessaire est généré automatiquement et supprimé après utilisation.

2. **Organisation des Fichiers** :
   - Chaque dossier contient :
     - Les musiques téléchargées au format `.mp3`.
     - L'image de couverture `cover.jpg` associée.

3. **Téléchargement Sélectif** :
   - Possibilité de télécharger :
     - **Un seul fichier MP3**.
     - **Tout le dossier en format ZIP**.

4. **Interface Moderne** :
   - Affichage de l'image de couverture à côté de chaque dossier.
   - Repli/dépli des dossiers avec un bouton **toggle**.
   - Utilisation d'icônes élégantes pour le bouton **Télécharger** via Font Awesome.

---

## **Technologies Utilisées** 🛠️

- **Python** (Flask, Selenium, Requests, Mutagen)
- **HTML/CSS** (Bootstrap 5 pour un design moderne)
- **Font Awesome** (pour les icônes)
- **Selenium** (pour automatiser la récupération des fichiers et des titres)

---

## **Prérequis** ✅

Pour exécuter ce projet, vous devez disposer des éléments suivants :

1. **Python 3.x** installé sur votre machine.
2. Un navigateur **Chrome** et le **ChromeDriver** correspondant.
3. Les bibliothèques Python nécessaires (voir `requirements.txt`).

---

## **Installation** ⚙️

1. **Cloner le projet** depuis GitHub :
   ```bash
   git clone https://github.com/votre-utilisateur/band2binks.git
   cd band2binks
   ```

2. **Créer un environnement virtuel** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Télécharger ChromeDriver** :
   - Rendez-vous sur [ChromeDriver](https://sites.google.com/chromium.org/driver/).
   - Placez le fichier dans un dossier accessible par le système.

---

## **Exécution de l'Application** ▶️

1. **Lancer le serveur Flask** :
   ```bash
   python app.py
   ```

2. **Accéder à l'application** dans votre navigateur :
   ```
   http://127.0.0.1:5000
   ```

3. **Utilisation** :
   - Entrez une URL Bandcamp dans le champ prévu.
   - Les musiques et l'image de couverture seront téléchargées automatiquement.
   - Parcourez les dossiers pour voir les fichiers et utilisez les boutons de téléchargement.

---

## **Arborescence du Projet** 📂

```
band2binks/
│
├── app.py                # Application principale Flask
├── requirements.txt      # Liste des dépendances Python
├── templates/
│   └── index.html        # Interface utilisateur HTML
├── static/
│   ├── downloads/        # Contient les fichiers téléchargés
│   └── folder.png        # Icône de dossier par défaut
└── README.md             # Documentation du projet
```

---

## **Exemples d'Utilisation** 🎥

1. **Entrer une URL valide** :
   - Exemple : `https://nom_artiste.bandcamp.com/album/pack_musique`.

2. **Téléchargement des musiques** :
   - Les fichiers seront organisés dans un dossier nommé **Pack_Musique**.
   - Une image de couverture `cover.jpg` sera téléchargée.

3. **Fonctionnalités de l'interface** :
   - **Télécharger tout** : Télécharge l'ensemble du dossier en format ZIP.
   - **Télécharger individuellement** : Télécharge chaque fichier MP3 séparément.
   - **Replier/Déplier** : Affiche ou masque les fichiers dans un dossier.

---

## **Dépendances** 🧩

- Flask
- Selenium
- Requests
- Mutagen
- Bootstrap 5
- Font Awesome

Installez-les via :
```bash
pip install -r requirements.txt
```

---

## **Améliorations Futures** 🌟

- Ajout d'une barre de progression pour les téléchargements.
- Gestion des erreurs plus détaillée pour les URL invalides.
- Support multi-utilisateur avec gestion des sessions.

---

## **Auteur** ✍️

- **Nom** : Votre Nom  
- **GitHub** : [Votre Profil GitHub](https://github.com/votre-utilisateur)  
- **Contact** : [Votre Email](mailto:votre-email@example.com)

---

## **Licence** 📄

Ce projet est sous licence **MIT**. Vous êtes libre de le modifier et de le distribuer.

---

🎉 **Merci d'utiliser BAND2BINKS !** Si vous avez des questions ou des suggestions, n'hésitez pas à ouvrir une **issue** ou une **pull request**. 🚀
