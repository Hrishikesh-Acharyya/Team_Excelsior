#!/usr/bin/env bash

# Ensure shell fails on errors
set -o errexit

# Install ffmpeg (needed for Whisper audio conversion)
apt-get update
apt-get install -y ffmpeg
