"""
This is package has been built to scrape the website, Check Out My Cards (COMC). COMC is an online marketplace for buying and selling sports cards, trading cards, and other collectibles.

This package is strictly built for end users who wish to scrape data for personal use.

Please be consideration of COMC servers when using COMCscraper.

"""

#required packages
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np


def getSportsCards(sport, sort, attributes):
    
    """
    Get all sports cards for a specific sport with given attributes sorted by user choice

    """
    #baseURL along with user chosen parameters
    searchURL = 'https://www.comc.com/Cards/' + sport + ',' + sort + ',_' + attributes + ',i100'

    #empty lists for scraping COMC
    description = []
    card = []
    lowestprice = []
    
    #beginning messages
    print("The scraping of " + sport + " cards has begun.")
    print("Here is the URL you are scarping: " + searchURL)
    
    #URL exception
    try:
        source_code = requests.get(searchURL, timeout = 100)
        plain_text = source_code.content
        soup = BeautifulSoup(plain_text, "lxml")
    except URLError as url_error:
        print("Server Not Found")
    
    #Scraping description, player and lowest price for sale
    
    for desc in soup.find_all('div', class_ ="description"):
        desc2 = desc.text.replace('\r\n','').strip()
        description.append(desc2)

    for title in soup.find_all('h3', class_ ="title"):
        title2 = title.text.replace('\n', '')
        card.append(title2)
    
    for price in soup.find_all('a', title = "View Sales Data"):
        price2 = price.text
        lowestprice.append(price2)

    #store scraped data in dataframe
    result = pd.DataFrame({'Card': description, 'Player': card, 'Lowest Price': lowestprice})
    
    #Error Message if no results found
    if result.empty:
        print('No results, please alter search and try again...')
        return

    #create temp variable for cleaning up player column
    temp=result.Player

    result['Player (Clean)'] = np.where(temp.apply(str).str.contains(" - "), result.Player.str.split(' - ').str.get(1),
                   np.where(temp.str.contains("[EX to NM]"), result.Player.str.split('[').str.get(0).str.strip(), 
                   np.where(temp.str.contains(" #/"), result.Player.str.split('#').str.get(0).str.strip(),                   
                   np.where(temp.str.contains("Noted"), result.Player.str.split('[').str.get(0).str.strip(),result.Player.str.strip()))))
    
    result['Player (Clean)'] = result['Player (Clean)'].apply(str).str.split('#').str.get(0).str.strip()
    result['Year'] = result.Card.str.split(expand = True)[0]
    result['Season'] = result.Year.str.split('-').str.get(0)
    result['Serial #/'] = temp.str.split(' #/').str.get(1).str.strip().str.replace(',','')
    result['Set'] = result.Card.str.split(' - ').str.get(0).str.strip()
    result['Brand'] = result.Set.str.replace(r'[0-9]', '').str.replace(r'-', '').str.strip()
    result['Card #'] = result.Card.str.split('#').str.get(1).str.strip()
    result['Subset'] = result.Card.str.split(' - ').str.get(1).str.strip().str.split(' #').str.get(0).str.strip('[]')
    result['Attributes'] = attributes
    
    #Rearranges Columns
    result = result[['Card', 'Year','Player', 'Player (Clean)','Lowest Price','Season','Serial #/','Set','Brand','Card #','Subset', 'Attributes']]
    
    #Return Dataframe
    return(result)