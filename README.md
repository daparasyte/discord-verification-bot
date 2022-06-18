# Discord Verification Bot
Make your own Captcha verification bot for your discord servers using Python and Nextcord.

## How To Get Started:
1. Download the code: https://github.com/daparasyte/discord-verification-bot/archive/refs/heads/main.zip
2. Install dependencies using: `pip install -r requirements.txt`
3. Create your discord bot in https://discord.com/developers/applications and invite the bot in your server
4. Copy the bot token and paste it in the `.env` file.
5. Create a channel in your discord server where you want to run the bot and paste this channel's ID in the `.env` file (you need to turn on developer mode from discord setting to copy the IDs).
6. Create a verified role for your server and paste the role ID in the `.env` file.
7. Make three new folders namely: `captchaFolder`, `UserID` and `Counter`.

## Setup:
1. Make sure the bot is operating in only one channel. (i.e. the one we created earlier)
2. New members should not be able to see other channels without getting the verification role. (the one we created earlier)

## Running the bot:
1. Run the code. (You will see that the bot comes online in your discord server)
2. Type `verify` in the channel - ONLY server owners can use this command.

## Here is how it works:
![verify](https://user-images.githubusercontent.com/62950304/174449147-63d4cafc-4bc0-44d1-8863-b43a22034989.gif)
