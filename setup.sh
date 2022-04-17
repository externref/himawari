python3 -m pip install virtualenv
python3 -m virtualenv env
source env/bin/activate
python3 -m pip install lightbulb-ext-filament aiosqlite python-dotenv groundwork-sphinx-theme sphinx myst-parser
python3 -m pip install -U hikari hikari-lightbulb
python3 .
