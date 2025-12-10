import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# connect to UFC webpage and extract page info

response = requests.get("http://ufcstats.com/statistics/events/completed?page=all")

##print(response)
##print(response.content)

# convert content to bs4 element 
soup = BeautifulSoup(response.content, "html.parser")
##print(soup)

table_rows = soup.find_all('tr', class_ = "b-statistics__table-row")
#print(table_rows[0])
#print(table_rows[1])
#print(table_rows[2])

ufc_events_url = []
# Pulls every seperate UFC event URL
for i in range(2, len(table_rows)):
    event_link = table_rows[i].find('a')
    ufc_events_url.append(event_link.get('href'))

#print(ufc_events_url)

# Create dictionary to initalise data frame
dta = {"Event": ["-"],
       "Date": ["-"],
       "Location": ["-"],
       "WL": ["-"],
       "Fighter_A": ["-"],
       "Fighter_B": ["-"],
       "Fighter_A_KD": ["-"],
       "Fighter_B_KD": ["-"],
       "Fighter_A_STR": ["-"],
       "Fighter_B_STR": ["-"],
       "Fighter_A_TD": ["-"],
       "Fighter_B_TD": ["-"],
       "Fighter_A_SUB": ["-"],
       "Fighter_B_SUB": ["-"],
       "Victory_Result": ["-"],
       "Victory_Method": ["-"],
       "Round": ["-"],
       "Time": ["-"],
       "Weight_Class": ["-"],
       "Title": [0],
       "Fight_Bonus": [0],
       "Perf_Bonus": [0],
       "Sub_Bonus": [0],
        "KO_Bonus": [0]}

# Use Pandas variable to convert the dictinoary into a data frame
fight_data = pd.DataFrame(dta)

# Row counter
jj = 0
start_time = time.perf_counter()

for i in range(len(ufc_events_url)):
    url = ufc_events_url[i]
    print(f"{i+1} out of {len(ufc_events_url)} events completed")

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    #print(soup)

    # Get the event data, location and name                        
    event_title = soup.find('span', class_ = "b-content__title-highlight").get_text(strip = True)
    date_location = soup.find_all('li', class_ = "b-list__box-list-item")

    event_loc = {}
    for tag in date_location:
        title_text = tag.find('i').get_text(strip = True)
        all_text = tag.get_text(strip = True)
        event_loc[title_text] = all_text.replace(title_text, "")
    #print(event_loc)
   

    fight_table = soup.find_all('tr', class_ = "b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click")
 
    for tr in fight_table:

        # Store every fight data into a seperate row    
        fight_data.loc[jj, "Event"] = event_title
        fight_data.loc[jj, "Date"] = event_loc["Date:"]
        fight_data.loc[jj, "Location"] = event_loc["Location:"]

        tds = tr.find_all('td')

        # fight result
        fight_data.loc[jj,"WL"] = tds[0].get_text(strip = True).upper()
        # fighter names
        fighters = tds[1].find_all('p')
        fight_data.loc[jj, "Fighter_A"] = fighters[0].get_text(strip = True)
        fight_data.loc[jj, "Fighter_B"] = fighters[1].get_text(strip = True)
        # fight stats
        KD = tds[2].find_all('p')
        fight_data.loc[jj, "Fighter_A_KD"] = KD[0].get_text(strip = True)
        fight_data.loc[jj, "Fighter_B_KD"] = KD[1].get_text(strip = True)
        STR = tds[3].find_all('p')
        fight_data.loc[jj, "Fighter_A_STR"] = STR[0].get_text(strip = True)
        fight_data.loc[jj, "Fighter_B_STR"] = STR[1].get_text(strip = True)
        TD = tds[4].find_all('p')
        fight_data.loc[jj, "Fighter_A_TD"] = TD[0].get_text(strip = True)
        fight_data.loc[jj, "Fighter_B_TD"] = TD[1].get_text(strip = True)
        SUB = tds[5].find_all('p')
        fight_data.loc[jj, "Fighter_A_SUB"] = SUB[0].get_text(strip = True)
        fight_data.loc[jj, "Fighter_B_SUB"] = SUB[1].get_text(strip = True)
        # method
        Method = tds[7].find_all('p')
        fight_data.loc[jj, "Victory_Result"] = Method[0].get_text(strip = True)
        fight_data.loc[jj, "Victory_Method"] = Method[1].get_text(strip = True)
        # round
        fight_data.loc[jj, "Round"] = tds[8].find('p').get_text(strip = True)
        # time
        fight_data.loc[jj, "Time"] = tds[9].find('p').get_text(strip = True)

        fight_data.loc[jj, "Weight_Class"] = tds[6].find('p').get_text(strip = True)
        img_list = tds[6].find_all('img')

        img_dn = {"belt.png":0, "fight.png":0, "perf.png":0, "sub.png":0, "ko.png":0}

        # extract image tag information if it exists 
        if len(img_list) !=0:
            for img in img_list:
                src = img.get('src')
                key = src.split('/')[-1]
                img_dn[key] = 1
        
        fight_data.loc[jj, "Title"] = img_dn ["belt.png"]
        fight_data.loc[jj, "Fight_Bonus"] = img_dn["fight.png"]
        fight_data.loc[jj, "Perf_Bonus"] = img_dn["perf.png"]
        fight_data.loc[jj, "Sub_Bonus"] = img_dn["sub.png"]
        fight_data.loc[jj, "KO_Bonus"] = img_dn["ko.png"]



        # Goes to next row once inital event data has filled out
        jj = jj +1

end_time = time.perf_counter()
execution_time = end_time - start_time

print(f"Execution time: {round(execution_time/60,2)} minutes")
  
# Exports data to CSV and removes first column containing indicies   
fight_data.to_csv("/Users/Ehad/Downloads/UFC_Events_Data.csv", index = False)