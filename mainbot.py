from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response
import discord
import zipfile

# token
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# bot setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

# message
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('the message was empty')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

@client.event
async def on_ready() -> None:
    print(f'{client.user} is Now Running !!!')


@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

    # send a zipped game!!!
    if message.content.startswith('game'):
        file_paths = [
            r'C:\Users\user\Desktop\game\open.bat',
            r'C:\Users\user\Desktop\game\surviveio.py'
        ]
        with zipfile.ZipFile('game_files.zip', 'w') as zip_file:
            for file_path in file_paths:
                zip_file.write(file_path, os.path.basename(file_path))

        with open('game_files.zip', 'rb') as file:
            await message.channel.send(file=discord.File(file, filename='open_to_open.zip'))



def main() -> None:
    client.run(token=TOKEN)

if __name__ == "__main__":
    main()
