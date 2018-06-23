FROM python:3.6-alpine

ENV MEOWTH_INSTALLDIR="/opt/meowth"
ENV MEOWTH_CONFIG=$MEOWTH_INSTALLDIR/config.json

RUN addgroup -g 1000 meowth && adduser -u 1000 -S -G meowth meowth

RUN mkdir -p $MEOWTH_INSTALLDIR
COPY requirements.txt  $MEOWTH_INSTALLDIR/requirements.txt 

RUN apk add --update build-base git && \
    python3 -m pip install -r $MEOWTH_INSTALLDIR/requirements.txt 

RUN python3 -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite && \
    apk del build-base git make gcc g++

COPY . $MEOWTH_INSTALLDIR
RUN cp $MEOWTH_INSTALLDIR/config_blank.json $MEOWTH_CONFIG && \
    chown meowth:meowth -R $MEOWTH_INSTALLDIR

RUN apk del build-base git make gcc g++ && \
    rm -rf /var/cache/apk/* /root/* /root/.cache


USER meowth

WORKDIR $MEOWTH_INSTALLDIR

ENTRYPOINT ["python3", "launcher.py"]

