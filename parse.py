import csv
import os
import sqlalchemy
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Float

HOME_RESULT_MAP = {'H':'W','D':'D','A':'L'}
AWAY_RESULT_MAP = {'A':'W','D':'D','H':'L'}
POINTS_MAP = {'W':3, 'D':1, 'L': 0}

engine = create_engine('sqlite:///matchData.db', echo=True)
Base = declarative_base()

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    div = Column(String)
    date = Column(Date)
    home_id = Column(Integer, ForeignKey('performances.id')) 
    away_id = Column(Integer, ForeignKey('performances.id')) 
    referee_id = Column(Integer, ForeignKey('referees.id')) 
    ft_result = Column(String)
    ht_result = Column(String)
    home_odds = Column(Float)
    draw_odds = Column(Float)
    away_odds = Column(Float)
    odds_result = Column(String)

    def __repr__(self):
        return "<Game(home_id='%s', away_id='%s')>" % (
            self.home_id, self.away_id)

class Performance(Base):
    __tablename__ = "performances"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id')) 
    game_id = Column(Integer, ForeignKey('games.id')) 
    ft_goals = Column(Integer)
    ft_result = Column(String)
    ht_goals = Column(Integer)
    ht_result = Column(String)
    odds_result = Column(String)
    at = Column(String)
    shots = Column(Integer)
    shots_ot = Column(Integer)
    fouls = Column(Integer)
    corners = Column(Integer)
    yellows = Column(Integer)
    reds = Column(Integer)
    week = Column(Integer)
    points = Column(Integer)
    gd = Column(Integer)
    
class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Referee(Base):
    __tablename__ = "referees"
    id = Column(Integer, primary_key=True)
    name = Column(String)

def process_team(name, session):
    team = session.query(Team.id).filter(Team.name == name).one_or_none()
    if team is not None:
        return team[0]
    else:
        team = Team(**{'name':name})
        session.add(team)
        session.flush()
        session.refresh(team)
        return team.id


def process_ref(name, session):
    ref = session.query(Referee.id).filter(Referee.name == name).one_or_none()
    if ref is not None:
        return ref[0]
    else:
        ref = Referee(**{'name':name})
        session.add(ref)
        session.flush()
        session.refresh(ref)
        return ref.id

    
            
Base.metadata.create_all(engine)
    
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()    

DATA_DIR = "data/"
REL_COLS = 26 #Number of Relevant columns

for csv_file in os.listdir(os.getcwd() + "/" + DATA_DIR):
    print csv_file
    with open(DATA_DIR + csv_file, 'r') as f:
        reader = csv.reader(f)
        header = reader.next()
        header_keys = {h:{'index': idx, 'key': h.lower() + "_"} 
            for idx, h in enumerate(header[:REL_COLS])}
            
        season = (2000+int(csv_file[0:2]))*10000 + (2000+int(csv_file[2:4]))

        season_data = {}

        for row in reader:
            # print row
            match_data = {header_keys[h]['key']: row[header_keys[h]['index']] 
                for h in header_keys.keys()}

            home_team_id = process_team(match_data['hometeam_'], session)
            away_team_id = process_team(match_data['awayteam_'], session)
            referee_id = process_ref(match_data['referee_'], session)

            season_data.setdefault(home_team_id, {})
            season_data[home_team_id].setdefault('week', 0)
            season_data[home_team_id].setdefault('points', 0)
            season_data[home_team_id].setdefault('gd', 0)

            season_data.setdefault(away_team_id, {})
            season_data[away_team_id].setdefault('week', 0)
            season_data[away_team_id].setdefault('points', 0)
            season_data[away_team_id].setdefault('gd', 0)

            season_data[home_team_id]['week'] += 1
            season_data[away_team_id]['week'] += 1

            season_data[home_team_id]['points'] += POINTS_MAP[HOME_RESULT_MAP[match_data['ftr_']]]
            season_data[away_team_id]['points'] += POINTS_MAP[AWAY_RESULT_MAP[match_data['ftr_']]]
            
            season_data[home_team_id]['gd'] += int(match_data['fthg_']) - int(match_data['ftag_'])
            season_data[away_team_id]['gd'] += int(match_data['ftag_']) - int(match_data['fthg_'])

            ho_ = float(match_data['b365h_'])
            do_ = float(match_data['b365d_'])
            ao_ = float(match_data['b365a_'])
            h_odds = 100.0/(1.0 + ho_/do_ + ho_/ao_)
            d_odds = 100.0/(1.0 + do_/ao_ + do_/ho_)
            a_odds = 100.0/(1.0 + ao_/do_ + ao_/ho_)

            max_odds = max(h_odds, d_odds, a_odds)
            if h_odds == max_odds:
                odds_result = 'H'
            elif d_odds == max_odds:
                odds_result = 'D'
            else:
                odds_result = 'A'

            home_p = Performance(**{
                'team_id': home_team_id,
                'ft_goals': match_data['fthg_'],
                'ht_goals': match_data['hthg_'],
                'shots': match_data['hs_'],
                'shots_ot': match_data['hst_'],
                'fouls': match_data['hf_'],
                'corners': match_data['hc_'],
                'yellows': match_data['hy_'],
                'reds': match_data['hr_'],
                'ft_result': HOME_RESULT_MAP[match_data['ftr_']],
                'odds_result': HOME_RESULT_MAP[odds_result],
                'ht_result': HOME_RESULT_MAP[match_data['htr_']],
                'at':'H',
                'week': season_data[home_team_id]['week'],
                'points': season_data[home_team_id]['points'],
                'gd': season_data[home_team_id]['gd'],
                })

            away_p = Performance(**{
                'team_id': away_team_id,
                'ft_goals': match_data['ftag_'],
                'ht_goals': match_data['htag_'],
                'shots': match_data['as_'],
                'shots_ot': match_data['ast_'],
                'fouls': match_data['af_'],
                'corners': match_data['ac_'],
                'yellows': match_data['ay_'],
                'reds': match_data['ar_'],
                'ft_result': AWAY_RESULT_MAP[match_data['ftr_']],
                'odds_result': AWAY_RESULT_MAP[odds_result],
                'ht_result': AWAY_RESULT_MAP[match_data['htr_']],
                'at':'A',
                'week': season_data[away_team_id]['week'],
                'points': season_data[away_team_id]['points'],
                'gd': season_data[away_team_id]['gd'],
                })

            session.add(home_p)
            session.add(away_p)
            session.flush()
            session.refresh(home_p)
            session.refresh(away_p)


            game = Game(**{
                'season': season,
                'date': datetime.strptime(
                    row[header_keys['Date']['index']],'%d/%m/%y'),
                'home_id': home_p.id,
                'away_id': away_p.id,
                'referee_id': referee_id,
                'div': match_data['div_'],
                'ft_result': match_data['ftr_'],
                'ht_result': match_data['htr_'],
                'home_odds': match_data['b365h_'],
                'draw_odds': match_data['b365d_'],
                'away_odds': match_data['b365a_'],
                'odds_result' : odds_result,
                })

            session.add(game)
            session.flush()
            session.refresh(game)

            home_p.game_id = game.id
            away_p.game_id = game.id

            session.flush()

session.commit()



