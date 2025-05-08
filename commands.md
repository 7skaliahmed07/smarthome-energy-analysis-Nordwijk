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


Cleaning Database Queries:
-- SmartThings Messages
SELECT * FROM smartthings_messages WHERE value IS NULL OR value = '' OR epoch IS NULL;
SELECT device_id, COUNT(*) as count FROM smartthings_messages GROUP BY device_id HAVING count = 0;

-- Electricity Usage
SELECT * FROM electricity_usage WHERE t1_kwh IS NULL OR t2_kwh IS NULL OR epoch IS NULL OR t1_kwh < 0 OR t2_kwh < 0;

-- Gas Usage
SELECT * FROM gas_usage WHERE gas_m3 IS NULL OR epoch IS NULL OR gas_m3 < 0;

-- Weather
SELECT * FROM weather WHERE temperature IS NULL OR humidity IS NULL OR precipitation IS NULL OR wind_speed IS NULL OR pressure IS NULL
OR temperature < -40 OR temperature > 50 OR humidity < 0 OR humidity > 100 OR precipitation < 0 OR wind_speed < 0 OR pressure < 900 OR pressure > 1100;

