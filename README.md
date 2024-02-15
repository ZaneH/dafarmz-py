# DaFarmz 2.0

Using the lessons learned from 1.0, here is the next iteration of DaFarmz.
An idle farming game for Discord using [Cup Nooble's Sprout Lands](https://cupnooble.itch.io/sprout-lands-asset-pack) for the art.

Invite the bot using [this link](https://discord.com/api/oauth2/authorize?client_id=1141161773983088640&permissions=339008&scope=bot) or visit the home grown Discord server [here](https://discord.gg/pasxV2MTvW).

## Quickstart
    
```bash
git clone https://github.com/ZaneH/dafarmz-py.git
cd dafarmz-py

conda create -n dafarmz-py python=3.10 -y
conda activate dafarmz-py
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