# liste des quartier pour validation dans les deux schemas
neighborhoods = ["Anjou", "Beaurivage",
                 "Bois-Francs", "Cartierville",
                 "Cecil-P.-Newman", "Centre",
                 "Centre-Nord", "Chameran/Montpellier",
                 "Crémazie", "Préfontaine",
                 "Côte-Saint-Antoine", "Côte-Saint-Paul",
                 "Desmarchais-Crawford", "Dorval",
                 "Du College/Hodge", "Dupéré",
                 "Dutrisac", "Est",
                 "François-Perrault", "Gabriel-Sagard",
                 "Grande-Prairie", "Grenet",
                 "Guybourg", "Hochelaga",
                 "Ile-des-Soeurs", "L'Île-Bizard–Sainte-Geneviève",
                 "La Visitation", "Lachine-Ouest",
                 "Longue-Pointe", "Lorimier",
                 "Louis-Hébert", "Louis-Riel",
                 "Loyola", "Maisonneuve",
                 "Marc-Aurèle-Fortin", "Marie-Victorin",
                 "Mile End", "Nicolas-Viel",
                 "Milton-Parc", "Montagne",
                 "Nouveau-Bordeaux", "Ouest",
                 "Outremont", "Parc-Extension",
                 "Parc-Jarry", "Parc-Kent",
                 "Parc-Lafontaine", "Parc-Laurier",
                 "Petite-Bourgogne", "Petite-Côte",
                 "Pierrefonds-Est", "Pierrefonds-Ouest",
                 "Pointe-Saint-Charles", "Pointe-aux-Trembles",
                 "Port-Maurice", "Père-Marquette",
                 "René-Goupil", "René-Lévesque",
                 "Rivière-des-Prairies", "Saint-Henri",
                 "Saint-Louis", "Saint-Sulpice",
                 "Saint-Édouard", "Sainte-Lucie",
                 "Sainte-Marie", "Sault-Saint-Louis",
                 "Sault-au-Récollet", "Savane",
                 "Snowdon", "Tétreaultville",
                 "Upper Lachine", "Verdun-Centre",
                 "Vieux-Lachine - Saint-Pierre", "Vieux-Montréal",
                 "Vieux-Rosemont", "Ville-Émard",
                 "Édouard-Montpetit", "Étienne Desmarteaux"]

profile_insert_schema = {
    "type": "object",
    "required": ["first_name", "last_name", "email",
                 "password", "neighborhoods"],
    "properties": {
        "first_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50,
            "pattern": r"\S"
        },
        "last_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50,
            "pattern": r"\S"
        },
        "email": {
            "type": "string",
            "minLength": 5,
            "maxLength": 50,
            "pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        },
        "password": {
            "type": "string",
            # 8 caractères minimum, au moins une lettre majuscule,
            # minuscule et un chiffre
            "pattern": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$"
        },
        "neighborhoods": {
            "type": "array",
            "minItems": 0,
            "maxItems": 78,
            "uniqueItems": True,
            "items": {
                "type": "string",
                "enum": neighborhoods
            }
        }
    },
    "additionalProperties": False
}

declaration_insert_schema = {
    "type": "object",
    "required": ["first_name", "last_name", "address",
                 "inspection_date", "neighborhood",
                 "district"],
    "properties": {
        "first_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50,
            "pattern": r"\S"
        },
        "last_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50,
            "pattern": r"\S"
        },
        "address": {
            "type": "string",
            "minLength": 4,
            "maxLength": 100,
            "pattern": r"\S"
        },
        "inspection_date": {
            "type": "string",
            # ISO 8601
            "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
        },
        "description": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200,
            "pattern": r"\S"
        },
        "neighborhood": {
            "type": "string",
            "enum": neighborhoods
        },
        "district": {
            "type": "string",
            "enum": ["Mercier–Hochelaga-Maisonneuve",
                     "Côte-des-Neiges–Notre-Dame-de-Grâce",
                     "Rosemont–La Petite-Patrie", "Le Plateau-Mont-Royal",
                     "Villeray–Saint-Michel–Parc-Extension", "Montréal-Nord",
                     "LaSalle", "Le Sud-Ouest",
                     "Ville-Marie", "Saint-Léonard",
                     "Rivière-des-Prairies–Pointe-aux-Trembles",
                     "Ahuntsic-Cartierville",
                     "Lachine", "Anjou",
                     "Saint-Laurent", "Verdun",
                     "Outremont", "Pierrefonds-Roxboro",
                     "L'Île-Bizard–Sainte-Geneviève", "N/D"]
        }
    },
    "additionalProperties": False
}
