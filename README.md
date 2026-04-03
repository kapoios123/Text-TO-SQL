# AI Data Assistant (Text-to-SQL)

An intelligent data assistant that allows users to query their databases or Excel/CSV files using natural language. The application translates plain text questions into executable SQL queries and visualizes the results instantly.

## Features
* Multi-Source Support: Connect to SQLite (.db), MySQL, or upload Excel/CSV files.
* Natural Language Processing: Powered by Llama 3 (via Groq API) to convert user questions into SQL.
* Security Shield: A built-in security layer ensures only SELECT statements are executed, protecting data from unauthorized modification or deletion.
* Automated Schema Mapping: Automatically detects table structures and column names to provide context to the AI.

## Technologies
* Streamlit: Web interface and deployment.
* Groq Cloud SDK: LLM integration for query generation.
* Pandas & SQLAlchemy: Data processing and database communication.

## Installation
1. Clone the repository.
2. Install dependencies: pip install -r requirements.txt
3. Run the application: streamlit run test_groq.py
