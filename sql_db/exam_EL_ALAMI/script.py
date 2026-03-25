# Partie 2: SQL Requests
# Q1: Compter le nombre de Pokémon par type dans l'ordre décroissant.

q1_req = """
    SELECT name_type, count(*) as count_members FROM PokemonType AS pt
    LEFT JOIN Types AS t on pt.type_id = t.type_id
    GROUP BY name_type
    ORDER BY count_members DESC;
"""

# Q2: Lister les Pokémon avec un nombre de base de points supérieur à 600, triés de manière décroissante.

q2_req = """
    SELECT name, base_total FROM Pokemon
    WHERE base_total > 600
    ORDER BY base_total DESC;
"""

# Q3: Afficher les types de Pokémon avec la base de points moyenne dans l'ordre croissant

q3_req = """
    SELECT t.name_type, AVG(p.base_total) as avg_base_total FROM PokemonType AS pt
    LEFT JOIN Types AS t on pt.type_id = t.type_id
    LEFT JOIN Pokemon AS p on pt.pokedex_number = p.pokedex_number
    GROUP BY name_type
    ORDER BY avg_base_total ASC;
"""

# Q4: Trouver les Pokémon qui ont la capacité spéciale 'Overgrow' et trier par la base de points dans un ordre décroissant.

q4_req = """
    SELECT p.name, p.base_total FROM PokemonAbility AS pa
    LEFT JOIN Pokemon AS p on pa.pokedex_number = p.pokedex_number
    LEFT JOIN Abilities AS a on a.ability_id = pa.ability_id
    WHERE a.name_ability = 'Overgrow'
    ORDER BY p.base_total DESC;
"""

# Q5: Lister les noms des Pokémon, leur type principal et leur type secondaire (s'ils en ont un). Trier par le nom.

q5_req = """
    SELECT 
    p.name,
    MAX(CASE WHEN rn = 1 THEN t.name_type END) AS primary_type,
    MAX(CASE WHEN rn = 2 THEN t.name_type END) AS secondary_type
FROM (
    SELECT 
        pokedex_number,
        type_id,
        ROW_NUMBER() OVER (PARTITION BY pokedex_number ORDER BY type_id) AS rn
    FROM PokemonType
) pt
LEFT JOIN Pokemon p 
    ON p.pokedex_number = pt.pokedex_number
LEFT JOIN Types t 
    ON t.type_id = pt.type_id
GROUP BY p.name
ORDER BY p.name;
"""
# Q6: Afficher les Pokémon avec un total de stats supérieur à la moyenne par génération.

q6_req = """
    SELECT 
        p.name,
        p.generation,
    p.base_total
FROM Pokemon p
WHERE p.base_total > (
    SELECT AVG(p2.base_total)
    FROM Pokemon p2
    WHERE p2.generation = p.generation
)
ORDER BY p.generation, p.base_total DESC;
"""

# Q7: Trouver les Pokémon de type "fire" avec une attaque supérieure à 100.

q7_req = """
    SELECT p.name, s.attack FROM Stats as s
    LEFT JOIN Pokemon as p on s.pokedex_number = p.pokedex_number
    LEFT JOIN PokemonType as pt on s.pokedex_number = pt.pokedex_number
    WHERE pt.type_id = (SELECT type_id FROM Types WHERE name_type = 'fire') AND s.attack > 100;
"""

# Q8: Indiquer si le total des stats d'un Pokémon est supérieur ou inférieur à la moyenne par génération.

q8_req = """
    SELECT p.name, p.generation, p.base_total as total_stats,
        CASE 
                WHEN p.base_total > (
                        SELECT AVG(p2.base_total)
                        FROM Pokemon p2 WHERE p2.generation = p.generation) THEN 'Supérieur à la moyenne'
                ELSE 'Inférieur ou égal à la moyenne'
                END AS total_stats_comparison
        FROM Stats s
LEFT JOIN Pokemon p on s.pokedex_number = p.pokedex_number;
"""

# Python script
import psycopg2

conn = psycopg2.connect(database="examen_EL_ALAMI",
                        host="54.170.119.49",
                        user="daniel",
                        password="datascientest",
                        port="5432")

cur = conn.cursor()

def execute_query(query, display_all=False):
    cur.execute(query)
    response = cur.fetchall()
    print(' | '.join([' ']+[desc.name for desc in cur.description]))
    if not display_all:
        response = response[:10]
    for i, row in enumerate(response):
        print(' | '.join([str(i)]+[str(val) for val in row]))

def close_connection():
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("Q1: Compter le nombre de Pokémon par type dans l'ordre décroissant.")
    execute_query(q1_req)
    print("\nQ2: Lister les Pokémon avec un nombre de base de points supérieur à 600, triés de manière décroissante.")
    execute_query(q2_req)
    print("\nQ3: Afficher les types de Pokémon avec la base de points moyenne dans l'ordre croissant")
    execute_query(q3_req)
    print("\nQ4: Trouver les Pokémon qui ont la capacité spéciale 'Overgrow' et trier par la base de points dans un ordre décroissant.")
    execute_query(q4_req)
    print("\nQ5: Lister les noms des Pokémon, leur type principal et leur type secondaire (s'ils en ont un). Trier par le nom.")
    execute_query(q5_req)
    print("\nQ6: Afficher les Pokémon avec un total de stats supérieur à la moyenne par génération.")
    execute_query(q6_req)
    print("\nQ7: Trouver les Pokémon de type 'fire' avec une attaque supérieure à 100.")
    execute_query(q7_req)
    print("\nQ8: Indiquer si le total des stats d'un Pokémon est supérieur ou inférieur à la moyenne par génération.")
    execute_query(q8_req)

    close_connection()
 
