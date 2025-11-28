# Smart Home Energy Analytics  

Process and analyze 32 months of IoT data from a Dutch smart home to uncover energy usage patterns and device behavior.  

![image_alt](https://github.com/7skaliahmed07/smarthome-energy-analysis-Nordwijk/blob/a9dad3c516209428eb71074f8651f3d2b35a307d/image.jpg)

# 📌 Overview  
- *Data Sources*: SmartThings (30+ devices), P1e/P1g (energy meters), OpenWeatherMap.  
- *Scope*: 2,000+ daily messages over 32 months (temperature, device states, energy use).  
- *Goal*: Build a relational database pipeline and derive actionable insights.  

# 🛠️ Tech Stack  
- *Database*: Sqlite.  
- *ETL*: Python (Pandas, SQLAlchemy).  
- *Visualization*: Grafana/Plotly/Matplotlib/Seaborn.  

# 📂 Repository Structure  
├── /data/raw/           # Original datasets (JSON, CSV)  
├── /etl/                # Scripts for data cleaning/loading  
├── /analysis/           # Jupyter notebooks for exploration  
├── /docs/               # Schema diagrams, reports  
└── README.md  


--------------------------------------------------------------------------------------------------------------------------------------------

# File Handling
1. The gz-to-original.py file will handle all .gz files and convert them back to their original file extensions. 

# Database Initialization
To create a clean SQLite database (`smarthome.db`):
1. Run `python create_db.py`.
2. Verify tables in DB Browser for SQLite (`devices`, `smartthings_messages`, `electricity_usage`, `gas_usage`, `weather`).
3. Home_messages.py contains three parts which are database schema, connection and methods of tables.
4. Extract all CSV data from smartthings.py, p1e, and p1g files, and perform bulk creation in the database.
5. Change the timestamp to Integer UTC (Compact,Fast, UTC based)

6. # Data Validation and Cleaning
- *Validation*:
  - Removed rows with `NULL` or invalid values (e.g., negative usage, out-of-range weather data).
  - Verified no true duplicates in any table (based on unique constraints).
- *Time Range Alignment*:
  - Trimmed all tables to match the range: 2022-06-01 to 2025-01-31 (epoch 1654041600 to 1735622400).
  - *SmartThings Messages*: Starts late at 2022-10-09 due to dataset limitations; documented as a constraint.
  - *Weather*: Missing the last hour (2025-01-31 00:00:00 UTC); deemed acceptable due to minimal impact.
- *Additional Checks*:
  - Confirmed foreign key consistency in `smartthings_messages`.
  - Checked for gaps in weather data (noted 1-hour gap at the end).
  - Rebuilt `smartthings_messages` table to enforce unique index on `(device_id, epoch, capability, attribute)`.

7. # Data Analysis and Aggregation
- *Objective*: Analyze and aggregate data for insights.
- *Analyses*:
  - *Usage Distribution*: Computed hourly averages of electricity (t1_kwh, t2_kwh) and gas (gas_m3) usage, saved to `hourly_usage.csv`.
  - *Occupancy Detection*: Identified unoccupied intervals based on low SmartThings activity (e.g., switch/motion), saved to `unoccupied_intervals.csv`.

8. # Visualization and Reporting
- **Objective**: Visualize data and compile reports using Jupyter notebooks.
- **Notebooks**:
  - *usage_distribution.ipynb*: Visualizes the hourly distribution of electricity and gas usage.
    - Plot: Line plot of `t1_kwh`, `t2_kwh`, and `gas_m3` vs. hour.
    - Findings: Evening peaks (hour 21) in usage, early morning lows (hours 0–5).
  - *occupancy_analysis.ipynb*: Analyzes unoccupied intervals based on SmartThings activity gaps.
    - Plot: Histogram of gap durations (in hours).
    - Findings: 2338 intervals, many overnight or during the day (e.g., work hours).
  - *weather_correlation.ipynb*: Correlates daily temperature with gas usage.
    - Plot: Scatter plot of temperature vs. gas usage.
    - Findings: Negative correlation expected (higher gas usage on colder days).


