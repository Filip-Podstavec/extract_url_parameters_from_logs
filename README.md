# Extract URL parameters from access log
This Python script read access-log file, and extract from it the most crawled URL parameters extracted by specific bot.

If you don't have any access log find some on Google:
https://www.google.com/search?q=filetype%3Alog+inurl%3Aaccess

## Example output
Spreadsheet: https://docs.google.com/spreadsheets/d/1ExndYXQ54QJH0SrEw-RIPGHb7yEECBjLTHgxwRuP52k/edit?usp=sharing

## Setup
`pip install -r requirements.txt`

## Example usage

Analyze access log and export output to parameters.csv file:

`python logparser.py C:/my_folder/access-log.log`

Analyze access log and export output to custom CSV file:

`python logparser.py C:/my_folder/access-log.log --output=example.csv` 

