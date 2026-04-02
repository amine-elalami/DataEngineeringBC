import numpy as np
from urllib.request import urlretrieve
from pyspark.sql import SparkSession
from pyspark.sql.functions import isnan, isnull, regexp_replace, lower, length, to_date, mean, when, col
from pyspark.sql.types import BooleanType

def getMissingValues(dataframe):
  count = dataframe.count()
  columns = dataframe.columns
  nan_count = []
  # we can't check for nan in a boolean type column
  for column in columns:
    if dataframe.schema[column].dataType == BooleanType():
      nan_count.append(0)
    else:
      nan_count.append(dataframe.where(isnan(col(column))).count())
  null_count = [dataframe.where(isnull(col(column))).count() for column in columns]
  return([count, columns, nan_count, null_count])

def missingTable(stats):
  count, columns, nan_count, null_count = stats
  count = str(count)
  nan_count = [str(element) for element in nan_count]
  null_count = [str(element) for element in null_count]
  max_init = np.max([len(str(count)), 10])
  line1 = "+" + max_init*"-" + "+"
  line2 = "|" + (max_init-len(count))*" " + count + "|"
  line3 = "|" + (max_init-9)*" " + "nan count|"
  line4 = "|" + (max_init-10)*" " + "null count|"
  for i in range(len(columns)):
    max_column = np.max([len(columns[i]),\
                        len(nan_count[i]),\
                        len(null_count[i])])
    line1 += max_column*"-" + "+"
    line2 += (max_column - len(columns[i]))*" " + columns[i] + "|"
    line3 += (max_column - len(nan_count[i]))*" " + nan_count[i] + "|"
    line4 += (max_column - len(null_count[i]))*" " + null_count[i] + "|"
  lines = f"{line1}\n{line2}\n{line1}\n{line3}\n{line4}\n{line1}"
  print(lines)

def download_file(url, filename):
    return urlretrieve(url, filename)

def normalize_columns_name(df):
    for col in df.columns:
        df = df.withColumnRenamed(col, col.replace(" ", "_").lower())
    return df

def replace_string_nan_values(df, column, value, values_to_replace=["NaN"]):
    conditions = (col(column) == "NaN")
    conditiond = isnan(column)
    if len(values_to_replace) > 1:
        for val in values_to_replace[1:]:
            conditions = conditions | (col(column) == val)
    df = df.withColumn(
        column,
        when(
            conditions,
            value
        ).otherwise(col(column))
    )
    return df


# Q1 - Télécharger les fichers csv
global_url = "https://assets-datascientest.s3.eu-west-1.amazonaws.com"

gps_app_file, _ = download_file(global_url + "/gps_app.csv", "gps_app.csv")
gps_user_file, _ = download_file(global_url + "/gps_user.csv", "gps_user.csv")
print("Files downloaded !")

# Charger les données dans des DataFrames Spark
spark = SparkSession\
    .builder\
    .appName("Google Play Store Analysis")\
    .master("local[*]")\
    .getOrCreate()

raw_app = spark.read.option("header", True)\
                    .option("inferSchema", True)\
                    .option("escape", "\"")\
                    .csv("gps_app.csv")

raw_user = spark.read.option("header", True)\
                    .option("inferSchema", True)\
                    .option("escape", "\"")\
                    .csv("gps_user.csv")


# Q2 - Normaliser les noms de colonnes
raw_app = normalize_columns_name(raw_app)
raw_user = normalize_columns_name(raw_user)

print("Columns of gps_app.csv:", raw_app.columns)
print("Columns of gps_user.csv:", raw_user.columns)


# Q3-1 C'est plus judicieux de remplacer les valeurs de rating par la moyenne de la colonne,
# car cela permet de conserver une certaine cohérence dans les données.
# En remplaçant les valeurs manquantes par la moyenne,
# on évite d'introduire des biais potentiels qui pourraient survenir si on utilisait la médiane.
avg_rating = raw_app.filter(~isnan("rating")).select(mean("rating")).head()["avg(rating)"]
raw_app = raw_app.fillna({"rating": avg_rating})


# Q3-2 La colonne 'type' est catégorique, pour remplacer une valeur manquante
# on peut utiliser la valeur la plus fréquente (mode).
type_mode_value = raw_app.filter(~isnan("type")).agg({'type': 'mode'}).head()['mode(type)']
raw_app = raw_app.fillna({"type": type_mode_value})


# Q3-3 Afficher les valeurs uniques prises par la colonne type. Que remarquez-vous ? Supprimer le problème. 
# Cela réglera aussi la valeur manquante de la colonne content_rating.
print("Les valeurs uniques de la colonne 'type'")
raw_app.select("type").distinct().show()
# On remarque que la valeur 'NaN' est toujours présente, et une valeur '0' aussi est là.

raw_app = replace_string_nan_values(raw_app, 'type', type_mode_value, ["NaN", "0"])
raw_app.filter(isnan("type")).show()

# On applique le même processus à la colonne 'content_rating'
content_rating_mode_value = raw_app.filter(~isnan("content_rating")).agg({'content_rating': 'mode'}).head()['mode(content_rating)']
raw_app = raw_app.fillna({"content_rating": content_rating_mode_value})
raw_app = replace_string_nan_values(raw_app, 'content_rating', content_rating_mode_value)


# Q.3.4 Remplacer le reste des valeurs manquantes pour la colonne current_ver et la colonne android_ver par leur modalité respective.
current_ver_mode_value = raw_app.filter(~isnan("current_ver")).agg({'current_ver': 'mode'}).head()['mode(current_ver)']
print(current_ver_mode_value)
raw_app = raw_app.fillna({"current_ver": current_ver_mode_value})
raw_app = replace_string_nan_values(raw_app, 'current_ver', current_ver_mode_value)

android_ver_mode_value = raw_app.filter(~isnan("android_ver")).agg({'android_ver': 'mode'}).head()['mode(android_ver)']
raw_app = raw_app.fillna({"android_ver": android_ver_mode_value})
raw_app = replace_string_nan_values(raw_app, 'android_ver', android_ver_mode_value)

missingTable(getMissingValues(raw_app))


# Q4.1 Étudier les valeurs manquantes présentes dans ce jeu de données.
# Les valeurs manquantes (nan) de chaque colonne sont toutes sur les mêmes lignes
# On supprime les lignes qui contiennent des valeurs manquantes dans toutes les colonnes
raw_user = raw_user.dropna(subset=["translated_review", "sentiment", "sentiment_polarity", "sentiment_subjectivity"])
missingTable(getMissingValues(raw_user))

# Q4.2 Supprimer les lignes qui contiennent des valeurs manquantes dans toutes les colonnes.
# Afficher les statistiques des valeurs manquantes après suppression.
filter_cond = ~isnan("app")
for c in raw_user.columns:
    filter_cond = filter_cond & ~isnan(c)
raw_user = raw_user.filter(filter_cond)
missingTable(getMissingValues(raw_user))



# Q5.1 Vérifier s'il reste des valeurs non numériques dans les colonnes sentiment_polarity et sentiment_subjectivity.
# Pour ce faire, on pourra filtrer les lignes pour lesquelles la transformation de la colonne en double renvoie une valeur manquante.
raw_user = raw_user.withColumn("sentiment_polarity", col("sentiment_polarity").cast("double"))
raw_user = raw_user.withColumn("sentiment_subjectivity", col("sentiment_subjectivity").cast("double"))
raw_user.filter(isnull(col("sentiment_subjectivity")) | isnull(col("sentiment_polarity"))).show(5)
raw_user.filter(isnan(col("sentiment_subjectivity")) | isnan(col("sentiment_polarity"))).show(5)


# Q5.2 Convertir les colonnes numériques au format float.
raw_user = raw_user.withColumn("sentiment_polarity", col("sentiment_polarity").cast("float"))
raw_user = raw_user.withColumn("sentiment_subjectivity", col("sentiment_subjectivity").cast("float"))


# Q.5.3 Remplacer les caractères spéciaux de la colonne translated_review par des espaces.
# Remplacer ensuite tous les espaces de taille supérieure à 2 par un espace de taille 1.
# Pour répondre à cette question, on pourra utiliser la fonction regexp_replace de la collection pyspark.sql.functions.
raw_user = raw_user.withColumn("translated_review", regexp_replace(col("translated_review"), "[^a-zA-Z0-9]", " "))
raw_user = raw_user.withColumn("translated_review", regexp_replace(col("translated_review"), " {2,}", " "))
raw_user.select("translated_review").show(10, truncate=False)


# Q.5.4 Minimiser tous les caractères de la colonne translated_review.
raw_user = raw_user.withColumn("translated_review", lower(col("translated_review")))
raw_user.select("translated_review").show(10, truncate=False)


# Q.5.5 Afficher le nombre de commentaires pour chacun des groupes de tailles allant de 1 caractère à 10 caractères.
raw_user.withColumn("review_length", length(col("translated_review")))\
        .filter(col("review_length") < 11)\
        .groupBy("review_length").count()\
        .sort("review_length")\
        .show()


# Q5-6 Conserver uniquement les lignes dont le commentaire est de taille supérieure ou égale à 3.
raw_user = raw_user.filter(length(col("translated_review")) > 3)

# Q5-7 Calculer les 20 mots les plus présents pour les commentaires étant positifs.
map_partitions = raw_user.filter(col("sentiment") == "Positive").select("translated_review").rdd
rdd_flat = map_partitions.flatMap(lambda row: row.translated_review.split(" ")).filter(lambda word: len(word) > 1).map(lambda word: (word, 1))
top_20_mots = rdd_flat.reduceByKey(lambda x, y: x+y).sortBy(lambda x: x[1], False).collect()[:20]
print(top_20_mots)


## Nettoyage de raw_app
# Nous avons fait le plus dur. Retournons nettoyer le DataFrame raw_app.

# Q6-1 Changer le type de la colonne reviews en integer en transformant les lignes problématiques si nécessaire.
raw_app = raw_app.withColumn("reviews", col("reviews").cast("integer"))
raw_app = raw_app.fillna({"reviews" : 0})
raw_app.filter(isnull(col("reviews"))).show(5)


#Q6-2 Nous allons maintenant convertir la colonne installs en integer aussi.
raw_app = raw_app.withColumn("installs", regexp_replace(col("installs"), "[^0-9]", ""))\
        .withColumn("installs", col("installs").cast('integer'))
raw_app = raw_app.fillna({"installs" : 0})
raw_app.filter(isnull(col("installs"))).show(5)


# Q6-3 Répéter le même type d'opération pour transformer la colonne price en double.
# Attention ici à bien traiter les nombres à virgule.
raw_app = raw_app.withColumn("price", regexp_replace(col("price"), "[^0-9.,]", ""))\
        .withColumn("price", col("price").cast('double'))


#Q6-4 En partant du principe que la date de la colonne last_updated est au format MMMM d, yyyy,
# convertir cette colonne au format date avec la fonction to_date.
raw_app = raw_app.withColumn("last_updated", to_date(col("last_updated"), "MMMM d, yyyy"))
raw_app.printSchema()
# BONUS: Il y a une anomalie dans une ligne où la valeur de last_updated est dans la colonne 'genres'
raw_app = raw_app.withColumn("last_updated", when(col("genres")=="February 11, 2018",  to_date(col("genres"), "MMMM d, yyyy")).otherwise(col("last_updated")))\
            .withColumn("genres", when(col("genres")=="February 11, 2018", "").otherwise(col("genres")))

raw_app.write \
       .mode('overwrite') \
       .format("jdbc") \
       .option("url", "jdbc:mysql://0.0.0.0:3306/database") \
       .option("dbtable", "gps_app") \
       .option("user", "user") \
       .option("password", "password") \
       .save()