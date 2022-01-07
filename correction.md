## Fichier de correction

**Note:** Tous les services REST peuvent être testés avec un client REST tel que [YARC!](https://yet-another-rest-client.com/). Tous les services REST offerts par l'application sont aussi documentés sur la route `/doc`.

### Point A1
Une base de donnée vide nommée `db.db` dans le répertoire `/db` permet de tester le script d'insertion `db/script.py` qui peut être lancé avec la commande `python3 script.py`. Ce script a son propre fichier de reqûetes SQLite 3 dans `db/database.py`.

Le script de création de base de donnée nommé `db.sql` est aussi dans le répertoire `/db`. Pour créer un base de donnée vide on doit entrer la commande `sqlite3 db.db` et ensuite `.read db.sql`. La base de donnée doit obligatoirement être nommé `db.db` et rester dans le répertoire `/db` sinon l'application ne fonctionnera pas.

### Point A2
L'onglet "Recherche" au haut de la page d'accueil permet la recherche par arrondissement ou quartier. La recherche est faite par sous-chaîne donc si on entre "osemo" on aura tous les résultats de recherche pour "Rosemont". La longeur mininum pour une recherche est 3 caractères et le maximum est 100 caractères. Les résultats sont affichés sur la route `/results`qui contient un paramètre d'url nommé `search` pour le texte recherché. La page de résultats affiche le nombre de résultats et les déclaration sont affichées en ordre de numéro de déclaration.

### Point A3
Pour tester le BackgroundScheduler, il faut changer au bas du fichier `app.py` dans l'appel de `scheduler.add_job()` le paramètre `hour=0` (minuit) pour `minute=XX` où XX est une minute de l'heure courante où la fonction `jobs_seq` sera appelée.

Les fonctions `import_csv`, `csv_to_dn` et `csv_to_decl` sont très semblables au fonctions du script du point A1. Il n'y a cependant pas d'arrêt du script possible contrairement au point A1 à moins qu'il y ait une erreur avec le téléchargement du fichier CSV. De plus, les quartier et arrondissements sont mis-à-jour au lieu d'être insérés en totalité dans `csv_to_dn`. Finalement, la mise-à-jour des déclarations dans `csv_to_decl` contient l'appel pour l'envoie possible du courriel (point B1) et du ou des tweet(s) (point B2).

Un test simple consiste à supprimer manuellement une déclaration de la base de donnée (e.g. `delete from declarations where declaration_num = ?` où `?` est un numéro de déclaration). On active ensuite le BackgroundScheduler et on vérifie ensuite si la déclaration est présente dans la base de données (e.g. `select * from declarations where declaration_num = ?`où `?`est le même numéro de déclaration). L'outil de recherche du point A2 peut aussi servir à cette fin si on connait l'arrondissement ou le quartier de la déclaration.

### Point A4
Ce service REST est offert sur la route `/api/declarations`. Il retourne une erreur 400 si il manque un paramètre d'url (paramètre de date `du` et `au`), si l'une des deux dates n'est pas valide et si la date `au` est avant la date `du`. Un test facile à exécuter est par exemple de taper dans la barre d'adresse l'url `/api/declarations?du=2011-01-01&au=2012-01-01` et toutes les déclaration entre 2011 et 2012 seront affichées au format JSON. Une autre façon de tester le service est d'utiliser l'outil de recherche du point A5 ou A6.

### Point A5
L'onglet "Recherche rapide" de la page principale offre cette recherche rapide. La totalité de sa logique est dans le fichier `static/js/scripts.js` (fonctions `doQuickSearch`, `sendDatesRequest`, `populateNieghborhoods` et `populateQsearchTable`). Les résultats de recherche ne seront affichés que si les deux date sont entrées et valides et que la date de fin est plus grande ou égale à la date de début, sinon une erreur sera affichée. Aussitôt qu'il y a une nouvelle erreur de l'utilisateur et qu'il clique sur le bouton "Recherche rapide" les résultats de recherches antérieurs sont masqué jusqu'à ce qu'il n'y ait plus aucune erreur de date. Les résultats de recherche sont classés en ordre décroissants de nombre de déclarations.

### Point A6
L'onglet "Recherche rapide" de la page principale offre cette recherche rapide. La totalité de sa logique est dans le fichier `static/js/scripts.js` (fonctions `doQuickSearch`, `sendDatesRequest`, `populateDeclarations` et `populateQsearchDetailTable`). Le détail des déclarations pour un quartier est affiché si on choisi un quartier dans la liste déroulante. Si on choisi l'option "Choisissez un quartier" c'est les résultat du point A5 qui sont affichés. Le tableau de résultats en A6 est semblable à celui de A2 mis-à-part qu'il n'y a pas les champs numéro de quartier, nom de quartier et arrondissement puisque la recherche se fait par quartier.

### Point B1
Pour tester l'envoie de courriel, on doit supprimer une ou plusieurs déclaration(s) de la même façon que pour tester le point A3 et lancer le BackgroundScheduler. Le code de ce point est dans le fichier `app.py` et les fonctions concernées sont `send_email`, `get_html` et `get_dest_address`. Pour changer le destinataire du courriel il ne suffit que de changer l'adresse courriel dans le fichier `mail.yaml` à la racine du projet. Le courriel est sous forme de tableau HTML avec le détail des nouvelles déclarations ajoutées.

### Point B2
Pour tester l'envoie de tweet, on doit supprimer une ou plusieurs déclaration(s) de la même façon que pour tester le point A3 et lancer le BackgroundScheduler. Le code de ce point est dans le fichier `app.py` et les fonctions concernées sont `send_tweets`, `get_tweet_contents` et `populate_neighborhoods`. Lorqu'il y a de nouvelles déclarations, un ou plusieurs tweets sont faits sur le compte twitter [@6502Bed](https://twitter.com/6502Bed).  Il y aura un seul tweet si la totalité du texte fait moins de 280 caractères sinon il y aura plusieurs tweets étiquettés comme par exemple 1/3, 2/3 et 3/3.

### Point C1
Ce service REST est offert sur la route `/api/neighborhoods`. Pou tester il suffit de taper la route dans la barre d'adresse et les données vont s'afficher en format JSON.

### Point C2
Ce service REST est offert sur la route `/api/neighborhoods/xml`. Pou tester il suffit de taper la route dans la barre d'adresse et les données vont s'afficher en format XML avec encodage UTF-8.

### Point C3
Ce service REST est offert sur la route `/api/neighborhoods/csv`. Pou tester il suffit de taper la route dans la barre d'adresse et les données vont s'afficher en format CSV avec encodage UTF-8.

### Point D1
Ce service REST est offert sur la route `/api/declaration`. Pour tester, on peut utiliser un client REST ou bien utiliser le formulaire du point D3.

Le schema `declaration_insert_schema` dans `schemas.py` fait la majorité de la validation. J'ai décidé de mettre le champ `description` comme seul champ optionel mais il est retourné à null lors de la confirmation (code 201) advenant qu'il n'est pas fourni à la soumission. J'ai aussi décidé de permettre une date d'inspection jusqu'à un an avant et après la date du jour. Les validations en dehors du schema sont la validation de la date (sauf format) et valider que le quartier soumis est dans le bon arrondissement.

Pour ce qui est de l'insertion dans la base de données, il y a insertion dans la table `declarations` des champs `declaration_date`, `inspection_date`et `neighborhood_id`. Les nouveau attributs sont placés dans une nouvelle table `declarations_extra` qui a comme primary key le `declaration_num` correspondant. Par choix ces nouveaux champs ne sont pas affichés dans les tableaux des points A2 et A6.

Le formulaire est accessible sur la route `/new-declaration`. La logique du formulaire est dans le fichier `static/js/scripts.js`. Il y a les même validations côté client qu'avec le service REST (voir la fonction `addDeclaration`). La liste déroulante pour l'arrondissement est seulement accessoire et sert à la fois d'information supplémentaire et de source pour envoyer le bon nom d'arrondissement au service REST. Il y a un message d'erreur ou de succès qui apparaît lorsqu'on clique sur le bouton "Ajouter".

### Point D2
Ce service REST est offert sur la route `/api/declaration/{declaration_num}` où `declaration_num` est le numéro de déclaration. Pour tester, il faut utiliser un client REST. Ce que fait le service est de mettre le champ `is_visible` à false dans la table `declarations` ce qui masquera la déclaration pour les requêtes SQLite des points A2, A4, A5, A6, C1, C2 et C3. De plus, cela gardera la déclaration présente pour le point A3 et elle ne sera pas importée de nouveau lors d'une mise-à-jour de la base de données.

### Point D3
Pour ce point j'ai fais un nouveau service REST disponible sur la route `/api/declarations/delete`. Il prend trois paramètre d'url soit la date de début (paramètre `du`), la date de fin (paramètre `au`) et le nom quartier (paramètre `neighborhood`). Il y a validation côté serveur qu'il ne manque pas de paramètre, que les deux dates sont valides et que la date de fin est plus grande ou égale à la date de début. Si il y a une erreur de validation, une description de l'erreur en JSON est retourné avec code 400.

Le reste de la logique de modification du tableau de résultats est dans le fichier `static/js/scripts.js` (voir fonctions `deleteDeclarations` pour l'appel du service et `populateQsearchTable` pour l'ajout des boutons "Supprimer"). Après avoir reçu un code 200 pour la suppression, la fonction de recherche rapide est relancée pour faire disparaître du tableau l'entrée supprimée. Une message de confirmation ou d'erreur s'affiche aussi dans le haut de la page.

### Point E1
Ce service REST est offert sur la route `/api/profile`. Il peut seulement être testé avec un cleint REST puisque le point E2 n'a pas été développé. Le schema `profile_insert_schema` dans `schemas.py` fait la majorité de la validation. Pour la validation du email il ne s'agit que d'un pré-validation puisqu'il aurait fallu envoyer un email de confirmation pour s'assurer que ce soit la bonne addresse, ce qui n'a pas été fait. Pour le mot de passe il faut un minimum de 8 caractères avec au moin une lettre majuscule, une lettre minuscule et un chiffre. La seul validation faite à part du schema est de s'assurer que le email envoyé n'existe pas déja dans la table `profiles`.

La table `profiles` contient un salt de 32 caractère et un hashé de 128 caractères pour le mot de passe. Une table intermédiaire nommée `profiles_neighborhoods` a été crée pour les quartiers à surveiller. Une clé primaire dans cette table est la combinaison du `profile_id` et du `neighborhood_id`.

