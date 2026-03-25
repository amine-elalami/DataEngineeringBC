#!/bin/bash

echo "1. Affichez le nombre d'attributs par document ainsi que l'attribut name. \
Combien y a-t-il d'attribut par document ? N'affichez que les 12 premières lignes avec la commande head (notebook #2)."
cat people.json | jq '.[] | {name, attributes_count: length}' > res_jq.txt && head -n 12 res_jq.txt
echo "Commande : cat people.json | jq '.[] | {name, attributes_count: length}' > res_jq.txt && head -n 12 res_jq.txt"
echo "Réponse : 17 attributs par document"
echo -e "\n---------------------------------\n"

echo "2. Combien y a-t-il de valeur "unknown" pour l'attribut "birth_year" ? Utilisez la commande tail afin d'isoler la réponse."
cat people.json | jq 'group_by(.birth_year).[] | {birth_year: .[0].birth_year, count: length}' > res_jq.txt && tail res_jq.txt 
echo "Commande : cat people.json | jq 'group_by(.birth_year).[] | {birth_year: .[0].birth_year, count: length}' > res_jq.txt && tail res_jq.txt "
echo "Réponse : 42 personnes ont une valeur "unknown" pour l'attribut "birth_year"."
echo -e "\n---------------------------------\n"

echo "3. Affichez la date de création de chaque personnage et son nom. La date de création \
doit être de cette forme : l'année, le mois et le jour. N'affichez que les 10 premières lignes. (Pas de Réponse attendue)"
cat people.json | jq '.[]  | {name, creation : (.created | split("T") | .[0])}' > res_jq.txt && head -n 10 res_jq.txt
echo "Commande : cat people.json | jq '.[]  | {name, creation : (.created | split("T") | .[0])}' > res_jq.txt && head -n 10 res_jq.txt"
echo "Réponse : réponse de la question n si demandé"
echo -e "\n---------------------------------\n"

echo "4. Certains personnages sont nés en même temps. Retrouvez toutes les pairs d'ids (2 ids) des personnages nés en même temps."
cat people.json | jq 'group_by(.birth_year)[] | select(length==2) | map(.id)' > res_jq.txt && cat res_jq.txt
echo "Commande : cat people.json | jq 'group_by(.birth_year)[] | select(length==2) | map(.id)' > res_jq.txt && cat res_jq.txt"
echo "Réponse : [1, 5] [4, 11] [6, 36] [43, 51] [21, 62] [32, 52]"
echo -e "\n---------------------------------\n"

echo "5. Renvoyez le numéro du premier film (de la liste) dans lequel chaque personnage a été vu suivi du nom du personnage.\
 N'affichez que les 10 premières lignes. (Pas de Réponse attendue)"
cat people.json | jq '.[] | {first_film : .films.[0], name}' > res_jq.txt && head res_jq.txt
echo "Commande : cat people.json | jq '.[] | {first_film : .films.[0], name}' > res_jq.txt && head res_jq.txt"
echo "Réponse : "
echo -e "\n---------------------------------\n"

echo -e "\n----------------BONUS----------------\n"
echo "6 - Supprimez les documents lorsque l'attribut height n'est pas un nombre."
cat people.json | jq ' map(select(.height != "unknown")) ' > bonus/people_6.json
echo "Command : cat people.json | jq ' map(select(.height != "unknown")) ' > bonus/people_6.json"
echo -e "\n---------------------------------\n"

echo "7 - Transformer l'attribut height en nombre."
cat bonus/people_6.json | jq 'map(.height |= tonumber)' > bonus/people_7.json
echo "Command : cat bonus/people_6.json | jq 'map(.height |= tonumber)' > bonus/people_7.json"
echo -e "\n---------------------------------\n"

echo "8 - Ne renvoyez que les personnages dont la taille est entre 156 et 171."
cat bonus/people_7.json | jq ' map(select((.height >= 156) and (.height <= 171)))' > bonus/people_8.json && cat bonus/people_8.json
echo "Command : cat bonus/people_7.json | jq ' map(select((.height >= 156) and (.height <= 171)))' > bonus/people_8.json && cat bonus/people_8.json"
echo -e "\n---------------------------------\n"

echo "9 - Renvoyez le plus petit individu de people_8.json et affichez cette phrase en une seule commande : \
'<nom_du_personnage> is <taille> tall' Renvoyez la commande dans un fichier people_9.txt et non .json."
cat bonus/people_8.json | jq 'min_by(.height) | "\(.name) is \(.height) tall"' > bonus/people_9.txt && cat bonus/people_9.txt
echo "Command : cat bonus/people_8.json | jq 'min_by(.height) | \"\(.name) is \(.height) tall\"' > bonus/people_9.txt && cat bonus/people_9.txt"
echo -e "\n---------------------------------\n"
