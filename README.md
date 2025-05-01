# Smart Home Energy Analytics  

Process and analyze 32 months of IoT data from a Dutch smart home to uncover energy usage patterns and device behavior.  

# 📌 Overview  
- *Data Sources*: SmartThings (30+ devices), P1e/P1g (energy meters), OpenWeatherMap.  
- *Scope*: 2,000+ daily messages over 32 months (temperature, device states, energy use).  
- *Goal*: Build a relational database pipeline and derive actionable insights.  

# 🛠️ Tech Stack  
- *Database*: PostgreSQL (+ TimescaleDB for time-series).  
- *ETL*: Python (Pandas, SQLAlchemy).  
- *Visualization*: Grafana/Plotly.  

# 📂 Repository Structure  
├── /data/raw/           # Original datasets (JSON, CSV)  
├── /etl/                # Scripts for data cleaning/loading  
├── /analysis/           # Jupyter notebooks for exploration  
├── /docs/               # Schema diagrams, reports  
└── README.md  


--------------------------------------------------------------------------------------------------------------------------------------------
## Database Setup and Testing
The database is implemented in `home_messages_db.py` using SQLite. To test:
1. Run `python test_db.py` to initialize `myhome.db`, insert sample data, and query tables.
2. Open `myhome.db` in DB Browser for SQLite to view tables (`devices`, `smartthings_messages`, `electricity_usage`, `gas_usage`, `weather`) and data.