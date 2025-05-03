Creating a New File : 
 - fsutil file createnew newfile.md 0

Push Bulk Data into the Database & Single File : 
 - python p1g.py -d sqlite:///smarthome.db data/P1g/gz-to-csv/*.csv
 - python smartthings.py -d sqlite:///smarthome.db data/smartthings/gz-to-csv/smartthings.20230107.tsv

Create a Empty Database:
- python create_db.py

Creating a Backup file
- Copy-Item smarthome.db smarthome_backup_datetime.db

Env Activate
- nordwijk-env\Scripts\activate