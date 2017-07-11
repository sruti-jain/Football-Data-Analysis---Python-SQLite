#scraper.py
Scrapes football-data and downloads csv files for Premier League

#parse.py
Parses the data files and creates a db. Uses SQLAlchemy, so you can choose
the sql database you wish to use.

#Data fixes
Before creating the db, you should fix the following datapoints if you are
scraping the data yourself and not using the db or csv files in this repo

Removed non-unicode, 8bit bytestrings  used as a leading space-character
in Referee names from 0405.csv since it caused issues with parsing the data
Lines: 337 - 345

Referee data fixes:
```
0910   | 2009-11-07 | Wolves    | Arsenal   | St Bennett  => "S Bennett"
0910   | 2009-11-08 | Chelsea   | Man United | Mn Atkinson => "M Atkinson"
0910   | 2009-11-28 | Wigan     | Sunderland | Mn Atkinson => "M Atkinson"
0607   | 2007-04-06 | Everton   | Fulham    | D Gallagh => "D Gallagher"
0607   | 2007-05-05 | Reading   | Watford   | D Gallaghe => "D Gallagher"
0304   | 2003-08-23 | Southampton | Birmingham | Graham Barber => "G Barber"
0304   | 2003-09-20 | Newcastle   | Bolton     | Graham Barber => "G Barber"
```

Added missing referee data in 1213.csv

#Schema:
```
CREATE TABLE performances (
    id INTEGER NOT NULL,
    team_id INTEGER,
    game_id INTEGER,
    ft_goals INTEGER,
    ft_result VARCHAR,
    ht_goals INTEGER,
    ht_result VARCHAR,
    odds_result VARCHAR,
    at VARCHAR,
    shots INTEGER,
    shots_ot INTEGER,
    fouls INTEGER,
    corners INTEGER,
    yellows INTEGER,
    reds INTEGER,
    week INTEGER,
    points INTEGER,
    gd INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(team_id) REFERENCES teams (id),
    FOREIGN KEY(game_id) REFERENCES games (id)
  );
CREATE TABLE referees (
    id INTEGER NOT NULL,
    name VARCHAR,
    PRIMARY KEY (id)
  );
CREATE TABLE games (
    id INTEGER NOT NULL,
    season INTEGER,
    div VARCHAR,
    date DATE,
    home_id INTEGER,
    away_id INTEGER,
    referee_id INTEGER,
    ft_result VARCHAR,
    ht_result VARCHAR,
    home_odds FLOAT,
    draw_odds FLOAT,
    away_odds FLOAT,
    odds_result VARCHAR,
    PRIMARY KEY (id),
    FOREIGN KEY(home_id) REFERENCES performances (id),
    FOREIGN KEY(away_id) REFERENCES performances (id),
    FOREIGN KEY(referee_id) REFERENCES referees (id)
    );
CREATE TABLE teams (
    id INTEGER NOT NULL,
    name VARCHAR,
    PRIMARY KEY (id)
  );
```

#Sample Queries: Fetching the point table
```
To get the table standings at a particular gameweek X in season Y:
Let's say Gameweek 20 in the 20152016 season..

  select t.name, p.points
  from performances p
  join games g on p.game_id = g.id
  join teams t on t.id = p.team_id
  where g.season=20152016
  and p.week=20
  order by p.points desc
  ;

OUTPUT:
Arsenal     42
Leicester   40
Man City    39
Tottenham   36
Man United  33
West Ham    32
Crystal Pa  31
Liverpool   30
Watford     29
Stoke       29
Everton     27
West Brom   26
Southampto  24
Norwich     23
Chelsea     23
Bournemout  21
Swansea     19
Newcastle   17
Sunderland  15
Aston Vill  8
```