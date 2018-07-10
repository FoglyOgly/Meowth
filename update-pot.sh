#!/bin/bash

pygettext -d meowth -p locale meowth

for lang in it en fr
do
    msgmerge -U locale/$lang/LC_MESSAGES/meowth.po locale/meowth.pot
    msgfmt -o locale/$lang/LC_MESSAGES/meowth.mo locale/$lang/LC_MESSAGES/meowth.po
done


