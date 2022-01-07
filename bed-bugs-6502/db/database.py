import sqlite3


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    # insère un arrondissement
    def insert_district(self, name):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(("insert into districts(name)"
                        " values(?)"), (name,))
        connection.commit()

    # insère un quartier résidentiel
    def insert_neighborhood(self, name, neighborhood_code, district_name):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(("insert into neighborhoods"
                        "(name, neighborhood_code, district_id)"
                        " values(?,?,"
                        "(select id from districts where name=?))"),
                       (name, neighborhood_code, district_name))
        connection.commit()

    # retourne true si une déclaration avec un même numéro
    # est déja présente, sinon false
    def is_declaration_present(self, declaration_num):
        cursor = self.get_connection().cursor()
        cursor.execute(("select declaration_num from declarations"
                        " where declaration_num=?"), (declaration_num,))
        declaration_num = cursor.fetchone()
        return False if declaration_num is None else True

    # insère une déclaration
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
