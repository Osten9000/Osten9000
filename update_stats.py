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

# Generate README content
readme_content = f"""# osten9000

### 

**Summoner:** {account['gameName']}#{account['tagLine']}  
**Summoner Level:** {summoner.get('summonerLevel', 'N/A')}  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## LEAGUE RANKED INFO
"""

if ranked:
    for queue in ranked:
        readme_content += f""" 
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

# Write to README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("✅ README.md updated successfully!")
