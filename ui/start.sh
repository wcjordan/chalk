#!/bin/bash
set -ex

npx expo login --non-interactive -u $EXPO_USERNAME
cd js; yarn web
