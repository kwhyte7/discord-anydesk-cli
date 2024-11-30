import discord 
import functions
import asyncio

AUTHORISED_USERS = ["ADD YOUR DISCORD CLIENT ID HERE AS AN INTEGER"] # the bot will only listen to these users
AUTHORISED_CHANNELS = ["ADD DISCORD CHANNEL IDS HERE AS AN INTEGER"] # the bot will only listen to these channels.
COMMAND_PREFIX = "!" # prefix for non terminal commands

async def show_commands(temulator, message, arguments=""):
	await message.reply("\n".join(list(COMMANDS.keys())))

COMMANDS = {
	"d" : functions.download_from_discord,
	"show" : functions.upload_to_discord,
	"help" : show_commands
}

with open("token.txt", "r") as f:
	TOKEN = f.read()
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
terminal_emulator = functions.TerminalEmulator()

@client.event
async def on_ready():
    print("bot's ready")
    
    
@client.event
async def on_message(message):
    if not (message.author.id in AUTHORISED_USERS and message.channel.id in AUTHORISED_CHANNELS):
        return

    try:
        if message.content.startswith(COMMAND_PREFIX):
            for command, func in COMMANDS.items():
                if command == message.content.split()[0][1:]:
                    await func(terminal_emulator, message, message.content.split()[1:])
                    return
        # Fire off the terminal command asynchronously without waiting for it to finish
        # This runs the command in the background, without blocking the event loop.
        asyncio.create_task(run_terminal_command(message))  # This will run in the background.

        print(message.content)

    except Exception as e:
        await functions.send_long_message(message, f"```{e}```")

# This function will run the terminal command asynchronously.
async def run_terminal_command(message):
    # Run the command asynchronously, using a thread so it doesn't block
    result, _ = await asyncio.to_thread(terminal_emulator.run_command, message.content)

    # Send the result of the command asynchronously
    if len(result) < 2000 - 6:
		result = f"```{result}```"
    await functions.send_long_message(message, result)
				
client.run(TOKEN)
