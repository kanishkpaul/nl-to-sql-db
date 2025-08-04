import streamlit as st
import mysql.connector
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# MySQL DB connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="kanishk",
    database="testdb"
)
cursor = db.cursor()

# Groq: Convert NL to SQL
def get_sql_from_nl(nl_query):
    prompt = f"""You are a SQL expert. Convert the following natural language request into a valid MySQL SQL query:\n\n"{nl_query}"\n\nOnly output the SQL query, nothing else."""
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
    )
    
    sql = response.json()["choices"][0]["message"]["content"]
    return sql.strip("```sql\n").strip("```").strip()

# UI Layout
st.set_page_config(page_title="NL to SQL", layout="centered")
st.title("🧠 Natural Language to SQL")
st.markdown("Type a question or command about your database in natural language.")

# User input
nl_input = st.text_area("Your Natural Language Query", height=100)

if st.button("Run Query") and nl_input:
    try:
        with st.spinner("Thinking..."):
            sql_query = get_sql_from_nl(nl_input)
            st.code(sql_query, language="sql")

            cursor.execute(sql_query)

            if sql_query.strip().lower().startswith("select"):
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                st.success("Query executed successfully!")
                st.dataframe(result, use_container_width=True)
            else:
                db.commit()
                st.success("Query executed and committed.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
