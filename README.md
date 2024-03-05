# EdenRPG

- https://github.com/ZaneH/edenrpg-bot

Using the lessons learned from DaFarmz, here is the new and improved version of the game.

Invite the bot using [this link](https://discord.com/api/oauth2/authorize?client_id=1141161773983088640&permissions=339008&scope=bot) or visit the home grown Discord server [here](https://discord.gg/pasxV2MTvW).

## Quickstart
    
```bash
git clone https://github.com/ZaneH/edenrpg-bot.git
cd edenrpg-bot

conda create -n edenrpg python=3.10 -y
conda activate edenrpg
pip install -r requirements.txt

# Start a MongoDB instance
make mongodb

# Start bot
python main.py
```

## Environment Variables

```
DISCORD_TOKEN=
MONGO_URI=
TOPGG_WEBHOOK_SECRET=
```

## Other

- [Game progression notebook](https://df.zaaane.com/notebooks/progression.html)