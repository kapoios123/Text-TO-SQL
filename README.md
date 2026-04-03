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


# How to use the App
You can share this link with your users: https://smart-ai-data-assistant.streamlit.app/

Step-by-Step Instructions:

# 1. Set up your API Key

Locate the "API Settings" section in the sidebar on the left.

Enter your Groq API Key. If a default key is already provided, you can proceed directly.

# 2. Connect your Data Source

Under "Configuration" in the sidebar, select your data type:

Excel/CSV: Upload your spreadsheet. The app will automatically read the columns.

SQLite: Upload your .db or .sqlite file.

MySQL: Enter your host, username, password, and database name to connect.

# 3. Verify the Data Structure

Once connected, click "See Database Structure" in the main window. This shows you exactly which tables and columns the AI can "see."

# 4. Ask a Question

Use the chat input box at the bottom of the screen.

Type your question in plain Greek or English.

Example: "What were the total sales for the Product 'Laptop' in the East region?"

Example: "Show me the top 5 customers by quantity."

# 5. Review and Results

The AI will generate the corresponding SQL query and display it for transparency.

If the query is safe, the app will execute it and display the resulting data table automatically.
