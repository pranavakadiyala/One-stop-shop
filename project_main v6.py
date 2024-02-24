## File: project.py

import pandas as pd
from bs4 import BeautifulSoup
import requests
import json 
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import tabula 
from googletrans import Translator 


def main():
    # Welcome words + translation 
    welcome()
    
    welcomeUkrainian()
    # Ask to choose from the menu & then implement what the user has asked
    while True:
        try:
            # Menu
            menu()
            user_choice = int(input("Please enter the number for your desired service or '0' to exit: "))
            if user_choice == 0:
                break
            
            # Accommodation
            elif user_choice == 1:
                accommodation()
                continue
            
            # Health and social services
            elif user_choice == 2:
                healthsoc()
                continue
            
            # Legal services
            elif user_choice == 3:
                legal()
                continue 
            
            # Jobs
            elif user_choice == 4:
                jobs()
                continue 

            else:
                pass 
            
        except (ValueError, TypeError, KeyError):
            pass

t = Translator()
def welcomeUkrainian():
    uk = t.translate("""
          Hello! Welcome to Pittsburgh, Pennsylvania. 
          We are here to assist you during your transition to the city. 
          Here is a list of available services in Pittsburgh:
          """, dest = 'uk')
    print('\t\t  ' + uk.text)
    
def welcome():
    print("""
          Hello! Welcome to Pittsburgh, Pennsylvania. 
          We are here to assist you during your transition to the city. 
          Here is a list of available services in Pittsburgh:
          """)

def menu():
    print("""
          Menu:
          1. Accommodation
          2. Health and social services 
          3. Legal services
          4. Jobs 
          0. Exit
          """)

def accommodation():   
    '''
    First install selenium and import it. To install, type 'conda install -c conda-forge selenium'.
    After installing import webdriver from selenium.
    Then import:
        By from selenium.webdriver.common.by
        time
        regex (re)
        pandas as pd

    Download web driver. We use chrome, hence, download the chrome web driver.
    Website: "https://sites.google.com/chromium.org/driver/downloads?authuser=0"
    Please check for the correct version of driver to download in Google Settings ie., your browser version and driver version should match.
    
    Put it in a folder, assign the path to a variable 'PATH'.  
    '''
    
    #set path
    with open('path.txt', 'r') as f:
        for line in f:
            line = line.strip()
    #print(line)
    PATH = line
    #update the path.txt file to your path which houses the chromedriver

    #set the browser. specifying the webdriver we use for the browser as Chrome
    driver = webdriver.Chrome(PATH)
    
    #opening and accessing the webpage
    driver.get("https://www.ukrainetakeshelter.com/")
    
    #find the name given to the search bar
    search = driver.find_element(By.NAME, "query")
    
    #input which location you want to find accomodation
    search.send_keys("Pittsburgh, Pennsylvania, United States\n")
    
    #wait a second for the website to respond
    time.sleep(1)
    
    #select the first option from the dropdown menu
    search.find_element(By.XPATH, 
                        '/html/body/main/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/form/div/div/div/div[1]').click()
    #Opening the website, putting in the query and takes a bit of time to run, wait for 1 minute here
    time.sleep(10)
    
    ##We want to restrict to listings in Pittsburgh only, we do that by looking at listings with 0.00 as kilometers. 
    ##Comparing Xpaths of the first and last listing, we notice that the index value of the last div changes with the listing
    ##Lisitng one was div[1] and the last listing was div[96]
    ##We use this to loop over all the Kms and only append to dict if Kms are 0.00 
    distance = {}
    for i in range(1, 97): 
        d = driver.find_element(By.XPATH, "/html/body/main/div/div[3]/div[2]/div/div[1]/div/div/div[2]/div[" +str(i)+"]/t/span[2]/span")
        #print(str(i) +', ' + d.text)
        if d.text == '0.00':
            distance[i] = d.text
    
    #finding the key value of the last key value pair
    max_distance_key = max(distance.keys())
    
    #generating a list of lists of the listings, restricting to the ones in Pittsburgh only
    total_list = []
    for i in range(1, max_distance_key+1):
        l = driver.find_element(By.XPATH, "/html/body/main/div/div[3]/div[2]/div/div[1]/div/div/div[2]/div["+str(i)+"]").text
        total_list.append(l.split('\n'))
    
    #finding a set of spaces that were advertised in the listings
    space_old = set()
    for i in total_list:
        space_old.add(i[2])
    
    '''
    Menu options for spaces:
        1 space
        2 spaces
        3 spaces
        4 spaces
        5 and above spaces
    '''
    space = []
    for i in space_old:
        space.append(i)
    #print(space)
    
    #creating varaibles (and a list) of all the various space categories available in the listings
    five_above = []
    for i in range(len(space)):
        if re.search(r'1', space[i]) != None:
            one = space[i]
        elif re.search(r'2', space[i]) != None:
            two = space[i]
        elif re.search(r'3', space[i]) != None:
            three = space[i]
        elif re.search(r'4', space[i]) != None:
            four = space[i]
        elif re.search(r'[5-9][0-9]*', space[i]) != None:
            five_above.append(space[i])       
     
    #making a dataframe from the listings data    
    acc_data = pd.DataFrame(total_list, columns = ['Description', 'Location', 'Spaces', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'])
    
    #droping location as it is redundant
    acc_data.drop(columns='Location', inplace = True)
    
    #converting all None to NA
    acc_data.fillna('NA', inplace = True)
    
    #generating a column for verified info, since information about verification of
    # a particular listing is not available in a single, particular column, we first loop
    #through all rows, then all column values within a particular row. If a value matches
    #our regex about verification, we add to our column, if not we instead put 'NA'
    verified = {}
    for i in acc_data.index:
        for col in acc_data.columns:
            if re.search(r'(Verified)', acc_data.iloc[i][col]) != None: 
                verified[i] = [acc_data.iloc[i][col]]
                break
            elif re.search(r'(Verified)', acc_data.iloc[i][col]) == None: 
                verified[i] = ['NA']
    
    verified_df = pd.DataFrame(verified)
    verified_df = verified_df.T
    verified_df.rename(columns = {0:'Verified'}, inplace = True)
    
    #generating a column for short term info - same logic as for verified column
    short_term = {}
    for i in acc_data.index:
        for col in acc_data.columns:
            if re.search(r'(Short Term)', acc_data.iloc[i][col]) != None: 
                short_term[i] = [acc_data.iloc[i][col]]
                break
            elif re.search(r'(Short Term)', acc_data.iloc[i][col]) == None: 
                short_term[i] = ['NA']
    short_term_df = pd.DataFrame(short_term)
    short_term_df = short_term_df.T
    short_term_df.rename(columns = {0:'Short Term'}, inplace = True)
    
    #generating a column for long term info - same logic as for verified column
    long_term = {}
    for i in acc_data.index:
        for col in acc_data.columns:
            if re.search(r'(Long Term)', acc_data.iloc[i][col]) != None: 
                long_term[i] = [acc_data.iloc[i][col]]
                break
            elif re.search(r'(Long Term)', acc_data.iloc[i][col]) == None: 
                long_term[i] = ['NA']
    long_term_df = pd.DataFrame(long_term)
    long_term_df = long_term_df.T
    long_term_df.rename(columns = {0:'Long Term'}, inplace = True)
    
    #creating a details dataframe to add all the other info - we use total_list
    
    #remove data on description, location and spaces from each individual listins from total_list
    detail_list = []
    for i in total_list:
        detail_list.append(i[3:])
    
    #then remove data about verification, short term and long term.
    #We loop through each list first inside the detail_list, and then loop through every 
    #str value inside the list. We stop looping once we have removed the information we need
    for i in detail_list:
        for x in range(len(i)):
            if re.search(r'(Verified)', i[x]) != None:
                i.remove(i[x])
                break
    for i in detail_list:
        for x in range(len(i)):
            if re.search(r'(Short Term)', i[x]) != None:
                i.remove(i[x])
                break
    for i in detail_list:
        for x in range(len(i)):
            if re.search(r'(Long Term)', i[x]) != None:
                i.remove(i[x])
                break
    
    #joining all the other details for each listing, using ',' and appending into one big list
    detail_list_join = []
    for i in detail_list:
        detail_list_join.append(', '.join(i))
    
    details_df = pd.DataFrame(detail_list_join, columns=['Details'])
    
    #creating a clean dataframe for accomodation
    acc_data_clean = acc_data.copy()
    acc_data_clean.drop(columns=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'], inplace = True)
    acc_data_clean = pd.concat([acc_data_clean, verified_df, short_term_df, long_term_df, details_df], axis = 1)
    
    #Specifying the menu for users to choose between different space choices and representing the appropriate dataframe info
    def menu_acc():
        print('''
              Choose the number of spaces you are looking for in accomodation
              1 - 1 Space
              2 - 2 Spaces
              3 - 3 Spaces
              4 - 4 Spaces
              5 - 5 Spaces and more
              0 - Exit
              ''')
        y = int(input('Enter your choice: '))
        
        while y!=0:
            if y == 1:
                print('\n\nInformation for accomodation with one space\n')
                pd.set_option('display.expand_frame_repr', False)
                print(acc_data_clean.loc[acc_data_clean['Spaces'] == one])
            elif y == 2:
                print('\n\nInformation for accomodation with two spaces\n')
                pd.set_option('display.expand_frame_repr', False)
                print(acc_data_clean.loc[acc_data_clean['Spaces'] == two])
            elif y == 3:
                print('\n\nInformation for accomodation with three spaces\n')
                pd.set_option('display.expand_frame_repr', False)
                print(acc_data_clean.loc[acc_data_clean['Spaces'] == three])
            elif y == 4:
                print('\n\nInformation for accomodation with four spaces\n')
                pd.set_option('display.expand_frame_repr', False)
                print(acc_data_clean.loc[acc_data_clean['Spaces'] == four])
            elif y == 5:
                print('\n\nInformation for accomodation with five and more spaces\n')
                pd.set_option('display.expand_frame_repr', False)
                concat = pd.concat([acc_data_clean.loc[acc_data_clean['Spaces'] == five_above[0]], acc_data_clean.loc[acc_data_clean['Spaces'] == five_above[1]]], axis = 0)
                print(concat)    
            
            y = int(input('Enter your choice [Pick a number within 1-5 or 0 to exit]: '))
        
        print('Exit')
    
    menu_acc()
    
def healthsoc(): # A function to display health and social services available in Pittsburgh
    page = requests.get('https://www.dhs.pa.gov/refugeesinpa/Pages/Directory-Service-Contractors.aspx#C2') # accessing site with resources for refugees in PA
    soup = BeautifulSoup(page.content, 'html.parser') # scraping site
    tags2 = soup.find_all(class_ = "ms-rteTableOddRow-default") # accessing table that contains information on health and social services for refugees
    health = str(tags2[9]) # accessing the health services in Pittsburgh only
    social = str(tags2[1]) # accessing the social services in Pittsburgh only
    # Assigning variables to each piece of information scraped from web below:
    nameSoc = social[191:228] # accessing string that refers to the name of the social service business in Pittsburgh
    nameSoc = nameSoc.replace('&amp;', 'and') # fixing string to remove special character & for just 'and'
    addSoc = social[317:337] + ', ' + social[376:396] # accessing string for address of social service business
    phoneSoc = social[578:590] # accessing string with phone number for social service business
    nameHeal = health[207:234] # accessing string with name of health services business in Pittsburgh
    addHeal = health[303:344] # accessing string with address of health services business
    phoneHeal = health[409:423] # accessing string with phone number of health services business
    
    # Introducing the information
    print('\n\nBelow you will find information about available health and social services for refugees in Pittsburgh.\n')

    # creating a DF and formatting for readable output for user
    info = pd.DataFrame({'Social Services': [nameSoc, addSoc, phoneSoc], 'Health Services': [nameHeal, addHeal, phoneHeal]})
    print('%-45s %-20s' % ('Social Services', 'Health Services'))
    for i in info.values:
        print('%-45s %-20s' % (i[0], i[1]))

    # Closing information
    print('\nIf you are in need of medical assistance, apply for Refugee Medical Assistance (RMA). RMA offers short-term medical coverage to refugees.')
def legal(): 
    # Part 1
    print("Part 1: Learn more about legal statuses in the US")
    print("""
          Possible legal statuses in the US:
              
          1. Uniting for Ukraine
          2. Temporary Protected Status (TPS)
          3. Humanitarian Parole
          4. B2 “Tourist” Visa
          5. Asylum
          6. Refugee
          7. Family Based Immigration
          8. Employment-Based Immigrant Visas & Green Cards
          9. Nonimmigrant Employment-Based Visas
          10. Lautenberg Program
          11. F-1 Student Visa & J-1 Exchange Visitor Visa 
          
          Detailed info about each status: https://linforukraine.org/legal-library/
          """)
    # Part 2
    print("Part 2: Find a legal representative")
    print("""
          Only two groups of people may provide legal services:
          1. attorneys
          2. accredited representatives of non-profit religious, charitable, or social service organizations
          """)

    print("""
          Please see below a list of accredited representatives of non-profit 
          religious, charitable, or social service organizations (pro-bono)
          """) 
    pdf_path = "https://www.justice.gov/eoir/page/file/942306/download#PENNSYLVANIA"
    page106 = tabula.read_pdf(
        pdf_path, 
        pages=106,
        lattice=True, 
        stream=True)    
    page106_df = pd.DataFrame()
    page106_df = pd.concat([c for c in page106])
    #select representatives from Pittsburgh 
    data_df = page106_df['Philadelphia, PA 19106\r(215) 832-0900'].loc[10:14]
    data_list = data_df.values.tolist()
    data = []
    for i in data_list[:-1]:
        a = i.split('\r')
        data.append(a)
    #name
    names = []
    for i in data:
        names.append(i[0])
    #address
    address = []
    pattern = r'^[0-9]+'
    for string in data:
        for element in string:
            if re.search(pattern, element) != None:
                address.append(element)
    #phone
    phone = []
    for i in data:
        phone.append(i[-1])
    
    info = pd.DataFrame({'Name': names,'Address in Pittsburgh': address, 'Phone': phone})
    print('%-55s %-25s %-20s' % ('Name', 'Address in Pittsburgh', 'Phone'))
    for i in info.values:
        print('%-55s %-25s %-20s' % (i[0], i[1], i[2]))
    
    # Part 3   
    print("\n")
    print("Part 3: Protect yourself from fraud")
    print("""
          Please read this before asking for legal representation:
          
          What to expect from a legal representative: https://www.unhcr.org/en-us/58595dfc4.pdf
          How to protect yourself from fraud: https://www.unhcr.org/en-us/585989984.pdf 
          """)

def jobs(): 
    url = 'https://serpapi.com/search.json?engine=google_jobs&q=jobsforimmigrants+pittsburgh&hl=en&gl=us&google_domain=google.com&api_key=9b4a52d8d21c0146d86a86d788bbfdab4001278cc2f25cff915821822b036adf'
    
    # API used to extract google job search results. API key was required but provided for free by SerpAPI.
    # q which is the parameter that defines the query we wanted to search was set to "jobs for immigrants" and Pittsburgh was set as the location of interest. 
    
    response = requests.get(url, headers = {'Content-Type': 'application/json'})
    
    if response.status_code  == 200:
        jobs_data = json.loads(response.content.decode('utf-8'))
           
    
    # jobs_data returns a JSON dict of dicts and lists from where the jobs results below were extracted. 
    
    jobs_results = jobs_data['jobs_results']

    # jobs_results only returns the jobs search results we are interested in.
    
    print('Here is a list of the jobs available for immigrants in Pittsburgh, PA:\n')
    
    print('{:68s} {:85s} {:10s}'.format('Job Title','Company','Employment Type'))
        
    for job in jobs_results:
        job_title = job['title']
        company = job['company_name']
        employment_type = job['detected_extensions']['schedule_type']
        print('{:68s} {:85s} {:10s}'.format(job_title, company, employment_type))
        
    # The code above shows the different jobs available to immigrants, along with the companies hiring for these jobs and the type of employment( full-time, part-time, contract, etc...).
    # The results are displayed in the form of a table using regular Python formatting with columns: Job Title", "Company" and " Employment type". 
    
    
    # The code below asks the user if they would like to see a description of the jobs.
    # If the user answers anything other than "Yes" or "No" (due to typos maybe), he/she is prompted again to answer between "Yes" or "No" ONLY. 
    # If the user answers "No", the following text is displayed on his/her screen: 'No problem. Thanks for using our services !"
    # However, if he/she answers "Yes", a numbered list of the available jobs is displayed for him/her to choose by entering the number associated with the jobs he/she interested in.
    # If the user fails to enter a number within the appropriate range, he/she will see an Error message and will be prompted again to enter a valid number (using the numbered list that was provided to him/her earlier). 
    # When the user enters a correct/valid number, he/she is provided with the description of the job posting that he/she is interested in + where he/she can go to apply for the jobs.
    # A final "thank you" message is displayed and then user is taken back to the main menu where he/she can access other resources in our app such as "Accommodation", "Legal services", "healthcare services". 
    
    x = ''     
    while x.title() != 'Yes' and x.title() != 'No':
        x = input('Would you like to see a description of the jobs ? Enter Yes or No:')
        print('\n')
        if x.title() == 'No':
            print('No problem. Thanks for using our services !')
            break
        elif x.title() == 'Yes':
            list_of_jobs = [] 
            for job in jobs_results:
                job_title = job['title']
                list_of_jobs.append(job_title)
            length = len(list_of_jobs)
            print('If you would like to see the description for:\n')
            for i in range(length):
                print(list_of_jobs[i], 'Enter', i, '\n')
            dict_jobs = dict(enumerate(list_of_jobs))
            y = int(input('Which one would you like to know more about ? Enter the number: '))
            if y not in range(length):
                while y not in range(length):
                    print('Error')
                    y = int(input('Please enter a valid number using the list above: '))
            if y in range(length):
                for job in jobs_results:
                    if dict_jobs[y] == job['title']:
                        job_description = job['description']
                        print('Here is the job description for', dict_jobs[y], ':\n')
                        print(job_description)
                        job_app_website = job['via']
                        print('You can apply for this job', job_app_website, '\n')
                        print('Hope you found this information helpful ! \n')
                        print('Thanks for using our services !')
                        break

if __name__ == '__main__':
    main()

