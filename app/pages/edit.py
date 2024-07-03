import streamlit as st
import pandas as pd
from utils.drive_functions import Drive
import os

# Initialize the Drive client
g_client = Drive(token_path='credentials/g_token.pickle', cred_path='credentials/gdrive-cred.json')

# Constants
OPTIONS = [
    'Bills', 'Rent', 'Eating out', 'Shopping', 'Transport', 'Groceries', 'Entertainment',
    'Health & Beauty', 'Home & Garden', 'Other', 'Uncategorized', 'Income', 'Transfers',
    'Investment', 'Savings', 'Loan', 'Study','Leisure'
]

# Streamlit app
def main():
    st.title("Edit Statements")

    bank = st.selectbox("Bank:", ["Lloyds", "Natwest"])

    if bank:
        enriched_folder = os.getenv(f"{bank.upper()}_ENRICHED_FOLDER_ID")
        staging_folder = os.getenv(f"{bank.upper()}_STAGING_FOLDER_ID")

        # Fetch files
        staging_files = g_client.get_files_from_folder(staging_folder)
        enriched_files = g_client.get_files_from_folder(enriched_folder)
        enriched_files = {v:k for k,v in enriched_files.items()}

        if staging_files:
            statement_id = st.selectbox("Select file", options=list(staging_files.keys()), format_func=lambda x: staging_files[x])

            if statement_id:
                process_statement(statement_id, staging_files, enriched_files, enriched_folder)

def process_statement(statement_id, staging_files, enriched_files, enriched_folder):
    filename = staging_files[statement_id]
    enriched_file = 'enriched_'+filename 
    if enriched_file in enriched_files.keys():
        statement_id = enriched_files[enriched_file]
        df = g_client.read_excel_file(statement_id)
    else:
        df = g_client.read_excel_file(statement_id)
        df = df.sort_values(by=['Date'])
        df['Category'] = ''
        df = df[list(df.columns[:2]) + ["Category"] + list(df.columns[2:-1])]

    with st.form(key="statement"):
        edited_df = st.data_editor(
            df,
            column_config={
                "Category": st.column_config.SelectboxColumn(
                    "Category", help="Category of transaction", width="small", options=OPTIONS, required=False),
                "Date": st.column_config.DateColumn(disabled=True),
                "Description": st.column_config.TextColumn(disabled=True),
                "Type": st.column_config.TextColumn(disabled=True),
                "Money In (£)": st.column_config.TextColumn(disabled=True),
                "Money Out (£)": st.column_config.TextColumn(disabled=True),
                "Balance (£)": st.column_config.TextColumn(disabled=True),
            },
            hide_index=True
        )
        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        save_and_upload_file(edited_df, filename, enriched_folder)

def save_and_upload_file(edited_df, filename, enriched_folder):
    save_path = os.path.join("enriched", f"enriched_{filename}")
    edited_df.to_excel(save_path, index=False)
    g_client.upload_to_drive(enriched_folder, save_path)
    st.success(f"File saved as {save_path}")

main()

# if __name__ == "__main__":
    # main()
