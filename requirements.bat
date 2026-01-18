@echo off

python -m pip install --upgrade pip

pip install requests beautifulsoup4 playwright transformers torch urllib3

python -m playwright install
