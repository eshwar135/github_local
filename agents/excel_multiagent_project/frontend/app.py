import streamlit as st
import requests

st.title("Excel Multi-Agent Query System")

uploaded_file = st.file_uploader("Upload Excel file", type=["xls", "xlsx"])
if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    resp = requests.post("http://localhost:8000/upload_excel", files=files)
    st.write(resp.json())

query = st.text_input("Enter query")
if st.button("Run Query") and query:
    data = {"query": query}
    resp = requests.post("http://localhost:8000/query", data=data)
    if resp.status_code == 200:
        st.json(resp.json())
    else:
        st.error(f"Error: {resp.text}")
