import subprocess
import asyncio
import os
import discord
import aiohttp

import os
import subprocess
import asyncio

class TerminalEmulator:
    def __init__(self):
        # Initialize with the current working directory
        self.current_directory = os.getcwd()

    def run_command(self, command):
        try:
            # Handle "cd" commands manually
            if command.startswith("cd"):
                # Extract the target directory
                target_dir = command[3:].strip() or "~"  # Default to home if no directory is given
                
                # If target_dir is "~", expand it to the current user's home directory
                if target_dir == "~":
                    target_dir = os.path.expanduser("~")
                
                # Resolve the full path (relative to current directory if it's not absolute)
                new_directory = os.path.join(self.current_directory, target_dir) if not os.path.isabs(target_dir) else target_dir

                # Normalize the path (resolve any relative paths like ".." and "." as well)
                new_directory = os.path.abspath(new_directory)

                if os.path.isdir(new_directory):  # Validate directory exists
                    self.current_directory = new_directory
                    return f"Changed directory to {self.current_directory}", 0
                else:
                    return f"Directory not found: {new_directory}", 1

            # For other commands, run them in the current directory
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.current_directory  # Use the tracked directory
            )

            # Return output or error
            if result.stdout:
                return result.stdout.strip(), 0
            if result.stderr:
                return result.stderr.strip(), 1
            return "No output", 1  # In case there is no output (stdout and stderr are empty)

        except Exception as e:
            return f"Error: {str(e)}", 2  # Ensure a tuple is returned

    async def run_command_async(self, command, cb):
        await cb(self.run_command(command))

    def get_current_directory(self):
        return self.current_directory

async def send_long_message(message, string):
    if len(string) < 6000:
        for i in range(0, len(string), 2000):
            await message.reply(string[i:i+2000])
            await asyncio.sleep(0.2)
    else:
        with open("temp/log.txt", "w") as f:
            f.write(string)
        await message.reply(files=[discord.File("temp/log.txt")])
    return


# Function to download the file using aiohttp
async def download_file(url, destination):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # Check if the response is valid
            if response.status == 200:
                with open(destination, 'wb') as file:
                    # Write the file content to the destination
                    file.write(await response.read())
            else:
                print(f"Failed to download {url}. Status: {response.status}")
                
async def download_from_discord(terminal_emulator, message, arguments=""):
    if message.attachments:
        for attachment in message.attachments:
            # Get the URL of the attachment
            attachment_url = attachment.url
            # Define the filename (save it in the current directory or specify a path)
            filename = attachment.filename
            
            save_directory = terminal_emulator.get_current_directory()
            # Ensure the save directory exists
            os.makedirs(save_directory, exist_ok=True)

            # Download the file
            await download_file(attachment_url, os.path.join(save_directory, filename))

            await message.reply(f"Downloaded {filename} from {attachment_url} to ${os.path.join(save_directory, filename)}")

async def upload_to_discord(terminal_emulator, message, arguments=""):
    # Get the current directory from the terminal emulator
    current_directory = terminal_emulator.get_current_directory()
    
    # Build the full file path (combining the current directory with the arguments)
    file_path = os.path.join(current_directory, " ".join(arguments))

    # Check if the file exists
    if not os.path.exists(file_path):
        # If the file doesn't exist, send a message informing the user
        await message.reply(f"Error: The file '{arguments}' does not exist in the current directory.")
        return

    # If the file exists, send the file
    try:
        await message.reply(files=[discord.File(file_path)])
    except discord.DiscordException as e:
        # Handle any errors during the upload process (e.g., size limits, invalid file types)
        await message.reply(f"Error: Unable to upload the file. {str(e)}")
