// Valide une date au format ISO 8601. Valide à partir de l'an 0 à l'an 9999
// même s'il n'y a pas de déclaration avant 2011.
function isValidDate(date)
{
    // retourne false si le format général n'est pas bon
    if(!/^\d{4}-\d{2}-\d{2}$/.test(date))
        return false;

    // conversion en int
    var parts = date.split("-");
    var day = parseInt(parts[2], 10);
    var month = parseInt(parts[1], 10);
    var year = parseInt(parts[0], 10);

    // retourne false si le mois n'est pas valide
    if(month == 0 || month > 12) {
        return false;
    }

    // nombre de jours dans chaque mois
    var monthLength = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ];

    // calcul d'année bisextile
    if(year % 400 == 0 || (year % 100 != 0 && year % 4 == 0)) {
        // si bisextile, février a 29 jours
        monthLength[1] = 29;
    }

    // si le jour est valide on retourne true, la date est valide
    if(day > 0 && day <= monthLength[month - 1]) {
        return true;
    }
    
    return false;
};

// POINT A5 et A6
// retourne true si la date de début est
// plus petite que la date de fin
function isValidDates(startDate, endDate) {

    // conversion en date de début
    var parts = startDate.split("-");
    var sdDay = parseInt(parts[2], 10);
    var sdMonth = parseInt(parts[1], 10) - 1; // mois de 0 à 11
    var sdYear = parseInt(parts[0], 10);
    startDate = new Date(sdYear, sdMonth, sdDay);

    // conversion en date de fin
    parts = endDate.split("-");
    var edDay = parseInt(parts[2], 10);
    var edMonth = parseInt(parts[1], 10); - 1; // mois de 0 à 11
    var edYear = parseInt(parts[0], 10);
    endDate = new Date(edYear, edMonth, edDay);

    return startDate <= endDate;
};

function addInvalidClass(elem) {
    if(!elem.classList.contains("is-invalid")) {
        elem.classList.add("is-invalid");
    }
};

function removeInvalidClass(elem) {
    if(elem.classList.contains("is-invalid")) {
        elem.classList.remove("is-invalid");
    }
};

function addHiddenClass(elem) {
    if(!elem.classList.contains("hidden")) {
        elem.classList.add("hidden");
    }
};

function removeHiddenClass(elem) {
    if(elem.classList.contains("hidden")) {
        elem.classList.remove("hidden");
    }
};

// POINTS A5 et A6
// exécutée lors de la méthode onclick du bouton
// de recherche rapide. Valide les dates et ensuite fait
// la requête ajax.
function doQuickSearch()
{
    var startDate = document.getElementById("startdate");
    var endDate = document.getElementById("enddate");

    // si erreur de l'utilisateur
    if(!datesValid(startDate, endDate)) {
        // on masque les résultats
        var qSearchDetail = document.getElementById("divqsearchdetail");
        var qsearch = document.getElementById("divqsearch");
        var resultNum = document.getElementById("resultnum");
        addHiddenClass(qSearchDetail);
        addHiddenClass(qsearch);
        addHiddenClass(resultNum);
        return;
    }

    var strStartDate = startDate.value.trim();
    var strEndDate = endDate.value.trim();

    sendDatesRequest(strStartDate, strEndDate)
};

// POINT A5 et A6
// valide les deux dates
function datesValid(startDate, endDate) {

    var startDateError = document.getElementById("startdateerror");
    var strStartDate = startDate.value.trim();
    var strEndDate = endDate.value.trim();

    removeInvalidClass(startDate)
    removeInvalidClass(endDate)

    // validation date de début
    if(strStartDate == "" || !isValidDate(strStartDate)) {
        startDateError.innerHTML = "Date invalide"
        addInvalidClass(startDate);
        return false;
    }

    // validation date de fin
    if(strEndDate == "" || !isValidDate(strEndDate)) {
        addInvalidClass(endDate);
        return false;
    }

    // vérification que la date de début est <= à la date de fin
    if(!isValidDates(strStartDate, strEndDate)) {
        startDateError.innerHTML = "La date de début doit être plus petite que la date de fin";
        addInvalidClass(startDate);
        return false;
    }

    return true;
}

// POINT A5 et A6
// fait la requête Ajax et génère le table de 
// résultats si code 200
function sendDatesRequest(startDate, endDate) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            var qSearch = document.getElementById("divqsearch");
            var qSearchDetail = document.getElementById("divqsearchdetail");
            var selectDetail = document.getElementById("selectdetail");
            var resultnum = document.getElementById("resultnum");
            if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);             
                // si il y a au moins une déclaration
                if(data.length > 0) {
                    // si aucun quartier sélectionné
                    if(selectDetail.selectedIndex == 0) {
                        // tableau des quartiers, arrondissements et nombre de déclarations
                        var neighborhoods = populateNeighborhoods(data);

                        // génération du table de résultats
                        populateQsearchTable(neighborhoods);

                        // nombre de résultats
                        var num = neighborhoods.length;
                        resultnum.innerHTML = num < 2 ? num + " résultat": num + " résultats"

                        // affichage du table
                        removeHiddenClass(qSearch);
                        removeHiddenClass(resultnum);

                        // masquage du table détaillé
                        addHiddenClass(qSearchDetail);
                    }
                    else {
                        // quartier sélectionné
                        var neighborhood = selectDetail.options[selectDetail.selectedIndex].text;

                        // tableau des déclaration pour le quartier sélectionné
                        var declarations = populateDeclarations(data, neighborhood);

                        // génération du table de résultats
                        populateQsearchDetailTable(declarations);

                        // nombre de résultats
                        var num = declarations.length;
                        resultnum.innerHTML = num < 2 ? num + " résultat": num + " résultats"

                        // affichage du table détaillé
                        removeHiddenClass(qSearchDetail);
                        removeHiddenClass(resultnum);

                        // masquage du table
                        addHiddenClass(qSearch);
                    }
                }
                else {
                    // masquage des deux tables si aucune donnée
                    addHiddenClass(qSearch);
                    addHiddenClass(qSearchDetail);
                }                            
            } else {
                // masquage des deux tables si code 400 ou 500 
                addHiddenClass(qSearch);
                addHiddenClass(qSearchDetail);
            }
        }
    };

    xhr.open("GET", "/api/declarations?du="+startDate+"&au="+endDate, true);
    xhr.send();
};

// POINT A5
// retourne la liste d'arrondissements, quartier et
// nombre de déclarations
function populateNeighborhoods(data) {
    var neighborhoods = [];

    for(var i = 0; i < data.length; i++) {
        var declaration = data[i];
        var found = false;
        for(var j = 0; j < neighborhoods.length && !found; j++) {
            // si le quartier est déja présent on incrémente
            // le nombre de déclarations de 1
            if(neighborhoods[j][1] == declaration.neighborhood_name &&
               neighborhoods[j][0] == declaration.district_name) {
                neighborhoods[j][2] += 1;
                found = true;
            }
        }

        // Ajout d'un nouveau quartier
        if(!found) {
            var neighborhood = [declaration.district_name, declaration.neighborhood_name, 1];
            neighborhoods.push(neighborhood);
        }
    }

    // tri en ordre décroissant de nombre de déclarations
    return neighborhoods.sort(function(a, b) {
        return b[2] - a[2];
    });
};

// POINT A6
// retourne la liste de déclarations pour un quartier donné
function populateDeclarations(data, neighborhood) {
    var declarations = [];

    for(var i = 0; i < data.length; i++) {
        // déclaration
        var d = data[i];

        // si le nom de quartier correspond
        if(d.neighborhood_name == neighborhood) {

            // strings "N/D" à la place des champs possiblement null
            var iDate = d.inspection_date == null ? "N/D": d.inspection_date;
            var eNum = d.extermination_num == null ? "N/D": d.extermination_num;
            var tsDate = d.treatment_start_date == null ? "N/D": d.treatment_start_date;
            var teDate = d.treatment_end_date == null ? "N/D": d.treatment_end_date;
            var xCoord = d.x_coord == null ? "N/D": d.x_coord;
            var yCoord = d.y_coord == null ? "N/D": d.y_coord;
            var longitude = d.longitude == null ? "N/D": d.longitude;
            var latitude = d.latitude == null ? "N/D": d.latitude;

            var temp = [d.declaration_num,
                        d.declaration_date,
                        iDate,
                        eNum,
                        tsDate,
                        teDate,
                        xCoord,
                        yCoord,
                        longitude,
                        latitude];
            
            // ajout à la liste            
            declarations.push(temp)
        }        
    }

    // tri en ordre croissant de numéro de déclaration
    return declarations.sort(function(a, b) {
        return a[0] - b[0];
    });
};

// POINT A5
// génère le tableBody avec les résultats
function populateQsearchTable(neighborhoods) {
    var tbody = document.getElementById("tbodyqsearch");

    // on vide le tableBody
    tbody.innerHTML = "";

    for(var i = 0; i < neighborhoods.length; i++) {
        // ajout ligne
        var tr = tbody.insertRow();
        for(var j = 0; j < 3; j++) {
            // ajout cellule
            var td = tr.insertCell();
            td.innerHTML = neighborhoods[i][j];

            // id pour retrouver le nom de quartier plus tard
            if(j == 1) {
                td.id = "neighborhood_"+i;
            }
        }

        // création du bouton suppression (point D3)
        var btn = document.createElement("button");
        btn.innerHTML = "supprimer";
        btn.className = "btn btn-dark"
        btn.id = i;
        btn.addEventListener("click", function() { deleteDeclarations(this);}, false);
        
        // ajout du bouton à la cellule
        var td = tr.insertCell();
        td.appendChild(btn);
    }
};

// POINT A6
// génère le table Body détaillé avec les déclarations
function populateQsearchDetailTable(declarations) {
    var tbody = document.getElementById("tbodyqsearchdetail");

    // on vide le tableBody
    tbody.innerHTML = "";

    for(var i = 0; i < declarations.length; i++) {
        // ajout ligne
        var tr = tbody.insertRow();

        // ajout de la cellule de numéro de déclaration
        var h = tr.insertCell();
        h.outerHTML = "<th scope=\"row\">" + declarations[i][0] +"</th>";

        for(var j = 1; j < 10; j++) {
            // ajout cellule
            var td = tr.insertCell();
            td.innerHTML = declarations[i][j];
        }
    }
};

// POINT D1
// vérifie que la date de visite n'est pas plus vielle de 1 an ou
// pas plus de un an dans le futur
function isDateInRange(visitDate) {
    // date limite l'an passé
    var lastYear = new Date();
    lastYear.setFullYear(lastYear.getFullYear() - 1);
    lastYear.setHours(0, 0, 0, 0);

    // date limite l'an prochain
    var nextYear = new Date();
    nextYear.setFullYear(nextYear.getFullYear() + 1);
    nextYear.setHours(0, 0, 0, 0);

    // conversion en date
    var parts = visitDate.split("-");
    var day = parseInt(parts[2], 10);
    var month = parseInt(parts[1], 10) - 1; // mois de 0 à 11
    var year = parseInt(parts[0], 10);
    visitDate = new Date(year, month, day);

    // pas plus de 1 an d'écart, avant ou après
    if(visitDate < lastYear || visitDate > nextYear) {
        return false;
    }

    return true;
};

// POINT D1
// valide le formulaire de déclaration
// et fait le POST à l'API
function addDeclaration() {
    var firstName = document.getElementById("firstname");
    var lastName = document.getElementById("lastname");
    var address = document.getElementById("address");
    var visitDate = document.getElementById("visitdate");
    var description = document.getElementById("description");
    var neighborhood = document.getElementById("selectneighborhood");
    var district = document.getElementById("selectdistrict");

    removeInvalidClass(firstName)
    removeInvalidClass(lastName)
    removeInvalidClass(address)
    removeInvalidClass(visitDate)
    removeInvalidClass(description)
    removeInvalidClass(neighborhood)
    removeInvalidClass(district)

    // validation

    var strFirstName = firstName.value.trim();
    if(strFirstName == "" || strFirstName.length > 50) {
        addInvalidClass(firstName);
        return;
    }

    var strLastName = lastName.value.trim();
    if(strLastName == "" || strLastName.length > 50) {
        addInvalidClass(lastName);
        return;
    }

    var strAddress = address.value.trim();
    if(strAddress == "" || strAddress.length > 100) {
        addInvalidClass(address);
        return;
    }

    var strVisitDate = visitDate.value.trim();
    if(strVisitDate == "" || !isValidDate(strVisitDate) || !isDateInRange(strVisitDate)) {
        addInvalidClass(visitDate);
        return;
    }

    strDescription = description.value.trim();
    if(strDescription.length > 200) {
        addInvalidClass(description);
        return;
    }

    if(neighborhood.selectedIndex == 0) {
        addInvalidClass(neighborhood);
        return; 
    }

    if(district.selectedIndex == 0) {
        addInvalidClass(district);
        return; 
    }

    var strNeighborhood = neighborhood.options[neighborhood.selectedIndex].text
    var strDistrict = district.options[district.selectedIndex].text

    var jsonDecl;

    // on adapte l'objet json à envoyer
    // dépendant si on a une description ou non
    if(strDescription == "") {
        jsonDecl = {
            first_name: strFirstName,
            last_name: strLastName,
            address: strAddress,
            inspection_date: strVisitDate,
            neighborhood: strNeighborhood,
            district: strDistrict
        }
    }
    else {
        jsonDecl = {
            first_name: strFirstName,
            last_name: strLastName,
            address: strAddress,
            inspection_date: strVisitDate,
            description: strDescription,
            neighborhood: strNeighborhood,
            district: strDistrict
        }
    }
    console.log(JSON.stringify(jsonDecl));
    postData('/api/declaration', jsonDecl)
        .then(data => {
            var divSuccess = document.getElementById("alertsuccess");
            var divFail = document.getElementById("alertfail");
            if(data.hasOwnProperty("declaration_num")) {
                // on affiche le succès
                removeHiddenClass(divSuccess);
                addHiddenClass(divFail);

                // réinitialisation des champs
                firstName.value = "";
                lastName.value = "";
                address.value = "";
                visitDate.value = "";
                description.value = "";
                neighborhood.selectedIndex = 0;
                district.selectedIndex = 0;


            }
            else {
                // afficher une erreur
                removeHiddenClass(divFail);
                addHiddenClass(divSuccess);
            }
        });

};

async function postData(url = '', data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    return response.json();
}

// change le selected index du select d'arrondissement 
// lorsqu'on change de quartier (point D1)
function changeDistrict() {
    var ddlN = document.getElementById("selectneighborhood");
    var ddlD = document.getElementById("selectdistrict");
    var districtId = ddlN.options[ddlN.selectedIndex].getAttribute('district');
    ddlD.selectedIndex = districtId;
};

// POINT D3
// Supprime les déclarations affichées grâce au point A5
function deleteDeclarations(btn) {
    var startDate = document.getElementById("startdate");
    var endDate = document.getElementById("enddate");

    // td contenant le nom de quartier correspondant
    var td = document.getElementById("neighborhood_"+btn.id);
    var neighborhood = td.innerHTML;

    // on revalide les dates en cas de modification
    if(!datesValid(startDate, endDate)) {
        return;
    }

    var strStartDate = startDate.value.trim();
    var strEndDate = endDate.value.trim();

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            var divSuccess = document.getElementById("alertsuccess");
            var divFail = document.getElementById("alertfail");
            if (xhr.status === 200) {
                // on affiche le succès
                removeHiddenClass(divSuccess);
                addHiddenClass(divFail);

                // on relance l'autre service pour effacer 
                // le résultat qu'on vient de supprimer
                doQuickSearch();
            }
            else {
                // on affiche une erreur
                removeHiddenClass(divFail);
                addHiddenClass(divSuccess);
            }
        }
    };

    var url = "/api/declarations/delete?du="+strStartDate+"&au="+strEndDate+"&quartier="+neighborhood;
    xhr.open("DELETE", url, true);
    xhr.send();
    
};