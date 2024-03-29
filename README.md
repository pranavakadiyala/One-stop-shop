# One-stop-shop

In this project, we developed a prrof-of-concept a content aggregator application, using Python, that collates information about available resources for Ukrainian refugees in Pittsburgh. We extract information from a variety of sources on both government and public websites: lists on a PDF, a static website, an interactive website, and an API. 

This task required **nine different libraries**: pandas, requests, beautifulsoup, regex, JSON, time, selenium, googletrans, and tabula. We scraped websites using selenium and beautifulsoup to aggregate information relating to accommodations and health services. Using tabula, we tabulated legal services data on a PDF and converted it to a CSV file to open in Python. Finally, we used a live API to fetch data on job listings from Google job search. We then presented all information using pandas to make it readable to the user. Within our Python program, the user chooses from a menu of Accommodations, Health and Social Services, Legal Services, and Employment. After selecting from the menu, the user sees what resources are available in Pittsburgh. 

Contributors: **Pranava Kadiyala**, Samira Diabi, Amelia Janaskie, Kate Shapovalenko
