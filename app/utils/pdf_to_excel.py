import logging
import os
import io
import zipfile
from datetime import datetime
import pandas as pd
import numpy as np

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_renditions_element_type import \
    ExtractRenditionsElementType
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

def remove_unwanted_char(tables,columns_only=True):
    tables.columns = [col.replace('_x000D_','').strip() for col in tables.columns]
    if not columns_only:
        for col in tables.columns:
            tables[col] = tables[col].astype(str).str.replace(' _x000D_','').str.strip()
    return tables

def extract_tables_from_pdf_lloyds(src,output_path):
    try:
        file = open(src,'rb')
        input_stream = file.read()
        file.close()

        credentials = ServicePrincipalCredentials(
        client_id="6081dd7f1db542f69745187209ff86eb",
        client_secret="p8e-GZTDGyr9DJh5VqQv0w8_M-YTjwRSJLYT"
        )

        pdf_services = PDFServices(credentials=credentials)
        input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)
        extract_pdf_params = ExtractPDFParams(
                    elements_to_extract=[ExtractElementType.TEXT, ExtractElementType.TABLES],
                    elements_to_extract_renditions=[ExtractRenditionsElementType.TABLES],
                    add_char_info=True,
                )

                # Creates a new job instance
        extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)

        # Submit the job and gets the job result
        location = pdf_services.submit(extract_pdf_job)
        pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

        # Get content from the resulting asset(s)
        result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
        stream_asset: StreamAsset = pdf_services.get_content(result_asset)

        # Creates an output stream and copy stream asset's content to it
        zip_bytes = io.BytesIO(stream_asset.get_input_stream())
        with zipfile.ZipFile(zip_bytes,'r') as zip_ref:
            # zip_ref.printdir()
            # zip_ref.extractall()
            tables = []
            for file_name in zip_ref.namelist():
                if file_name.endswith('.xlsx'):
                    with zip_ref.open(file_name) as file:
                        tables.append(pd.read_excel(file))

        for table in tables:
            table = remove_unwanted_char(table)

        with_dates = [i for i,table  in enumerate(tables) if table.columns[0]=='Date']
        table = pd.concat([tables[i] for i in with_dates]).reset_index(drop=True)
        
        # clean data
        table_clean = remove_unwanted_char(table,False)
        # ffill
        table_clean['Date'] = table_clean['Date'].ffill()
        
        # remove extra text
        table_clean['Date'] = table_clean['Date'].str.split(' ').apply(lambda x:" ".join(x[:3]))

        table_clean['Date']=pd.to_datetime(table_clean['Date'],format="%d %b %y",errors='coerce')

        table_clean['Money In (£)'] = table_clean['Money In (£)'].str.replace(',','').astype(float) 
        table_clean['Money Out (£)']  = table_clean['Money Out (£)'].str.replace(',','').astype(float)
        table_clean['Balance (£)']   = table_clean['Balance (£)'].str.replace(',','').astype(float)

        return table_clean.to_excel(output_path,index=False)

    except (ServiceApiException, ServiceUsageException, SdkException) as e:
        logging.exception(f'Exception encountered while executing operation: {e}')

def extract_tables_from_pdf_natwest(src,output_path):
    try:
        file = open(src,'rb')
        input_stream = file.read()
        file.close()

        credentials = ServicePrincipalCredentials(
        client_id="6081dd7f1db542f69745187209ff86eb",
        client_secret="p8e-GZTDGyr9DJh5VqQv0w8_M-YTjwRSJLYT"
        )

        pdf_services = PDFServices(credentials=credentials)
        input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)
        extract_pdf_params = ExtractPDFParams(
                    elements_to_extract=[ExtractElementType.TEXT, ExtractElementType.TABLES],
                    elements_to_extract_renditions=[ExtractRenditionsElementType.TABLES],
                    add_char_info=True,
                )

                # Creates a new job instance
        extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)

        # Submit the job and gets the job result
        location = pdf_services.submit(extract_pdf_job)
        pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

        # Get content from the resulting asset(s)
        result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
        stream_asset: StreamAsset = pdf_services.get_content(result_asset)

        # Creates an output stream and copy stream asset's content to it
        zip_bytes = io.BytesIO(stream_asset.get_input_stream())
        with zipfile.ZipFile(zip_bytes,'r') as zip_ref:
            # zip_ref.printdir()
            # zip_ref.extractall()
            tables = []
            for file_name in zip_ref.namelist():
                if file_name.endswith('.xlsx'):
                    with zip_ref.open(file_name) as file:
                        tables.append(pd.read_excel(file))

        for table in tables:
            table = remove_unwanted_char(table)

        with_dates = [table for i,table  in enumerate(tables) if table.columns[0]=='Date']
        for table in with_dates:
            if len(table.columns)==5:
                table.columns = ["Date","Description","Paid In(£)","Withdrawn(£)","Balance(£)"]
        if len(with_dates)>1:
            table = pd.concat(with_dates).reset_index(drop=True)
        else:
            table = with_dates[0]
        # ffill
        table['Date'] = table['Date'].ffill()
        # clean data
        table_clean = remove_unwanted_char(table,False)

        has_year= table_clean['Date'].apply(lambda x:x[-4:].isdigit())
        # add year
        year = os.path.basename(src).split('.')[0].split('_')[-1]
        
        table_clean.loc[~has_year,'Date'] = table_clean[~has_year]['Date']+f' {year}'

        table_clean['Datestring'] = table_clean['Date']
        table_clean['Date']=pd.to_datetime(table_clean['Date'],format="%d %b %Y",errors='coerce')


        error_index = table_clean[table_clean['Date'].isna()].index
        if len(error_index):
            table_clean.loc[error_index,'Balance(£)'] = table_clean['Withdrawn(£)']  
            table_clean.loc[error_index,'Withdrawn(£)'] = table_clean['Paid In(£)']
            table_clean.loc[error_index,'Paid In(£)'] = table_clean['Description']
            table_clean.loc[error_index,'Description'] = table_clean['Datestring']
            table_clean['Date'] = table_clean['Date'].ffill()
            table_clean.drop(columns=['Datestring'])

        if 'Paid In(£)' not in table_clean.columns:
            table_clean['Paid In(£)'] = np.nan
            table_clean['Withdrawn(£)'] = table_clean['Paid In(£) Withdrawn(£)']
            table_clean = table_clean.drop(columns=['Paid In(£) Withdrawn(£)'])
        if 'Withdrawn(£)' not in table_clean.columns:
            table_clean['Withdrawn(£)'] = np.nan
        if 'Balance(£)' not in table_clean.columns:
            table_clean['Balance(£)'] = np.nan

        table_clean['Paid In(£)'] = table_clean['Paid In(£)'].astype(str).str.replace(',','').str.replace(' OD','').str.strip(' ').astype(float) 
        table_clean['Withdrawn(£)']   = table_clean['Withdrawn(£)'].astype(str).str.replace(',','').str.replace(' OD','').str.strip(' ').astype(float)
        table_clean['Balance(£)']   = table_clean['Balance(£)'].astype(str).str.replace(',','').str.replace(' OD','').str.strip(' ').astype(float)
        table_clean = table_clean.drop(columns=['Datestring'])
        
        # table_clean.to_excel(output_file_path,index=False)
        return table_clean.to_excel(output_path,index=False)
    
    except (ServiceApiException, ServiceUsageException, SdkException) as e:
        logging.exception(f'Exception encountered while executing operation: {e}')