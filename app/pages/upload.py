import os
import streamlit as st
from utils.pdf_to_excel import extract_tables_from_pdf_lloyds,extract_tables_from_pdf_natwest
from utils.drive_functions import Drive
import pandas as pd

from dotenv import load_dotenv

load_dotenv()


st.title("Upload statements")

g_client = Drive(token_path='credentials/g_token.pickle',cred_path='credentials/gdrive-cred.json')



def main():
    bank = st.selectbox("Bank:",["Lloyds","Natwest"])
    raw_folder = os.getenv(f"{bank.upper()}_RAW_FOLDER_ID")
    staging_folder = os.getenv(f"{bank.upper()}_STAGING_FOLDER_ID")


    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Process the uploaded file if needed
        try :
            assert g_client.drive is not None
            st.write("File uploaded successfully!")
            # For demonstration, we'll just display the file name
            st.write(f"File name: {uploaded_file.name}")

            # You can save the file if needed
            upload_path=f"uploads/{uploaded_file.name}"
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # upload to drive
                g_client.upload_to_drive(raw_folder,upload_path)

        except Exception as e:
            print(e)

        try:
            output_path = "uploads/"+"".join(os.path.basename(upload_path).split('.')[:-1])+".xlsx"
            if bank=="Lloyds":
                extract_tables_from_pdf_lloyds(upload_path,output_path)
                g_client.upload_to_drive(staging_folder,output_path)
            elif bank=="Natwest":
                extract_tables_from_pdf_natwest(upload_path,output_path)
                g_client.upload_to_drive(staging_folder,output_path)
            st.write("File saved successfully!")
        except Exception as e :
            print(e)

        # st.table(pd.DataFrame({'Date':['1','2','3']}))


main()

# if __name__ == "__main__":
    # main()
    # print()