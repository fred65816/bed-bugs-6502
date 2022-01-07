
from flask import Flask, request, render_template
from flask import redirect, url_for, flash, g, jsonify
from flask_json_schema import JsonSchema, JsonValidationError
from .database import Database
from os import urandom
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import csv
import requests
import sys
import hashlib
import uuid
from datetime import date, datetime
from .apiclasses import Declaration, NeighborhoodTotal
from .apiclasses import Profile, NewDeclaration
from .schemas import profile_insert_schema, declaration_insert_schema
import json
from dicttoxml import dicttoxml
import pandas as pd
import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import tweepy as tw
from dateutil.relativedelta import relativedelta

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_url_path="", static_folder="static")

schema = JsonSchema(app)

app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY")
app.config['JSON_AS_ASCII'] = False


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


# valide une date (retour true si valide)
def date_is_valid(str_date):
    try:
        datetime.strptime(str_date, "%Y-%m-%d")
        return True
    except ValueError as e:
        return False


@app.route("/", methods=["GET", "POST"])
def search_get():
    error = None

    try:
        # utilisé pour la liste déroulante
        neighborhoods = get_db().get_neighborhoods()
    except Exception:
        return redirect(url_for("error_database"))

    if request.method == "POST":
        search = request.form["textsearch"]

        # validation de la recherche
        if(len(search) < 3 or len(search) > 100):
            error = "Vous devez entrer une chaîne entre 3 et 100 caractères"
            return render_template("search.html",
                                   error=error,
                                   textsearch=text_search,
                                   neighborhoods=neighborhoods)
        else:
            return redirect(url_for("results_get", search=search))
    else:
        return render_template("search.html",
                               error=error,
                               neighborhoods=neighborhoods)


# point A2
@app.route("/results")
def results_get():
    search = request.args.get("search")

    # si le query parameter est manquant
    if search is None:
        return redirect(url_for("error_bad_request"))

    search = f"%{search}%"
    decl = None
    num_decl = 0

    try:
        decl = get_db().get_declarations(search)
        num_decl = 0 if decl is None else len(decl)
    except Exception:
        return redirect(url_for("error_database"))

    return render_template("results.html", declarations=decl, num=num_decl)


# point D3
@app.route("/new-declaration")
def declaration_add():
    districts = get_db().get_districs_with_id()
    neighborhoods = get_db().get_neighborhoods_with_district_id()
    return render_template("declaration.html", districts=districts,
                           neighborhoods=neighborhoods)


# point A4
@app.route('/api/declarations', methods=["GET"])
def api_get_declarations():
    declarations = None
    start_date = request.args.get("du")
    end_date = request.args.get("au")

    # si il manque un argument d'url
    if start_date is None or end_date is None:
        return jsonify({"error": "missing query param(s)"}), 400

    # si une des dates est invalide
    if not date_is_valid(start_date) or not date_is_valid(end_date):
        return jsonify({"error": "invalid date(s)"}), 400

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # si la date de fin est plus petite
    # que la date de début
    if end_date < start_date:
        return jsonify({"error": "end_date is before start_date"}), 400

    try:
        declarations = get_db().api_get_declarations(start_date, end_date)
    except Exception:
        return "", 500

    # si il n'y a aucun résultat
    # on retourne un tableau vide
    if declarations is None:
        return jsonify([]), 200

    return jsonify([d.asDictionary() for d in declarations])


# point C1
@app.route('/api/neighborhoods', methods=["GET"])
def api_get_neighborhoods_total():
    neighborhoods = None

    try:
        neighborhoods = get_db().api_get_neighborhoods_total()
    except Exception:
        return "", 500

    return jsonify([n.asDictionary() for n in neighborhoods])


# point C2
@app.route('/api/neighborhoods/xml', methods=["GET"])
def api_get_neighborhoods_total_xml():
    neighborhoods = None

    try:
        neighborhoods = get_db().api_get_neighborhoods_total()
    except Exception:
        return "", 500

    return dicttoxml([n.asDictionary() for n in neighborhoods],
                     attr_type=False)


# point C3
@app.route('/api/neighborhoods/csv', methods=["GET"])
def api_get_neighborhoods_total_csv():
    neighborhoods = None

    try:
        neighborhoods = get_db().api_get_neighborhoods_total()
    except Exception:
        return "", 500

    # Panda dataframe to csv
    return pd.DataFrame([n.asDictionary() for n in neighborhoods],
                        columns=["declaration_total",
                                 "neighborhood_name"]).to_csv(encoding="utf-8",
                                                              index=False)


# point E1
@app.route('/api/profile', methods=["POST"])
@schema.validate(profile_insert_schema)
def api_create_profile():
    data = request.get_json()

    # on vérifie s'il y a un autre utilisateur avec le même email
    try:
        if get_db().is_email_present(data["email"]):
            return jsonify({"error": "email already exists"}), 400
    except Exception:
        return "", 500

    # génération du salt et du hash du mot de passe
    password = data["password"]
    salt = uuid.uuid4().hex
    pwd_hash = hashlib.sha512(str(password + salt).encode("utf-8")).hexdigest()

    # suppression des blancs au début et fin de chaînes
    first_name = data["first_name"].strip()
    last_name = data["last_name"].strip()

    profile = Profile(None, first_name, last_name, data["email"],
                      salt, pwd_hash, data["neighborhoods"])

    # savegarde du profil
    try:
        profile = get_db().api_save_profile(profile)
    except Exception:
        return "", 500

    return jsonify(profile.asDictionary()), 201


# point D1
@app.route('/api/declaration', methods=["POST"])
@schema.validate(declaration_insert_schema)
def api_create_declaration():
    data = request.get_json()
    inspection_date = data["inspection_date"]
    first_name = data["first_name"].strip()
    last_name = data["last_name"].strip()
    address = data["address"].strip()
    neighborhood = data["neighborhood"]
    district = data["district"]

    # la description est optionelle
    if "description" not in data:
        description = None
    else:
        description = data["description"].strip()

    # on regarde si c'est une vrai date
    # et non une date comme le 30 février
    if not date_is_valid(inspection_date):
        return jsonify({"error": "invalid date"}), 400

    # date de déclaration
    declaration_date = date.today()
    year_before = declaration_date - relativedelta(years=1)
    year_after = declaration_date + relativedelta(years=1)

    inspection_date = datetime.strptime(inspection_date, "%Y-%m-%d").date()

    # la date de visite doit être moins de 1 an avant ou après aujourd'hui
    if inspection_date < year_before or inspection_date > year_after:
        return jsonify({"error": "invalid date"}), 400

    # validation que l'arrondissement correspond au bon quartier
    try:
        verified_district = get_db().get_district_neighborhood(neighborhood)
    except Exception:
        return "", 500

    if verified_district != district:
        return jsonify({"error": "invalid district"}), 400

    declaration = NewDeclaration(None, first_name, last_name,
                                 address, inspection_date.isoformat(),
                                 description, neighborhood,
                                 district, declaration_date.isoformat())

    try:
        declaration = get_db().api_save_declaration(declaration)
    except Exception:
        return "", 500

    return jsonify(declaration.asDictionary()), 201


# point D2
@app.route('/api/declaration/<int:declaration_num>', methods=["DELETE"])
def api_delete_declaration(declaration_num):
    try:
        # si la déclaration n'existe pas
        if not get_db().declaration_exist(declaration_num):
            return "", 404
        else:
            get_db().api_delete_declaration(declaration_num)
            return "", 200
    except Exception:
        return "", 500


# point D3
@app.route('/api/declarations/delete', methods=["DELETE"])
def api_delete_declarations():
    start_date = request.args.get("du")
    end_date = request.args.get("au")
    neighborhood = request.args.get("quartier")

    # si il manque un argument d'url
    if (start_date is None or end_date is None
       or neighborhood is None):
        return jsonify({"error": "missing query param(s)"}), 400

    # si une des date n'est pas valide
    if not date_is_valid(start_date) or not date_is_valid(end_date):
        return jsonify({"error": "invalid date(s)"}), 400

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # si la date de début est plus
    # grande que la date de fin
    if end_date < start_date:
        return jsonify({"error": "end date is smaller than start date"}), 400

    try:
        get_db().api_delete_declarations(start_date.isoformat(),
                                         end_date.isoformat(),
                                         neighborhood)
    except Exception:
        return "", 500

    return "", 200


@app.errorhandler(JsonValidationError)
def validation_error(e):
    errors = [validation_error.message for validation_error in e.errors]
    return jsonify({"error": e.message, "errors": errors}), 400


@app.route("/error-bad-request", methods=["GET"])
def error_bad_request():
    return render_template("400.html"), 400


@app.route("/error-database", methods=["GET"])
def error_database():
    return render_template("500.html"), 500


@app.route('/doc', methods=["GET"])
def api_get_doc():
    return render_template("doc.html")


# Code du Background Scheduler
# télécharge le fichier csv
# et retourne un liste où chaque ligne de la liste
# est un liste avec les champs d'une déclaration
def import_csv():
    URL = ("https://data.montreal.ca/dataset/"
           "49ff9fe4-eb30-4c1a-a30a-fca82d4f5c2f/"
           "resource/6173de60-c2da-4d63-bc75-0607cb8dcb74/"
           "download/declarations-exterminations-punaises-de-lit.csv")

    print("Téléchargement du fichier CSV..")
    session = requests.Session()
    request = session.get(URL)

    # erreur si la requête ne retourne pas un code 200
    if request.status_code != requests.codes.ok:
        print((f"Erreur: La requête à https://data.montreal.ca "
               f"a retourné un code {request.status_code}"))
        return False

    # conversion de la requête au format utf-8
    content = request.content.decode("utf-8")
    # conversion du fichier csv en liste de listes
    list_csv = list(csv.reader(content.splitlines()))
    # on enlève la ligne de nom des champs
    list_csv.pop(0)
    return list_csv


# Ajoute les quartiers et arrondissements manquant
# au besoin
def csv_to_dn(list_csv):
    # liste des quartiers et arrondissements
    try:
        districts = get_db().get_districs()
        neighborhoods = get_db().get_neighborhoods()
    except Exception:
        print(("Erreur avec la requête des arrondissements"
               " et quartiers"))
        # si erreur avec la BD, on sort de la fonction
        # pour éviter des insertions de quartier et
        # arrondissements en double dans la BD
        return

    for entry in list_csv:
        district = entry[8]
        neighborhood = entry[7]

        # si l'arrondissement n'est pas présent on l'insère
        if district not in districts and district != "":
            try:
                get_db().insert_district(district)
            except Exception as error:
                print((f"Erreur avec l'insertion de "
                       f"l'arrondissement {district}: {error}"))

        # si le quartier n'est pas présent on l'insère
        if neighborhood not in neighborhoods:
            try:
                get_db().insert_neighborhood(neighborhood, entry[6], district)
            except Exception as error:
                print((f"Erreur avec l'insertion du "
                       f"quartier {neighborhood}: {error}."))


# insère les nouvelles déclarations du fichier CSV
# dans la base de donnée.
def csv_to_decl(list_csv):
    new_declarations = []

    for e in list_csv:
        e[0] = int(e[0])

        # certains champs peuvent être null
        e[2] = None if e[2] == '' else e[2]
        e[3] = None if e[3] == '' else int(e[3])
        e[4] = None if e[4] == '' else e[4]
        e[5] = None if e[5] == '' else e[5]
        e[1] = e[1].replace("T", " ")

        # insertion de la déclaration dans la BD
        try:
            if not get_db().is_declaration_present(e[0]):
                get_db().insert_declaration(e[0], e[1],
                                            e[2], e[3], e[4], e[5],
                                            e[7], float(e[9]), float(e[10]),
                                            float(e[11]), float(e[12]))
                print(f"insertion de la déclaration #{e[0]}")

                declaration = [e[0], e[1], e[2], e[3],
                               e[4], e[5], e[6], e[7],
                               e[8], e[9], e[10], e[11],
                               e[12]]

                # ajout à la liste pour les points B1-B2
                new_declarations = add_declaration(new_declarations,
                                                   declaration)
            else:
                print(f"La déclaration #{e[0]} est déja présente")
        except Exception as error:
            print((f"Erreur avec l'insertion de la "
                   f"déclaration #{e[0]}: {error}."))

    # si on a au moins un nouvelle déclaration
    # on envoie le email et le(s) tweet(s) des points B1-B2
    if len(new_declarations) > 0:
        send_email(new_declarations)
        send_tweets(new_declarations)


# job du background scheduler
def jobs_seq():
    with app.app_context():
        list_csv = import_csv()
        if list_csv:
            csv_to_dn(list_csv)
            csv_to_decl(list_csv)


# ajoute une nouvelle déclaration à la liste
# pour envoie de courriel en B1
def add_declaration(new_declarations, declaration):

    # vérification de doublons
    for nd in new_declarations:
        if declaration[0] == nd[0]:
            return new_declarations

    # ajout à la liste
    new_declarations.append(declaration)
    return new_declarations


# envoie le email pour le point B1
def send_email(new_declarations):
    destination_address = get_dest_address()
    source_address = os.getenv("SOURCE_EMAIL")
    email_password = os.getenv("EMAIL_PASSWORD")
    subject = "Nouvelles déclarations d'extermination"
    html = get_html(new_declarations)

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = source_address
    msg['To'] = destination_address

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(source_address, email_password)
    text = msg.as_string()
    server.sendmail(source_address, destination_address, text)
    server.quit()


# retour l'adresse du destinataire
# pour le point B1
def get_dest_address():
    with open(r"mail.yaml") as file:
        fields = yaml.full_load(file)
        return fields["dest_email"]


# construit le tableau html pour le email du point B1
def get_html(new_declarations):
    html = "<html><head></head><body><table>"
    html += "<tr>"
    html += ("<th>ID</th>"
             "<th>Date déclaration</th>"
             "<th>Date inspection</th>"
             "<th>Nb. exterminations</th>"
             "<th>Date début traitement</th>"
             "<th>Date fin traitement</th>"
             "<th>No. quartier</th>"
             "<th>Quartier</th>"
             "<th>Arrondissement</th>"
             "<th>X coord</th>"
             "<th>Y coord</th>"
             "<th>Longitude</th>"
             "<th>Latitude</th>")
    html += "</tr>"

    for i in range(0, len(new_declarations)):
        d = new_declarations[i]

        # champs pouvant être null
        d[2] = "N/D" if d[2] is None else d[2]
        d[3] = "N/D" if d[3] is None else d[3]
        d[4] = "N/D" if d[4] is None else d[4]
        d[5] = "N/D" if d[5] is None else d[5]

        # construction du table
        html += "<tr>"
        for j in range(0, len(d)):
            html += "<td>" + str(d[j]) + "</td>"
        html += "</tr>"

    html += "</table></body></html>"

    return html


# envoie le ou les tweets pour le point B2
def send_tweets(new_declarations):

    # liste des contenus des tweets
    tweets = get_tweet_contents(new_declarations)

    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_TOKEN_SECRET")

    # authentification à l'API de Twitter
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)

    today = datetime.now()
    today = today.strftime("%Y-%m-%d")
    total = len(tweets)
    index = 1

    # pour chaque contenu
    for tweet in tweets:
        # première ligne du tweet (e.g. "2021-04-25 (1/1)")
        tweet_header = today + " (" + str(index) + "/" + str(total) + ")\n"

        # envoie du tweet
        tweet_content = tweet_header + tweet + "\n#bedbugs"
        api.update_status(tweet_content)
        index = index + 1


# retourne un liste de contenus de tweets
def get_tweet_contents(new_declarations):
    # liste des quartiers avec le nombre de déclarations
    neighborhoods = populate_neighborhoods(new_declarations)
    tweets = []
    max_length = 250
    current_tweet = ""

    for i in range(0, len(neighborhoods)):
        # longeur du quartier plus nombre
        length = len(neighborhoods[i][0]) + len(str(neighborhoods[i][1])) + 4

        # s'il reste de la place pour l'ajouter
        # au tweet courant on l'ajoute
        if max_length - length >= 0:
            current_tweet = (current_tweet + "\n" + neighborhoods[i][0] +
                             ": " + str(neighborhoods[i][1]))
            max_length = max_length - length
        else:
            # sinon on ajoute le tweet à la liste et on
            # en commence un nouveau
            tweets.append(current_tweet)
            current_tweet = ("\n" + neighborhoods[i][0] +
                             ": " + str(neighborhoods[i][1]))
            max_length = 250 - length

        # on ajoute le tweet courant après le
        # dernier quartier de la liste
        if i == len(neighborhoods) - 1:
            tweets.append(current_tweet)

    return tweets


# retourne un liste de quartiers avec
# nombre de déclarations pour le point B2
def populate_neighborhoods(new_declarations):
    neighborhoods = []

    for d in new_declarations:
        found = False
        for i in range(0, len(neighborhoods)):
            if found:
                break
            # si le nom match on incrémente de 1
            if neighborhoods[i][0] == d[7]:
                neighborhoods[i][1] = neighborhoods[i][1] + 1
                found = True

        # ajout d'un nouveau quartier à la liste
        if not found:
            neighborhood = [d[7], 1]
            neighborhoods.append(neighborhood)

    return neighborhoods


scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(jobs_seq, 'cron', hour=0, id="update")
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
