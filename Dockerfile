FROM python:alpine

WORKDIR /opt/Meowth

RUN apk add git gcc libc-dev
RUN python -V
RUN pip install "requests>=2.18.4" "hastebin.py>=0.2" "python-dateutil>=2.6.1" "fuzzywuzzy>=0.15.1" "dateparser>=0.6.0" "python-Levenshtein"
RUN pip install -U git+https://github.com/Rapptz/discord.py@rewrite

CMD [ "python3", "launcher.py", "-r" ]