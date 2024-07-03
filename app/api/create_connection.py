from sqlalchemy import create_engine
import pandas as pd

# Database connection details
PROJECT_NAME = "personal_finance"
POSTGRES_DBNAME = "postgres"
POSTGRES_SCHEMA = "magic"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_HOST = "192.168.0.84"
POSTGRES_PORT = 5432

# Create a connection string
connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"

# Create an engine
engine = create_engine(connection_string)

# Define a query to load data
query = f"SELECT * FROM statements_raw.lloyds_raw"  # Replace 'your_table_name' with your actual table name

# Load data into a pandas DataFrame
df = pd.read_sql(query, engine)


