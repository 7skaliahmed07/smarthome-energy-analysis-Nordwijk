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
