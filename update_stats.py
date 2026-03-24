from riotwatcher import RiotWatcher, LolWatcher
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

# Get match IDs (last 5 matches)
matches_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{account['puuid']}/ids?start=0&count=5"
matches_response = requests.get(matches_url, headers=headers)
matches = matches_response.json()

# Generate README content
readme_content = f"""# osten9000
###
**Summoner:** {account['gameName']}#{account['tagLine']}  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## RANKED INFO
"""

if ranked:
    for queue in ranked:
        readme_content += f"""
**{queue.get('queueType', 'N/A')}**  
Tier: {queue.get('tier', 'N/A')} {queue.get('rank', 'N/A')}  
League Points: {queue.get('leaguePoints', 'N/A')} LP  
Wins: {queue.get('wins', 'N/A')}  
Losses: {queue.get('losses', 'N/A')}  
"""
        if queue.get('wins') and queue.get('losses'):
            total = queue['wins'] + queue['losses']
            win_rate = (queue['wins'] / total) * 100
            readme_content += f"Win Rate: {win_rate:.1f}%\n"
else:
    readme_content += "\nNo ranked data found - player is unranked\n"
"""
readme_content += "\n## LAST 5 MATCHES\n\n"

for i, match_id in enumerate(matches, 1):
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
                kda_str = f"{kda:.2f}:1"
            else:
                kda_str = "Perfect"
            
            result = "WIN" if participant['win'] else "LOSS"
            lane = participant.get('teamPosition', participant.get('lane', 'N/A'))
            
            readme_content += f"""
### Match {i}: {result} - {participant['championName']}
- **KDA:** {kills}/{deaths}/{assists} ({kda_str})
- **Damage:** {participant['totalDamageDealtToChampions']:,}
- **Lane:** {lane}
- **Gold:** {participant['goldEarned']:,}
- **Duration:** {match_detail['info']['gameDuration'] // 60}m {match_detail['info']['gameDuration'] % 60}s
- **Queue:** {match_detail['info']['gameMode']}
"""
            break

readme_content += 
"""

"""
---
*Stats automatically updated every 6 hours via GitHub Actions*
"""

# Write to README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("✅ README.md updated successfully!")
