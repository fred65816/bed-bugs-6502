import sqlite3
from .apiclasses import Declaration, NeighborhoodTotal
from .apiclasses import NewDeclaration, Profile


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/db.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    # retourne les déclarations pour le point A2
    def get_declarations(self, text_search):
        cursor = self.get_connection().cursor()
        cursor.execute(("select d.declaration_num, d.declaration_date,"
                        " d.inspection_date, d.extermination_num,"
                        " d.treatment_start_date, d.treatment_end_date,"
                        " n.neighborhood_code, n.name, di.name,"
                        " d.x_coord, d.y_coord, d.longitude, d.latitude"
                        " from declarations as d"
                        " inner join neighborhoods as n"
                        " on d.neighborhood_id = n.id"
                        " inner join districts as di"
                        " on n.district_id = di.id"
                        " where (n.name like ?"
                        " or di.name like ?) and d.is_visible = ?"),
                       (text_search, text_search, True))
        declarations = cursor.fetchall()
        return declarations

    # retourne les déclarations pour le point A4
    def api_get_declarations(self, start_date, end_date):
        cursor = self.get_connection().cursor()
        cursor.execute(("select d.declaration_num, d.declaration_date,"
                        " d.inspection_date, d.extermination_num,"
                        " d.treatment_start_date, d.treatment_end_date,"
                        " n.neighborhood_code, n.name, di.name,"
                        " d.x_coord, d.y_coord, d.longitude, d.latitude"
                        " from declarations as d"
                        " inner join neighborhoods as n"
                        " on d.neighborhood_id = n.id"
                        " inner join districts as di"
                        " on n.district_id = di.id"
                        " where date(d.declaration_date) >= date(?)"
                        " and date(d.declaration_date) <= date(?)"
                        " and d.is_visible = ?"),
                       (start_date, end_date, True))
        declarations = cursor.fetchall()
        if len(declarations) == 0:
            return None
        return [Declaration(d[0], d[1], d[2], d[3], d[4], d[5], d[6],
                            d[7], d[8], d[9], d[10], d[11], d[12])
                for d in declarations]

    # retourne le nombre de déclaration pour
    # chaque quartier pour le point C1
    def api_get_neighborhoods_total(self):
        cursor = self.get_connection().cursor()
        cursor.execute(("select n.name, count(*) as total"
                        " from declarations d"
                        " inner join neighborhoods n"
                        " on d.neighborhood_id = n.id"
                        " where d.is_visible = ?"
                        " group by n.name order by total asc;"),
                       (True,))
        neighborhoods = cursor.fetchall()
        if len(neighborhoods) == 0:
            return None
        return [NeighborhoodTotal(n[0], n[1]) for n in neighborhoods]

    # sauvegarde le profil au point E1
    def api_save_profile(self, profile):
        connection = self.get_connection()

        # création du profil
        connection.execute(("insert into profiles(first_name,"
                            " last_name, email, salt, hash, picture)"
                            " values(?, ?, ?, ?, ?, ?)"),
                           (profile.first_name, profile.last_name,
                            profile.email, profile.salt,
                            profile.pwd_hash, None))
        connection.commit()

        # mise du profil ID dans l'instance profil
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        result = cursor.fetchall()
        profile.id = result[0][0]

        # Ajout des quartiers à surveiller
        for neighborhood in profile.neighborhoods:
            connection.execute(("insert into profiles_neighborhoods"
                                "(profile_id, neighborhood_id) values(?,"
                                "(select id from neighborhoods"
                                " where name = ?))"),
                               (profile.id, neighborhood))
            connection.commit()

        return profile

    # sauvegarde la nouvelle déclaration au point D1
    def api_save_declaration(self, declaration):
        connection = self.get_connection()

        # création de la nouvelle déclaration
        connection.execute(("insert into declarations(declaration_date,"
                            " inspection_date, neighborhood_id, is_visible)"
                            " values(?, ?,"
                            " (select id from neighborhoods"
                            " where name = ?), ?)"),
                           (declaration.declaration_date,
                            declaration.inspection_date,
                            declaration.neighborhood, True))
        connection.commit()

        # mise du numéro de déclaration
        # dans l'instance declaration
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        result = cursor.fetchall()
        declaration.declaration_num = result[0][0]

        # création de l'entrée pour la table avec infos extra
        connection.execute(("insert into declarations_extra(declaration_num,"
                            " address, first_name, last_name, description)"
                            " values(?, ?, ?, ?, ?)"),
                           (declaration.declaration_num, declaration.address,
                            declaration.first_name, declaration.last_name,
                            declaration.description))
        connection.commit()

        return declaration

    # supprime une déclaration au point D2
    def api_delete_declaration(self, declaration_num):
        connection = self.get_connection()
        connection.execute(("update declarations set is_visible = ?"
                            " where declaration_num = ?"),
                           (False, declaration_num))
        connection.commit()

    # supprime les déclarations au point D3
    def api_delete_declarations(self, start_date,
                                end_date, neighborhood):
        connection = self.get_connection()
        connection.execute(("update declarations"
                            " set is_visible = ?"
                            " where date(declaration_date) >= date(?)"
                            " and date(declaration_date) <= date(?)"
                            " and neighborhood_id in"
                            " (select id from neighborhoods"
                            " where name = ?)"),
                           (False, start_date, end_date, neighborhood))
        connection.commit()

    # retourne true si un numéro de déclaration existe
    def declaration_exist(self, declaration_num):
        cursor = self.get_connection().cursor()
        cursor.execute(("select declaration_num from declarations"
                        " where declaration_num = ?"),
                       (declaration_num,))
        ids = cursor.fetchall()
        if len(ids) == 0:
            return False
        return True

    # retourne true si un email est présent dans un profil
    def is_email_present(self, email):
        cursor = self.get_connection().cursor()
        cursor.execute(("select email from profiles where email = ?"),
                       (email,))
        email = cursor.fetchone()
        return False if email is None else True

    # retourne le nom d'arrondissement correspondant à
    # un nom de quartier
    def get_district_neighborhood(self, neighborhood):
        cursor = self.get_connection().cursor()
        cursor.execute(("select d.name from districts as d"
                        " inner join neighborhoods as n"
                        " on n.district_id = d.id"
                        " where n.name = ?"), (neighborhood,))
        district = cursor.fetchone()
        if district is None:
            return None
        else:
            return district[0]

    # retourne la liste des arrondissements
    def get_districs(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select name from districts")
        districts = [item[0] for item in cursor.fetchall()]
        return districts

    # retourne la liste d'arrondissements avec IDs
    def get_districs_with_id(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select id, name from districts order by id asc")
        districts = cursor.fetchall()
        return districts

    # retourne la liste des quartiers
    def get_neighborhoods(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select name from neighborhoods order by name asc")
        neighborhoods = [item[0] for item in cursor.fetchall()]
        return neighborhoods

    # retourne la liste des quartiers et leur ID
    # d'arrondissement correspondant
    def get_neighborhoods_with_district_id(self):
        cursor = self.get_connection().cursor()
        cursor.execute("select d.id, n.name from neighborhoods as n"
                       " inner join districts as d"
                       " on d.id = n.district_id order by n.name asc")
        neighborhoods = cursor.fetchall()
        return neighborhoods

    # retourne le nom d'un quartier, son code correspondant
    # et son nom de district d'après le ID de quartier
    def get_neighborhood_data(self, id):
        cursor = self.get_connection().cursor()
        cursor.execute("select n.name, n.neighborhood_code, d.name"
                       " from neighborhoods as n"
                       " inner join districts as d"
                       " on d.id = n.district_id")
        neighborhood = cursor.fetchone()
        return neighborhood

    # insère un arrondissement (point A3)
    def insert_district(self, name):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(("insert into districts(name)"
                        " values(?)"), (name,))
        connection.commit()

    # insère un quartier résidentiel (point A3)
    def insert_neighborhood(self, name, neighborhood_code, district_name):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(("insert into neighborhoods"
                        "(name, neighborhood_code, district_id)"
                        " values(?,?,"
                        "(select id from districts where name=?))"),
                       (name, neighborhood_code, district_name))
        connection.commit()

    # retourne true si une déclaration avec le même numéro
    # est déja présente, sinon false (point A3)
    def is_declaration_present(self, declaration_num):
        cursor = self.get_connection().cursor()
        cursor.execute(("select declaration_num from declarations"
                        " where declaration_num=?"), (declaration_num,))
        declaration_num = cursor.fetchone()
        return False if declaration_num is None else True

    # insère une déclaration (point A3)
    def insert_declaration(self, declaration_num, declaration_date,
                           inspection_date, extermination_num,
                           treatment_start_date, treatment_end_date,
                           neighborhood_name, x_coord, y_coord,
                           longitude, latitude):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(("insert into declarations"
                        "(declaration_num, declaration_date,"
                        " inspection_date, extermination_num,"
                        " treatment_start_date, treatment_end_date,"
                        " neighborhood_id, x_coord, y_coord,"
                        " longitude, latitude, is_visible)"
                        " values(?,?,?,?,?,?,"
                        "(select id from neighborhoods where name=?),"
                        " ?,?,?,?,?)"),
                       (declaration_num, declaration_date,
                        inspection_date, extermination_num,
                        treatment_start_date, treatment_end_date,
                        neighborhood_name, x_coord, y_coord,
                        longitude, latitude, True))
        connection.commit()
