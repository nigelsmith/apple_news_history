# Help Cal with research project

This is a quick script adapted from https://gist.github.com/RhetTbull/06617e33fe8645f75260311ab582fb6d to help Cal with his research project!

## Instructions

After you've cloned the repo locally run:

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python extract_apple_news_history.py` or
4a. `./extract_apple_news_history.py`

This will output JSON to standard output so you probably want instead to do

`./extract_apple_news_history.py > articles_history.json`

Running this again will wipe existing entries - so maybe name the file per person.

You will have to grant the terminal full disk access in modern versions of MacOS to access the Apple News container.