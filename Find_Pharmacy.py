#!/usr/bin/env python
# coding: utf-8

# In[1]:


from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
from selenium import webdriver
import pandas as pd
import time
import re


# In[8]:


# set driver
driver_path = 'chromedriver.exe'
driver = webdriver.Chrome(driver_path)
url = 'https://www.google.com/maps'
driver.get(url)

search_input = 'pharmacy vaccination near university of san francisco'
search_box = driver.find_elements_by_css_selector('input')
search_box[1].send_keys(search_input)

search_button = driver.find_elements_by_css_selector('button[aria-label="Search"]')
search_button[0].click()
time.sleep(6)

# create info lists
name, address, number, website = [],[],[],[]

aria_label = 'div[aria-label="Results for ' + search_input + '"] div.MVVflb-haAclf-uxVfW-hSRGPd'
parent = driver.find_elements_by_css_selector(aria_label)
#print('parent: {}'.format(len(parent)))

try:
    # website
    for div in parent:
        book_button = div.find_elements_by_css_selector('button[data-value="Book"]')
        website_button = div.find_elements_by_css_selector('button[data-value="Website"]')
        #print('book: {}'.format(len(book_button)))
        #print('web: {}'.format(len(website_button)))
        if len(book_button) != 0:
            book_button[0].click()
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)
            website.append(driver.current_url)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        elif len(website_button) != 0:
            website_button[0].click()
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)
            website.append(driver.current_url)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        else:
            website.append(None)
        #name
        name.append(div.find_elements_by_css_selector('span')[0].text)
        # address
        address.append(div.find_elements_by_css_selector('span[jstcache="864"]')[1].text.split('· ')[1])
        # phone number
        # since the index of phone number's presence varies, use regex to identify it
        span = div.find_elements_by_css_selector('div[jstcache = "863"]') #this span tag may contain instances of infomation that should be filtered
        candi_info = []
        for ind in range(len(span)):
            candi_info.append(span[ind].text)
        for item in candi_info:
            regex = re.findall(r'\(\d{3}\)\s\d{3}-\d{4}', item)
            if len(regex) != 0:
                number.append(regex[0])

    print ('Sucessfully scraped {} instances of pharmacy'.format(len(set(address))))
    driver.quit()


except IndexError:
    print ('List returns null')
    driver.quit()


# In[9]:


# convert scraped data into dataframe with duplicates dropped
d = {'name': name, 'address': address, 'number': number, 'website': website}
df = pd.DataFrame(d).drop_duplicates()
df


# In[10]:


# assume that according to database records, three of the listed pharmacies accept our insurance
# get "eligible" pharmacies from scraped data by sampling
sample = df.sample(n = 3, random_state = 1).reset_index(drop = True)
# get "eligible" pharmacies from database (example)
d_db = {
    'name': ['Pharmacy 1', 'Pharmacy 2', 'Saint Marys Medical Center Clinic Pharmacy', 'Walgreens Pharmacy', 'CVS Pharmacy'], 
    'address': ['123 W', '321 E', '2235 Hayes St', '3601 California St', '3600 Geary Blvd'],
    'number': ['(123)321-1234', '(321)123-4321', '(415) 750-5717', '(415) 668-5202', '(415) 668-6083'], 
    'website': ['https://P1.com', 'https://P2.com', None, 'https://www.walgreens.com/findcare/vaccination/covid-19', 'https://www.cvs.com/immunizations/covid-19-vaccine']
}
df_db = pd.DataFrame(d_db)
df_db


# In[11]:


# inner join scraped dataset and database dataset
result = pd.merge(df, df_db)
result


# In[ ]:




