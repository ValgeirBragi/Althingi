# Imports
import requests as req
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np

def session_scrape(session_num, df):
    # Create an url and a requests url from session_num
    session_url = "https://www.althingi.is/thingstorf/thingmalalistar-eftir-thingum/lagafrumvorp/?lthing=" + str(session_num)
    url = req.get(session_url)

    # Limit to relevant text
    session_text = BeautifulSoup(url.content, "html.parser")
    body = session_text.find('tbody')
    session_bills = body.find_all('tr')
    
    # Loop gathering information for every bill in the session
    for bill in session_bills:
        bill_info = bill.find_all('td')

        bill_dict = {} # Empty dict to append to the DataFrame at the end of the loop
        bill_dict['bill_num'] = bill_info[0].text
        bill_dict['bill_date'] = bill_info[1].text
        bill_dict['bill_title'] = bill_info[2].text
        bill_dict['bill_link'] = "https://www.althingi.is" + re.search(r'(?<=a href=")[\s\S][^"]+', str(bill_info[2]))[0]
        if re.search('title=', str(bill_info[3])):
            bill_dict['bill_reader'] = re.search(r'(?<=title=")[\w\s]+', str(bill_info[3]))[0]
            bill_dict['reader_minister'] = bill_info[3].text
        else:
            bill_dict['bill_reader'] = bill_info[3].text
            bill_dict['reader_minister'] = 0
        bill_dict['reader_link'] = re.search(r'(?<=a href=")[\s\S][^"]+', str(bill_info[3]))[0]
        
        # Append data to the DataFrame
        df = pd.concat([df, pd.DataFrame([bill_dict])])
    # Return the changed DataFrame
    return df