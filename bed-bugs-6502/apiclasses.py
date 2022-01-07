class Declaration:
    def __init__(self, declaration_num, declaration_date,
                 inspection_date, extermination_num,
                 treatment_start_date, treatment_end_date,
                 neighborhood_num, neighborhood_name,
                 district_name, x_coord, y_coord,
                 longitude, latitude):
        self.declaration_num = declaration_num
        self.declaration_date = declaration_date
        self.inspection_date = inspection_date
        self.extermination_num = extermination_num
        self.treatment_start_date = treatment_start_date
        self.treatment_end_date = treatment_end_date
        self.neighborhood_num = neighborhood_num
        self.neighborhood_name = neighborhood_name
        self.district_name = district_name
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.longitude = longitude
        self.latitude = latitude

    def asDictionary(self):
        return {"declaration_num": self.declaration_num,
                "declaration_date": self.declaration_date,
                "inspection_date": self.inspection_date,
                "extermination_num": self.extermination_num,
                "treatment_start_date": self.treatment_start_date,
                "treatment_end_date": self.treatment_end_date,
                "neighborhood_num": self.neighborhood_num,
                "neighborhood_name": self.neighborhood_name,
                "district_name": self.district_name,
                "x_coord": self.x_coord,
                "y_coord": self.y_coord,
                "longitude": self.longitude,
                "latitude": self.latitude}


class NeighborhoodTotal:
    def __init__(self, neighborhood_name, declaration_total):
        self.neighborhood_name = neighborhood_name
        self.declaration_total = declaration_total

    def asDictionary(self):
        return {"neighborhood_name": self.neighborhood_name,
                "declaration_total": self.declaration_total}


class Profile:
    def __init__(self, id, first_name, last_name,
                 email, salt, pwd_hash, neighborhoods):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.salt = salt
        self.pwd_hash = pwd_hash
        self.neighborhoods = neighborhoods

    def asDictionary(self):
        return {"id": self.id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email,
                "neighborhoods": self.neighborhoods}


class NewDeclaration:
    def __init__(self, declaration_num, first_name, last_name,
                 address, inspection_date, description,
                 neighborhood, district, declaration_date):
        self.declaration_num = declaration_num
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.inspection_date = inspection_date
        self.description = description
        self.neighborhood = neighborhood
        self.district = district
        self.declaration_date = declaration_date

    def asDictionary(self):
        return {"declaration_num": self.declaration_num,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "address": self.address,
                "inspection_date": self.inspection_date,
                "description": self.description,
                "neighborhood": self.neighborhood,
                "district": self.district,
                "declaration_date": self.declaration_date}
