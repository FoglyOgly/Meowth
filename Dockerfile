FROM python:3.6-alpine

ENV MEOWTH_INSTALLDIR="/opt/meowth"
ENV MEOWTH_CONFIG=$MEOWTH_INSTALLDIR/config/config.json

RUN addgroup -g 1000 meowth && adduser -u 1000 -S -G meowth meowth

RUN mkdir -p $MEOWTH_INSTALLDIR
COPY requirements.txt  $MEOWTH_INSTALLDIR/requirements.txt 

RUN apk add --update build-base git && \
    python3 -m pip install -r $MEOWTH_INSTALLDIR/requirements.txt 

RUN python3 -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite && \
    apk del build-base git make gcc g++

COPY ./pokegifs $MEOWTH_INSTALLDIR/pokegifs
COPY ./meowth $MEOWTH_INSTALLDIR/meowth
COPY ./locale $MEOWTH_INSTALLDIR/locale
COPY ./images $MEOWTH_INSTALLDIR/images
COPY ./data $MEOWTH_INSTALLDIR/data
COPY ./config $MEOWTH_INSTALLDIR/config
COPY launcher.py LICENSE emoji.rar $MEOWTH_INSTALLDIR/


RUN mkdir $MEOWTH_INSTALLDIR/logs && \
    chown meowth:meowth -R $MEOWTH_INSTALLDIR/config $MEOWTH_INSTALLDIR/logs

RUN apk del build-base git make gcc g++ && \
    rm -rf /var/cache/apk/* /root/* /root/.cache


USER meowth

VOLUME [ "$MEOWTH_INSTALLDIR/logs","$MEOWTH_INSTALLDIR/config" ]

WORKDIR $MEOWTH_INSTALLDIR

ENTRYPOINT ["python3", "launcher.py"]

