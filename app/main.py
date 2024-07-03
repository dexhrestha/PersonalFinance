import streamlit as st

st.set_page_config(page_title="Personal Finance Dashboard",page_icon=":materia;/edit:")

upload_page = st.Page("pages/upload.py",title = "Upload Statements",icon=":material/add_circle:")
home_page = st.Page("pages/home.py",title="Personal Finance Dashboard",icon="🔍")
edit_page = st.Page("pages/edit.py",title="Edit Statements",icon=":material/edit:")

pg = st.navigation([
    home_page,
    upload_page,
    edit_page,
])

pg.run()