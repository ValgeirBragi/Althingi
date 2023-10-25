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

# Scrapes the page of the bill, should later only be used inside a bigger function in this script
def bill_scrape(bill_url, three_debates_only = False, debate_text = False):

    #IMPORTANT: Sometimes there's an extra table for committee discussions. I'll have to filter them out or create a seperate clause

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

    # If page_tables is an odd number, then the third table is a committee table, move it from the list
    if len(page_tables) % 2 != 0:
        committee_table = page_tables.pop(3)

    # Function that goes through a debate table and collects relevant data
    # Note: Element [1] is a link to the day's meeting, didn't feel necessary to include
    # Note: Outside the table, the head of the committee the bill goes to is mentioned, could be worth to scrape in later versions
    def debate_table_scrape(prefix, table):
        blocks = table.find_all('td')
        row_count = int(len(blocks)/4) # Each row has four columns
        for i in range(0, row_count):
            # Add an affix if there's a continued debate
            if i > 0:
                affix = '_' + str(i+1)
            else:
                affix = ''
            bill_dict['{}_debate_date{}'.format(prefix, affix)]      = blocks[0+i*4].text
            bill_dict['{}_debate_timestamp{}'.format(prefix, affix)] = blocks[2+i*4].text[:-8]
            bill_dict['{}_debate_link{}'.format(prefix, affix)]      = blocks[2+i*4].find('a')['href']
            try: # There should only be one vote per debate
                bill_dict['{}_debate_vote_link'.format(prefix)] = blocks[3+i*4].find('a')['href']
            except:
                pass
    
    # Scrape the debate tables
    debate_table_scrape('first', page_tables[1])
    debate_table_scrape('second', page_tables[3])
    debate_table_scrape('third', page_tables[4])
    
    # TODO: Collect final bill
    # TODO: Collect text of debates

    return bill_dict

def debate_scrape(debate_url):
    url             = req.get(debate_url)
    debates_soup    = BeautifulSoup(url.content, "html.parser")
    body            = debates_soup.find('yf')
    links           = body.find_all('a')

    # All speeches are bolded, so that's how I'll filter out the other links (which are unrelevant/scraped already)
    debate_links = []
    for link in links:
        if re.search(r'<b>', str(link)):
            debate_links.append(link)
    
    # Empty dictionary to keep our information in
    debate_dict = {}
    for debate in debate_links:
        link    = 'https://' + re.search(r'(?<=//).+(?=")', str(debate)).group(0)
        key     = re.search(r'rad\w+', link).group(0)
        speaker = re.search(r'(?<=<b>)[^<]+', str(debate)).group(0)
        
        # Scraping text
        url = req.get(link)
        debate_soup     = BeautifulSoup(url.content, "html.parser")
        time            = debate_soup.find(class_ = 'main-timi').text
        debate_strings  = debate_soup.find('div', {'id': 'raeda_efni'})
        debate_strings  = debate_strings.find_all(class_ = 'ind')

        # Turning the debate_strings into a single string variable
        debate_text = ''
        for line in debate_strings:
            debate_text = debate_text + re.search(r'(?<=\>).+(?=<)', str(line)).group(0) + ' '
        # Some strings had space at the end, some didn't. So adding a space after every string and removing all double strings
        debate_text = re.sub(' +', ' ', debate_text)

        # Appending a nested dictionary of the speeches in the debate_dict
        debate_dict[key] = {
            'link'          : link,
            'speaker'       : speaker,
            'text'          : debate_text,
            'time_start'    : re.search(r'(?<=\[).+(?=\])', time).group(0) # Removing brackets with regex
        }
    
    return debate_dict


# Testing samples:

# Collecting all bills from a yearly session
# session_scrape(151, session_151)

# Collecting bill information
# bill_scrape('https://www.althingi.is/thingstorf/thingmalalistar-eftir-thingum/ferill/151/443/?ltg=151&mnr=443', 
#             three_debates_only = True)

# Collecting information on a single debate
# debate_scrape('https://www.althingi.is/altext/151/01/l21164717.sgml')
