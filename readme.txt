Inform Data Web Scraping Take Home Assessment
Oct 2024
Riley Martin

README

To run the app use the -h signature as described below.

usage: informDataWebScraper.py [-h] [-l LOG] [-f FILE_PATH]

Inform Data Web Scraper

optional arguments:
  -h, --help            show this help message and exit
  -l LOG, --log LOG     Set the logging level (DEBUG, INFO, WARNING, ERROR,
                        CRITICAL)
  -f FILE_PATH, --file_path FILE_PATH
                        Set the name of the .jsonl file, defaults to data.jsonl

Example:
python informDataWebScraper.py  -l DEBUG -f another_file.jsonl
