from riotwatcher import RiotWatcher
import requests
import json
import os
from datetime import datetime

api_key = os.environ.get('RIOT_API_KEY')
watcher = RiotWatcher(api_key)

SUMMONER_NAME = "osten"
TAGLINE = "9001"

# Get account info
account = watcher.account.by_riot_id("europe", SUMMONER_NAME, TAGLINE)

# Get summoner data
url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{account['puuid']}"
headers = {"X-Riot-Token": api_key}
response = requests.get(url, headers=headers)
summoner = response.json()

# Get ranked info using PUUID
ranked_url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{account['puuid']}"
ranked_response = requests.get(ranked_url, headers=headers)
ranked = ranked_response.json()

# Get champion mastery (top 3)
mastery_url = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{account['puuid']}/top?count=3"
mastery_response = requests.get(mastery_url, headers=headers)
mastery = mastery_response.json()

# Get champion names from Data Dragon
ddragon_url = "https://ddragon.leagueoflegends.com/cdn/14.5.1/data/en_US/champion.json"
ddragon_response = requests.get(ddragon_url)
champions_data = ddragon_response.json()

champion_map = {}
for champ_key, champ_data in champions_data['data'].items():
    champion_map[int(champ_data['key'])] = champ_data['name']

# Get match IDs (last 5 matches)
matches_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{account['puuid']}/ids?start=0&count=5"
matches_response = requests.get(matches_url, headers=headers)
matches = matches_response.json()

# Get last 5 matches details
last_5_matches = []
for match_id in matches:
    match_detail_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
    match_detail_response = requests.get(match_detail_url, headers=headers)
    match_detail = match_detail_response.json()
    
    for participant in match_detail['info']['participants']:
        if participant['puuid'] == account['puuid']:
            kills = participant['kills']
            deaths = participant['deaths']
            assists = participant['assists']
            if deaths > 0:
                kda = (kills + assists) / deaths
                kda_str = f"{kda:.2f}"
            else:
                kda_str = "Perfect"
            
            result = "WIN" if participant['win'] else "LOSS"
            border_color = "#0099FA" if participant['win'] else "#F5274D"
            
            # Get champion tile image
            champion_name = participant['championName'].lower()
            champion_image_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/{champion_name}_0.jpg"
            
            last_5_matches.append({
                'champion': participant['championName'],
                'champion_image': champion_image_url,
                'kills': kills,
                'deaths': deaths,
                'assists': assists,
                'kda': kda_str,
                'result': result,
                'border_color': border_color
            })
            break

# Prepare ranked data
ranked_solo = None
for queue in ranked:
    if queue.get('queueType') == 'RANKED_SOLO_5x5':
        ranked_solo = queue
        break

if ranked_solo:
    tier = ranked_solo.get('tier', 'UNRANKED').lower()
    rank = ranked_solo.get('rank', '')
    lp = ranked_solo.get('leaguePoints', 0)
    wins = ranked_solo.get('wins', 0)
    losses = ranked_solo.get('losses', 0)
    total_games_ranked = wins + losses
    win_rate = (wins / total_games_ranked) * 100 if total_games_ranked > 0 else 0
    
    # Get emblem URL
    if tier == 'unranked':
        emblem_url = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-emblem/emblem-unranked.png"
    else:
        emblem_url = f"https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-emblem/emblem-{tier}.png"
    
    tier_display = f"{ranked_solo.get('tier', 'N/A')} {ranked_solo.get('rank', 'N/A')}"
else:
    emblem_url = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-emblem/emblem-unranked.png"
    tier_display = "Unranked"
    lp = 0
    wins = 0
    losses = 0
    total_games_ranked = 0
    win_rate = 0

# Get top 3 mastery champions
top_champions = []
for i, champ in enumerate(mastery[:3], 1):
    champion_id = champ['championId']
    champion_name = champion_map.get(champion_id, f"Champion {champion_id}")
    mastery_points = champ['championPoints']
    champion_image = f"https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/{champion_name.lower()}_0.jpg"
    
    top_champions.append({
        'name': champion_name,
        'points': mastery_points,
        'image': champion_image
    })

# Fill missing champions with placeholders if needed
while len(top_champions) < 3:
    top_champions.append({
        'name': 'Unknown',
        'points': 0,
        'image': 'https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/Teemo_0.jpg'
    })

# Generate README content with HTML/CSS styling
readme_content = f"""<h1 style="border-bottom: none; margin-bottom: 0px; font-size: 45px; color: #ffffff">
  osten<span style="font-weight: normal; color: #999;"> #9001</span>
</h1>
<div style="display: flex; justify-content: flex-start; align-items: flex-start; gap: 10px;">
  <div align="left">
    <div style="
      background: #3C4856;
      border-radius: 4px;
      padding: 10px;
      margin: 4px;
      border: 1px solid #56677B;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      display: inline-block;
      min-width: 30px;
      text-align: left;
    ">
      <h3 style="color: #ffffff; margin: 0; font-weight: normal; font-size: 14px">Ranked Solo/Duo</h3>
      <hr style="border: none; height: 1px; background-color: #56677B; margin: 8px -10px; width: 100%;  width: calc(100% + 20px);">
      <div style="margin: -85px 0 -85px 0;">
        <img src="{emblem_url}" 
             style="width: 200px; height: 300px; object-fit: cover; object-position: 50% 50%; display: block; margin: 0 auto;">
      </div>
      <div style="margin-top: 0px; display: flex; justify-content: space-between; align-items: baseline;">
        <h3 style="color: #ffffff; margin: 0; font-size: 17px;">{tier_display}</h3>
        <span style="color: #999; font-size: 14px;">{wins}W {losses}L</span>
      </div>
      <div style="margin-top: -21px; display: flex; justify-content: space-between; align-items: baseline;">
        <h3 style="color: #999; font-size: 14px;">{lp} LP</h3>
        <span style="color: #999; font-size: 14px;">Win rate {win_rate:.0f}%</span>
      </div>
    </div>
  </div>
  <div align="right" style="flex: 1;">
    <div style="
      text-align: left;
      background: #3C4856;
      border-radius: 4px;
      padding: 10px;
      margin: 3px;
      border: 1px solid #56677B;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      display: block;
      min-width: 0px;
      text-align: left;
    ">
        <h3 style="color: #ffffff; margin: 0; font-weight: normal; font-size: 14px">Champion Mastery</h3>
        <hr style="border: none; height: 1px; background-color: #56677B; margin: 8px -10px; width: 100%;  width: calc(100% + 20px);">
        <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
          <div style="text-align: center;">
            <img src="{top_champions[0]['image']}" 
                 style="width: 80px; height: 80px; border-radius: 8px; object-fit: cover; border: 1px solid #56677B;">
            <div style="color: #fff; font-size: 12px; margin-top: 0px;">{top_champions[0]['name']}</div>
            <div style="color: #999; font-size: 12px; margin-top: 0px;">{top_champions[0]['points']:,}</div>
          </div>
          <div style="text-align: center;">
            <img src="{top_champions[1]['image']}" 
                 style="width: 80px; height: 80px; border-radius: 8px; object-fit: cover; border: 1px solid #56677B;">
            <div style="color: #fff; font-size: 12px; margin-top: 0px;">{top_champions[1]['name']}</div>
            <div style="color: #999; font-size: 12px; margin-top: 0px;">{top_champions[1]['points']:,}</div>
          </div>
          <div style="text-align: center;">
            <img src="{top_champions[2]['image']}" 
                 style="width: 80px; height: 80px; border-radius: 8px; object-fit: cover; border: 1px solid #56677B;">
            <div style="color: #fff; font-size: 12px; margin-top: 0px;">{top_champions[2]['name']}</div>
            <div style="color: #999; font-size: 12px; margin-top: 0px;">{top_champions[2]['points']:,}</div>
          </div>
        </div>
        <hr style="border: none; height: 1px; background-color: #56677B; margin: 8px -10px; width: 100%;  width: calc(100% + 20px);">
        <h3 style="color: #ffffff; margin: 0; font-weight: normal; font-size: 14px">Recent Matches</h3>
        <hr style="border: none; height: 1px; background-color: #56677B; margin: 8px -10px; width: 100%;  width: calc(100% + 20px);">
        <div style="display: flex; justify-content: space-around; gap: 15px; margin: 15px 0;">
"""

# Add last 5 matches
for match in last_5_matches:
    readme_content += f"""
    <div style="text-align: center;">
        <img src="{match['champion_image']}" 
             style="width: 40px; height: 40px; border-radius: 200px; object-fit: cover; border: 3px solid {match['border_color']};">
        <div style="color: #fff; font-size: 12px; margin-top: 0px;">{match['kills']}/{match['deaths']}/{match['assists']}</div>
        <div style="color: #999; font-size: 10px; margin-top: 0px;">{match['kda']} KDA</div>
    </div>"""

readme_content += f"""
        </div>
        <hr style="border: none; height: 1px; background-color: #56677B; margin: 8px -10px; width: 100%;  width: calc(100% + 20px);">
        <div style="text-align: center; color: #999; font-size: 11px; margin-top: 10px;">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        </div>
    </div>
  </div>
</div>
"""

# Write to README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("✅ README.md updated successfully with new formatted layout!")
