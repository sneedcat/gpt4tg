# gpt4tg
This is a fork of [Telegram-Chatbot-Gpt4Free](https://github.com/HexyeDEV/Telegram-Chatbot-Gpt4Free.git), with a few changes.

- Backported some changes from g4f
- Removed plugins
- Added tones
- Added allowed ids

If you want to support the original creator, then go donate to `HexyeDEV`.

# Installation
Clone the repo

```git clone https://github.com/sneedcat/gpt4tg```

After that go to the cloned repo directory.

Create an .env file with:

API_ID is your api id from https://my.telegram.org

API_HASH is your api hash from https://my.telegram.org

BOT_TOKEN is your bot token from Bot Father

Install all the packages running ```pip install -r requirements.txt```(may change based on your python version, settings and os.)

Now run main.py with ```python3 main.py```(may change based on your python version, settings and os.)

Enjoy!

Commands:

- /help - see a command list

- /newrole <Role Name> <Role Info> - create a new role

- /roles - list all the roles

- /role <Role Name> - enable a role

- /tone <Tone Name> (can be creative, precise or balanced)

- /gpt - Retrieves the response from bing gpt4

# Running the Application in a Docker Container

1. Build the Docker image using the command `docker build -t telegram-chatbot .`
2. Run the Docker container using the command `docker run -p 80:80 telegram-chatbot`
3. Alternatively, use Docker Compose to build and run the Docker container using the command `docker-compose up`
