import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Set page title and favicon
st.set_page_config(page_title="IMDb Movie Data", page_icon=":clapper:")

# File paths
filename = "imdb_primary_data.csv"
filename2 = "imdb_secondary_data.csv"

# Function to read primary data
def read_primary_data():
    df = pd.read_csv(filename)
    return df

# Function to read secondary data
def read_secondary_data():
    df = pd.read_csv(filename2)
    return df

# Function to fetch data from IMDb and save to CSV
def fetch_imdb_data():
    # the first page to be accessed
    my_url = "http://www.imdb.com/search/title?sort=num_votes,desc&start=1&title_type=feature&year=2024,2024"

    # define browser to get the first URL
    browser = webdriver.Firefox()

    # define browser to get the second/detail URL
    browser2 = webdriver.Firefox()

    # check file availability and content is not empty
    if filename in os.listdir():
        os.remove(filename)
    if filename2 in os.listdir():
        os.remove(filename2)

    f = open(filename, "w")
    fheaders = "Name,Year,Durasi(Menit),Rating\n"
    f2 = open(filename2, "w")
    f2headers = "Name,Budget,Gross_US,Opening_Week,Open_Week_Date,Gross_World\n"

    f.write(fheaders)
    f2.write(f2headers)

    try:
        # open session for first URL
        browser.get(my_url)

        # ACTION 1
        first_page = BeautifulSoup(browser.page_source, 'html.parser')
        movies = first_page.find_all("div", {"class": "sc-b189961a-0 hBZnfJ"})

        count2 = 0
        for movie in movies:
            count2 += 1
            menit = 0
            rating = "Not Rated"
            name = re.sub(r"\d+. ", "", movie.find("h3", {"class": "ipc-title__text"}).text)
            detil_line = movie.findAll("span", {"class": "sc-b189961a-8 kLaxqf dli-title-metadata-item"})
            if len(detil_line) > 2:
                year_movie = detil_line[0].text
                durasi = detil_line[1].text
                durasi = durasi.split(" ")
                if len(durasi) > 1:
                    menit = int(durasi[0].replace("h", "")) * 60 + int(durasi[1].replace("m", ""))
                else:
                    menit = int(durasi[0].replace("h", "")) * 60
                rating = detil_line[2].text
            elif len(detil_line) > 1:
                year_movie = detil_line[0].text
                durasi = detil_line[1].text
                durasi = durasi.split(" ")
                if len(durasi) > 1:
                    menit = int(durasi[0].replace("h", "")) * 60 + int(durasi[1].replace("m", ""))
                else:
                    menit = int(durasi[0].replace("h", "")) * 60
            else:
                year_movie = detil_line[0].text

            f.write(name + "," + year_movie + "," + str(menit) + "," + rating + "\n")

        # ACTION 2
        links = browser.find_elements(By.XPATH, '//div[@class="sc-b189961a-0 hBZnfJ"]')

        count = 0
        for link in links:
            title = re.sub(r"\d+. ", "", link.find_element(By.CSS_SELECTOR, "a").get_attribute('aria-label'))
            browser2.get(link.find_element(By.CSS_SELECTOR, "a").get_attribute('href'))

            # BOX OFFICE DATA ON THE 2ND URL
            det_page = browser2.page_source
            container_rows = BeautifulSoup(det_page, "html.parser")
            box_office_elements = container_rows.find("div", {"data-testid": "title-boxoffice-section"})
            if box_office_elements is not None:
                det_movie = box_office_elements.find_all("span", {"class": "ipc-metadata-list-item__list-content-item"})

                if len(det_movie) > 4:
                    budget = det_movie[0].text
                    gross_us = det_movie[1].text
                    open_week_rev = det_movie[2].text
                    open_week_date = det_movie[3].text
                    gross_world = det_movie[4].text

                    budget_num = int(re.sub("[A-Z£€₹$,()a-z]", "", budget))
                    gross_us_num = int(re.sub("[A-Z£€₹$,()a-z]", "", gross_us))
                    open_week_rev_num = int(re.sub("[A-Z£€₹$,()a-z]", "", open_week_rev))
                    open_week_date_std = datetime.strptime(open_week_date, "%b %d, %Y")
                    gross_world_num = int(re.sub("[A-Z£€₹$,()a-z]", "", gross_world))

                    f2.write(
                        str(title) + "," + str(budget_num) + "," + str(gross_us_num) + "," + str(open_week_rev_num) + "," + str(
                            open_week_date_std) + "," + str(gross_world_num) + "\n")

    except Exception as E:
        st.error(f"Error: {E}")

    finally:
        f.close()
        f2.close()
        browser.quit()
        browser2.quit()

# Fetch data from IMDb if files are not present
if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
    fetch_imdb_data()

# Main Streamlit app
st.title("IMDb Movie Data")

# Read primary data
primary_df = read_primary_data()

# Display primary data as list
st.subheader("Primary Data")
for index, row in primary_df.iterrows():
    st.write(f"{row['Name']} ({row['Year']}) - Duration: {row['Durasi(Menit)']} minutes, Rating: {row['Rating']}")

# Read secondary data
secondary_df = read_secondary_data()

# Display secondary data as list with clickable titles
st.subheader("Secondary Data")
for index, row in secondary_df.iterrows():
    if st.button(f"{row['Name']}"):
        st.write(f"**Budget**: {row['Budget']}")
        st.write(f"**Gross US**: {row['Gross_US']}")
        st.write(f"**Opening Week**: {row['Opening_Week']} (Date: {row['Open_Week_Date']})")
        st.write(f"**Gross World**: {row['Gross_World']}")

