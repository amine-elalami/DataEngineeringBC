-- Create the Animes table to store the initial data:
DROP TABLE IF EXISTS Animes;
CREATE TABLE Animes (
  anime_id SERIAL PRIMARY KEY,
  english_name VARCHAR(50) NOT NULL,
  score DECIMAL NOT NULL,
  genres VARCHAR(45) NOT NULL,
  type VARCHAR(10) NOT NULL,
  episodes INTEGER NULL,
  aired VARCHAR(45) NOT NULL,
  premiered VARCHAR(20) DEFAULT NULL,
  producers VARCHAR(45) NOT NULL,
  studios VARCHAR(45) NOT NULL,
  source VARCHAR(20) NOT NULL,
  duration VARCHAR(20) NOT NULL,
  rating VARCHAR(50) NOT NULL,
  ranked DECIMAL NOT NULL,
  popularity INTEGER NOT NULL
);

-- Insert the provided data into the Animes table:
INSERT INTO Animes(English_name, Score, Genres, Type, Episodes, Aired, Premiered, Producers, Studios, Source, Duration, Rating, Ranked, Popularity) VALUES
('Cowboy Bebop', 8.78, 'Action, Adventure, Drama, Sci-Fi, Space', 'TV', 26, 'Apr 3, 1998 to Apr 24, 1999', 'Spring 1998', 'Bandai Visual', 'Sunrise', 'Original', '24 min. per ep', 'R - 17+ (violence & profanity)', 28.0, 39),
('Cowboy Bebop:The Movie', 8.39, 'Action, Drama, Sci-Fi, Space', 'Movie', 1, 'Sep 1, 2001', null, 'Sunrise, Bandai Visual', 'Bones', 'Original', '1 hr. 55 min.', 'R - 17+ (violence & profanity)', 159.0, 518),
('Naruto', 7.91, 'Action, Adventure, Shounen', 'TV', 220, 'Oct 3, 2002 to Feb 8, 2007', 'Fall 2002', 'TV Tokyo, Shueisha', 'Studio Pierrot', 'Manga', '23 min. per ep.', 'PG-13 - Teens 13 or older', 660.0, 8),
('One Piece', 8.52, 'Action, Adventure, Shounen', 'TV', null, 'Oct 20, 1999 to ?', 'Fall 1999', 'Fuji TV, Shueisha', 'Toei Animation', 'Manga', '24 min.', 'PG-13 - Teens 13 or older', 95.0, 31),
('Mobile Suit Gundam SEED', 7.79, 'Action, Drama, Military, Sci-Fi, Space', 'TV', 50, 'Oct 5, 2002 to Sep 27, 2003', 'Fall 2002', 'Sotsu, Sony Music Entertainment', 'Sunrise', 'Original', '24 min. per ep.', 'R - 17+ (violence & profanity)', 850.0, 1057),
('Mobile Suit Gundam SEED Destiny', 7.22, 'Action, Drama, Military, Sci-Fi, Space', 'TV', 50, 'Oct 9, 2004 to Oct 1, 2005', 'Fall 2004', 'Sotsu, Sony Music Entertainment', 'Sunrise', 'Original', '24 min. per ep.', 'R - 17+ (violence & profanity)', 2687.0, 1530);

-- Check if tables exist before creating new ones to avoid errors:
DROP TABLE IF EXISTS Rating, Season, Producer, AnimeProducer, Studio, Genre, AnimeGenre;

-- Create the new tables to normalize the data:
CREATE TABLE Rating (
  rating_id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);

CREATE TABLE Season (
  season_id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  year INTEGER NULL
);

CREATE TABLE Producer (
  producer_id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);

CREATE TABLE AnimeProducer (
  anime_id INTEGER NOT NULL,
  producer_id INTEGER NOT NULL,
  PRIMARY KEY (anime_id, producer_id)
);

CREATE TABLE Studio (
  studio_id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);

CREATE TABLE Genre (
  genre_id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);

CREATE TABLE AnimeGenre (
  anime_id INTEGER NOT NULL,
  genre_id INTEGER NOT NULL,
  PRIMARY KEY (anime_id, genre_id)
);

-- Insert Values into the new tables:
INSERT INTO Rating(name) VALUES
    ('PG-13 - Teens 13 or older'),
    ('R - 17+ (violence & profanity)');

INSERT INTO Season(name, year) VALUES
    ('Spring', 1998),
    ('Fall', 1999),
    ('Fall', 2002),
    ('Fall', 2004);

INSERT INTO Producer(name) VALUES
    ('Bandai Visual'),
    ('Sunrise'),
    ('TV Tokyo'),
    ('Shueisha'),
    ('Fuji TV'),
    ('Sotsu'),
    ('Sony Music Entertainment');

INSERT INTO AnimeProducer(anime_id, producer_id)
    SELECT a.anime_id, p.producer_id
    FROM Animes a
    JOIN Producer p ON a.producers LIKE CONCAT('%', p.name, '%');

INSERT INTO Studio(name) VALUES
    ('Sunrise'),
    ('Bones'),
    ('Studio Pierrot'),
    ('Toei Animation');

INSERT INTO Genre(name) VALUES
    ('Action'),
    ('Adventure'),
    ('Drama'),
    ('Sci-Fi'),
    ('Space'),
    ('Shounen'),
    ('Military');

INSERT INTO AnimeGenre(anime_id, genre_id)
    SELECT a.anime_id, g.genre_id
    FROM Animes a
    JOIN Genre g ON a.genres LIKE CONCAT('%', g.name, '%');


-- Update the Animes table to reflect the new schema and populate the new columns:
UPDATE Animes
    SET
    type = 
        CASE 
            WHEN type = 'TV' THEN
                1
            WHEN type = 'Movie' THEN
                0
            ELSE NULL
        END,
    source = 
        CASE 
            WHEN source = 'Original' THEN
                1
            WHEN source = 'Manga' THEN
                0
            ELSE NULL
        END,
    duration = 
        CASE 
            WHEN type = '0' THEN
                (CAST(SUBSTRING(duration FROM '([0-9]+) hr') AS INTEGER) * 60) +
                CAST(SUBSTRING(duration FROM '([0-9]+) min') AS INTEGER)
            WHEN type = '1' THEN
                CAST(SUBSTRING(duration FROM '([0-9]+) min') AS INTEGER)
            ELSE NULL
        END;

-- Modify the Animes table to fit the new schema:
ALTER TABLE Animes
    ALTER COLUMN type TYPE BOOLEAN USING type::boolean,
    ALTER COLUMN source TYPE BOOLEAN USING source::boolean,
    ALTER COLUMN duration TYPE INTEGER USING duration::integer,
    ALTER COLUMN ranked TYPE INTEGER USING ranked::integer,

    ALTER COLUMN type SET NOT NULL,
    ALTER COLUMN source SET NOT NULL,
    ALTER COLUMN duration SET NOT NULL,
    ALTER COLUMN ranked SET NOT NULL;

-- Add foreign keys and new columns:
ALTER TABLE Animes
    ADD COLUMN premiered_id INTEGER DEFAULT NULL,
    ADD COLUMN studio_id INTEGER NOT NULL,
    ADD COLUMN rating_id INTEGER NOT NULL,
    ADD COLUMN start_date DATE NOT NULL,
    ADD COLUMN end_date DATE NULL,
    ADD FOREIGN KEY (premiered_id) REFERENCES Season(season_id),
    ADD FOREIGN KEY (studio_id) REFERENCES Studio(studio_id),
    ADD FOREIGN KEY (rating_id) REFERENCES Rating(rating_id);

-- Update the Animes table to populate the new foreign key columns and date columns based on the existing data:
UPDATE Animes
    SET
    premiered_id = (
        SELECT season_id
        FROM Season
        WHERE Animes.premiered = CONCAT(Season.name, ' ', Season.year)
        ),
    studio_id = (
        SELECT studio_id
        FROM Studio
        WHERE Animes.studios = Studio.name
        ),
    rating_id = (
        SELECT rating_id
        FROM Rating
        WHERE Animes.rating = Rating.name
        ),
    start_date = TO_DATE(SUBSTRING(aired FROM '([A-Za-z]+ [0-9]+, [0-9]+) to'), 'Mon DD, YYYY'),
    end_date = TO_DATE(SUBSTRING(aired FROM 'to ([A-Za-z]+ [0-9]+, [0-9]+)'), 'Mon DD, YYYY');

-- Remove the old columns that are now represented by foreign keys and new columns:
ALTER TABLE Animes
    DROP COLUMN aired,
    DROP COLUMN premiered,
    DROP COLUMN producers,
    DROP COLUMN studios,
    DROP COLUMN rating;
