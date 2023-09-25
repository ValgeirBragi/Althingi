# Imports
import requests as req
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np

# TODO: Add a function that incorporates all of these

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
        bill_info = bill.find_all('td') # Simplifying the text into smaller chunks

        bill_dict = {} # Empty dict to append to the DataFrame at the end of the loop
        bill_dict['bill_num']   = bill_info[0].text
        bill_dict['bill_date']  = bill_info[1].text
        bill_dict['bill_title'] = bill_info[2].text
        bill_dict['bill_link']  = "https://www.althingi.is" + re.search(r'(?<=a href=")[\s\S][^"]+', str(bill_info[2]))[0]
        if re.search('title=', str(bill_info[3])):
            bill_dict['bill_reader'] = re.search(r'(?<=title=")[\w\s]+', str(bill_info[3]))[0]
            bill_dict['reader_minister'] = bill_info[3].text
        else:
            bill_dict['bill_reader']        = bill_info[3].text
            bill_dict['reader_minister']    = 0
        bill_dict['reader_link'] = re.search(r'(?<=a href=")[\s\S][^"]+', str(bill_info[3]))[0]
        
        # Create a unique id for the bill (Format: bill_num + _year)
        bill_dict['bill_id'] = str(bill_dict['bill_num']) + str(bill_dict['bill_date'][-4:])
        # Append data to the DataFrame
        df = pd.concat([df, pd.DataFrame([bill_dict])])

    # Return the changed DataFrame
    return df

def bill_scrape(bill_url, three_debates_only = False, debate_text = False):
    url             = req.get(bill_url)
    bill_soup       = BeautifulSoup(url.content, "html.parser")
    debate_count    = bill_soup.find_all(class_ = 'clearboth')
    page_tables     = bill_soup.find_all('table')

    # Empty dict for the bill
    bill_dict = {}

    # Counting number of debates and filtering out debates that didn't have all three debates if enabled
    bill_dict['debate_count'] = len(debate_count)
    if three_debates_only == True:
        if len(debate_count) < 3:
            return False            # Returns false, when calling the function you should use an if statement to skip the bills
        
    if len(debate_count) > 3: # There shouldn't be more than 3 debates, but I want to be warned in case it happens
        print('More than 3 debates in {}, something must have gone wrong'.format(bill_url))

    # Only new information on first table is the link to the proposed bill
    bill_dict['bill_proposal_link'] = page_tables[0].find('a')['href']
    
    # Debate 1
    # Current version only works if there is one debate
    # Note: Element [1] is a link to the day's meeting, didn't feel necessary to include
    # Note: Outside the table, the head of the committee the bill goes to is mentioned, could be worth to scrape in later versions
    blocks = page_tables[1].find_all('td')
    bill_dict['first_debate_date']      = blocks[0].text
    bill_dict['first_debate_timestamp'] = blocks[2].text[:-8]
    bill_dict['first_debate_link']      = blocks[2].find('a')['href']
    bill_dict['first_debate_vote_link'] = blocks[3].find('a')['href']
    print(len(blocks))
    def debate_table_scrape(prefix, table):
        blocks = table.find_all('td')
        row_count = len(blocks)/4 # Checks if sessions are split/each row has four columns
        for i in range(1)
        #while(block_count > 0): # Turning the code into a while loop once it's tested


            #block_count += -4

    # for table in page_tables:
    #     links = table.find_all('a')
    #     print(len(links))
    #     #print(links[0].get("href"))

    #print(page_tables[0])
    # Collect data on bill

    # Collect text of debates


# Temporary for testing purposes
bill_scrape('https://www.althingi.is/thingstorf/thingmalalistar-eftir-thingum/ferill/151/443/?ltg=151&mnr=443', 
            three_debates_only = False)