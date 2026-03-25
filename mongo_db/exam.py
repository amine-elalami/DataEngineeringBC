from pymongo import MongoClient
from pprint import pprint

def write_result_to_file(result, filename):
    with open(filename, "w") as f:
        for item in result:
            f.write("%s\n" % item)

result = []

"""
Partie 1 : Connexion à la base de données
"""

client = MongoClient(
    host="127.0.0.1",
    port = 27017,
    username= "datascientest",
    password= "dst123"
)

# b) Afficher les bases de données disponibles
liste_bases = client.list_database_names()
print("b) Les bases de données disponibles sont :", liste_bases)
result.append("b) Les bases de données disponibles sont : {}".format(liste_bases))

# c) Afficher les collections disponibles dans la base de données "sample"
sample = client['sample']
liste_collections = sample.list_collection_names()
print("c) Les collections disponibles dans la base de données 'sample' sont :", liste_collections)
result.append("c) Les collections disponibles dans la base de données 'sample' sont : {}".format(liste_collections))

# d) Afficher un document de la collection "books"
books = sample['books']
document_books = books.find_one()
pprint("d) Le document de la collection 'books' est :", document_books)
result.append("d) Le document de la collection 'books' est : {}".format(document_books))

# e) Afficher le nombre de documents dans la collection "books"
print("e) Le nombre de documents dans la collection 'books' est :", books.count_documents({}))
result.append("e) Le nombre de documents dans la collection 'books' est : {}".format(books.count_documents({})))


print("\n" + "="*50 + "\n")
"""
Partie 2 : Exploration de la base
"""
print("Partie 2 : Exploration de la base")
# a) Afficher le nombre de livres avec plus de 400 pages.
# Afficher ensuite le nombre de livres ayant plus de 400 pages ET qui sont publiés.
livres_400_pages = books.count_documents({
    "pageCount": {"$gt": 400}
})
print("a-1) Le nombre de livres avec plus de 400 pages est :", livres_400_pages)
result.append("a-1) Le nombre de livres avec plus de 400 pages est : {}".format(livres_400_pages))

livres_400_pages_publies = books.count_documents({
    "$and": [
        {"pageCount": {"$gt": 400}},
        {"status": "PUBLISH"}
    ]
})
print("a-2) Le nombre de livres avec plus de 400 pages et qui sont publiés est :", livres_400_pages_publies)
result.append("a-2) Le nombre de livres avec plus de 400 pages et qui sont publiés est : {}".format(livres_400_pages_publies))

# b) Afficher le nombre de livres ayant le mot-clé Android dans leur description (brève ou longue).
livres_avec_android = books.count_documents({
    "$or": [
        {"shortDescription": {"$regex": "Android"}},
        {"longDescription": {"$regex": "Android"}}
    ]
})
print("b) Le nombre de livres avec 'Android' dans la description est :", livres_avec_android)
result.append("b) Le nombre de livres avec 'Android' dans la description est : {}".format(livres_avec_android))

# c) Chaque document possède un attribut categories qui est une liste.
# Vous devez grouper tous les documents en un à l'aide de l'opérateur $group.
# Puis, à l'aide de l'opérateur $addToSet, créez 2 sets à partir des catégories.

categories = books.aggregate([
    {"$group": {
        "_id": None,
        "categories_0": {"$addToSet": {"$arrayElemAt": ["$categories", 0]}},
        "categories_1": {"$addToSet": {"$arrayElemAt": ["$categories", 1]}}
    }}
]).to_list(length=5)

print("c) Les catégories d'index 0 sont :", len(categories[0]['categories_0']))
print("c) Les catégories d'index 1 sont :", len(categories[0]['categories_1']))

result.append("c) Les catégories d'index 0 sont : {}".format(len(categories[0]['categories_0'])))
result.append("c) Les catégories d'index 1 sont : {}".format(len(categories[0]['categories_1'])))

# d) Afficher le nombre de livres qui contiennent des noms de langages suivants dans leur description longue :
# Python, Java, C++, Scala.
nombre_livres_programmations = books.count_documents({
    "$or": [
        {"longDescription": {"$regex": "Python"}},
        {"longDescription": {"$regex": "Java"}},
        {"longDescription": {"$regex": "C++"}},
        {"longDescription": {"$regex": "Scala"}}
    ]
})
print(
    "d) Le nombre de livres qui contiennent les langages",
    "Python, Java, C++ ou Scala dans leur description longue est :",
    nombre_livres_programmation)
results.append(
    "d) Le nombre de livres qui contiennent les langages"+
    "Python, Java, C++ ou Scala dans leur description longue est : {}".format(
    nombre_livres_programmation))

# e) Afficher diverses informations statistiques sur notre base de données :
# nombre maximal, minimal, et moyen de pages par catégorie. 

statistics = books.aggregate([
    {"$unwind": {"path": "$categories"}},
    {"$group": {
        "_id": "$categories",
        "maxCountPage": {"$max": "$pageCount"},
        "minCountPage": {"$min": "$pageCount"},
        "avgCountPage": {"$avg": "$pageCount"},
        "count": {"$sum": 1}
    }},
    {"$match": {"maxCountPage": {"$gt": 0}, "_id": {"$ne": ""}}},
    {"$sort": {"avgCountPage": -1}}
]).to_list()
pprint("e) Informations statistiques par catégorie :")
pprint(statistics)

# f) Via une pipeline d'agrégation, créer de nouvelles variables en extrayant 
# des informations depuis l'attribut dates : année, mois, jour.
# On rajoutera une condition pour filtrer seulement les livres publiés après 2009.
# N'affichez que les 20 premiers.

edited_books = books.aggregate([
    {"$project": {
        "title": 1,
        "year": {"$year": "$publishedDate"},
        "month": {"$month": "$publishedDate"},
        "day": {"$dayOfMonth": "$publishedDate"}
    }},
    {"$match": {"year": {"$gt": 2009}}},
    {"$limit": 20}
]).to_list()

print("f) Les livres publiés après 2009 sont :")
pprint(edited_books)

# g) À partir de la liste des auteurs, créez de nouveaux attributs (author_1, author_2 ... author_n).
# Observez le comportement de "$arrayElemAt". N'affichez que les 20 premiers dans l'ordre chronologique.

decomposition_auteurs_et_filtres = books.aggregate([
    {"$project": {
        "title": 1,
        "author_1": {"$arrayElemAt": ["$authors", 0]},
        "author_2": {"$arrayElemAt": ["$authors", 1]},
        "author_3": {"$arrayElemAt": ["$authors", 2]},
        "author_4": {"$arrayElemAt": ["$authors", 3]},
        "author_5": {"$arrayElemAt": ["$authors", 4]},
        "year": {"$year": "$publishedDate"},
    }},
    {"$sort": {"year": -1}},
    {"$limit": 20}
]).to_list()

print("g) Les livres publiés après 2009 sont :")
pprint(decomposition_auteurs_et_filtres)
# Comportement de "$arrayElemAt" : 
#   si l'index demandé est supérieur à la taille de la liste, alors la clé n'est pas ajoutée au document.


# h) Afficher le nombre de publications pour les 10 premiers auteurs les plus prolifiques.
auteurs_prolifiques = books.aggregate([
    {"$project": {
        "title": 1,
        "first_author": {"$arrayElemAt": ["$authors", 0]}
    }},
    {"$group": {
        "_id": "$first_author",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}},
    {"$limit": 10}
]).to_list()

print("h) Les 10 auteurs les plus prolifiques sont :")
pprint(auteurs_prolifiques)

# i) [OPTIONNEL] Afficher la distribution du nombre d'auteurs 
distribution_auteurs = books.aggregate([
    {"$project": {"authors_count": {"$size": "$authors"}}},
    {"$group": {
        "_id": "$authors_count",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}}
]).to_list()

print("i) La distribution du nombre d'auteurs par livre est :")
pprint(distribution_auteurs)

# j) [OPTIONNEL] Afficher l'occurrence de chaque auteur selon son index dans l'attribut "authors"
occurences_auteurs = books.aggregate([
    {"$unwind": {
        "path": "$authors",
        "includeArrayIndex": "author_index",
        "preserveNullAndEmptyArrays": False}},
    {"$match": {"author": {"$ne": ""}}},
    {"$project": {
      "author": "$authors",
      "author_index": "$author_index"
    }},
    {"$group": {
        "_id": ["$author", "$author_index"],
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}},
    {"$limit": 20}
]).to_list()

print("j) La distribution du nombre d'auteurs par livre est :")
pprint(occurences_auteurs)
