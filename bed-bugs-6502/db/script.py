import csv
import requests
import sys
from database import Database

database = None


def get_db():
    global database
    if database is None:
        database = Database()
    return database


def close_connection():
    global database
    if database is not None:
        database.disconnect()


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
        print((f"Erreur: La requête à https://data.montreal.ca"
               f"a retourné un code {request.status_code}"))
        sys.exit(0)

    # conversion de la requête au format utf-8
    content = request.content.decode("utf-8")
    # conversion du fichier csv en liste de listes
    list_csv = list(csv.reader(content.splitlines()))
    # on enlève la ligne de nom des champs
    list_csv.pop(0)
    return list_csv


# insère les arrondissements et quartiers du fichier CSV
# dans la base de donnée.
def csv_to_dn(list_csv):
    districts = []
    neighborhoods = []

    for entry in list_csv:
        # l'arrondissement pour Dorval est vide donc on crée "N/D"
        district = entry[8].strip() if entry[8] != "" else "N/D"
        neighborhood = entry[7].strip()

        # ajout de l'arrondissement à la liste
        if(district not in districts):
            districts.append(district)
        result = [n[0] for n in neighborhoods
                  if n[0] == neighborhood and n[2] == district]

        # ajout du quartier à la liste
        if not result:
            neighborhoods.append([neighborhood, entry[6], district])

    # ajout des arrondissements à la BD
    for d in districts:
        try:
            get_db().insert_district(d)
        except Exception as error:
            print(f"Erreur avec l'insertion de l'arrondissement {d}: {error}")
            sys.exit(0)

    # ajout des quartiers à la BD
    for n in neighborhoods:
        try:
            get_db().insert_neighborhood(n[0], n[1], n[2])
        except Exception as error:
            print(f"Erreur avec l'insertion du quartier {n[0]}: {error}.")
            sys.exit(0)


# insère les déclarations du fichier CSV
# dans la base de donnée.
def csv_to_decl(list_csv):
    for e in list_csv:
        e[0] = int(e[0])

        # certains champs peuvent être null
        e[2] = None if e[2] == '' else e[2]
        e[3] = None if e[3] == '' else int(e[3])
        e[4] = None if e[4] == '' else e[4]
        e[5] = None if e[5] == '' else e[5]

        # insertion de la déclaration
        try:
            if not get_db().is_declaration_present(e[0]):
                get_db().insert_declaration(e[0], e[1].replace("T", " "),
                                            e[2], e[3], e[4], e[5],
                                            e[7], float(e[9]), float(e[10]),
                                            float(e[11]), float(e[12]))
                print(f"insertion de la déclaration #{e[0]}")
            else:
                print(f"La déclaration #{e[0]} est déja présente")
        except Exception as error:
            print((f"Erreur avec l'insertion de la"
                  f" déclaration #{e[0]}: {error}."))

    close_connection()


if __name__ == "__main__":
    list_csv = import_csv()
    csv_to_dn(list_csv)
    csv_to_decl(list_csv)
