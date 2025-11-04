from sqlalchemy import create_engine

# --- Database Configuration ---
# You can define the connection string as a constant
DB_CONNECTION_STRING = "mysql+pymysql://franquito:edwin@localhost:3306/inegi"
ASSISTANT_CONNECTION_STRING = "mysql+pymysql://assistant:edwin@localhost:3306/inegi"
GEMINI_API_KEY = "AIzaSyAFH3PjHBDT1zltBDtjH0nSZgOWdckrXDc"


# You can define the engine object itself as a constant
# We create it here so it's initialized only once when the module is imported.
# Note: setting echo=True is often helpful for debugging SQL
ENGINE = create_engine(DB_CONNECTION_STRING, echo=True)