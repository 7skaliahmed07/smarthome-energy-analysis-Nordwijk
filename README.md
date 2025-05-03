# Smart Home Energy Analytics  

Process and analyze 32 months of IoT data from a Dutch smart home to uncover energy usage patterns and device behavior.  

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
4. smartthings.py file extract devices from csv and add all csv's in bulk to the database.