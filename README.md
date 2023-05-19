### FreshBot

- Current implementation is in FreshBot.py and is a work in progress.  
- User commands are in commands.py.  
- ChatGPT in chatGPT.py is a chatBot that is in the works.  
- music.py is sourced and is currently not my work. Its used for learning purposes and will be modified.  

## Key Features
- All 'stock-trading' channels that the bot has access to will be updated with the current price of the stock set.

## Updates
- Code has been converted from using discord.client to discord.bot for better functionality.  
- responses.py is now redundant, but there for legacy reasons.  

## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/).

2. Clone this repository.

3. Navigate into the project directory:

   ```bash
   $ cd FRESHBOT
   ```

4. Create a new virtual environment:

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

7. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file.

8. Run the app using python or python3 depending on your system:

   ```bash
   $ python FreshBot.py
   ```