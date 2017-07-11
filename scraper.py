import requests
import shutil

BASE_URL = "http://www.football-data.co.uk/mmz4281/%s/E0.csv"
START_SEASON = 2003
END_SEASON = 2015 

def season_code(start):
    end = start + 1
    return str(start)[-2:] + str(end)[-2:]

season = START_SEASON
while season <= END_SEASON:
    s_code = season_code(season)
    response = requests.get(BASE_URL % s_code, stream=True)
    if response.status_code == 200:
        with open('%s.csv' % s_code, 'w') as f:
            f.write(response.text.encode('utf-8'))

    season+=1
