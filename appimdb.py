import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests
from bs4 import BeautifulSoup

# Function to get top picks titles and links
def get_top_picks():
    url = 'https://www.imdb.com/chart/top'  # URL to IMDb Top 250
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    movies = soup.select('td.titleColumn')
    links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]
    titles = [a.text for a in soup.select('td.titleColumn a')]
    
    top_picks = pd.DataFrame({
        'Title': titles,
        'Link': ['https://www.imdb.com' + link for link in links]
    })
    
    return top_picks

# Function to get box office data and technical specs from a movie detail page
def get_movie_details(movie_url):
    response = requests.get(movie_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract Box Office Data
    box_office_data = {}
    box_office_section = soup.find('section', {'data-testid': 'BoxOffice'})
    if box_office_section:
        for div in box_office_section.find_all('div'):
            key = div.find('span', class_='ipc-metadata-list-item__label').text
            value = div.find('span', class_='ipc-metadata-list-item__list-content-item').text
            box_office_data[key] = value
    
    # Extract Technical Specs
    tech_specs_data = {}
    tech_specs_section = soup.find('section', {'data-testid': 'TechSpecs'})
    if tech_specs_section:
        for div in tech_specs_section.find_all('div'):
            key = div.find('span', class_='ipc-metadata-list-item__label').text
            value = div.find('span', class_='ipc-metadata-list-item__list-content-item').text
            tech_specs_data[key] = value
    
    return box_office_data, tech_specs_data

# Read CSV files into dataframes
df = pd.read_csv('imdb_combined_data2.csv')

df['Rating'] = df['Rating'].astype("string")
df['Name'] = df['Name'].astype("string")
df['Year'] = pd.to_numeric(df['Year'])

# 1. COMPARISON CHART - BAR CHART
st.write("1. COMPARISON CHART - BAR CHART")
df_sel = df[['Rating','Gross_US', 'Gross_World']].sort_values(by=['Rating'])

# Drop rows with all zeros
hsl = df_sel.loc[(df_sel[['Gross_US', 'Gross_World']] != 0).all(axis=1)]

# Prepare the chart data from panda dataframe for BAR CHART
chart_data = pd.DataFrame(
    {
        "Rating": hsl['Rating'], "Gross US": hsl['Gross_US'], "Gross World":hsl['Gross_World']}
)

# BAR CHART
st.bar_chart(
   chart_data, x="Rating", y=["Gross US", "Gross World"], color=["#FF0000", "#0000FF"]  # Optional
)

# 2. RELATIONSHIP CHART - SCATTER PLOT
st.write("2. RELATIONSHIP CHART - SCATTER PLOT")
df_sel2 = df[['Gross_US','Gross_World','Durasi(Menit)','Budget','Rating']].sort_values(by=['Durasi(Menit)'])

# Drop rows with all zeros
hsl = df_sel2.loc[(df_sel2[['Gross_US', 'Gross_World']] != 0).all(axis=1)]

# Scale down the numbers in 3 columns
hsl['Gross_US'] = hsl['Gross_US']/1000000
hsl['Gross_World'] = hsl['Gross_World']/1000000
hsl['Budget'] = hsl['Budget']/1000000

# Prepare the data for plotting
chart_data2 = pd.DataFrame(hsl, columns=["Gross_US", "Gross_World", "Durasi(Menit)", "Budget", "Rating"])

# SCATTER PLOT
st.scatter_chart(
    chart_data2, 
    x='Durasi(Menit)',
    y=['Budget','Gross_US'],
    size='Gross_World',
    color=['#FF0000', '#0000FF'],  # Optional
)

# 3. COMPOSITION CHART - DONUT CHART
st.write("3. COMPOSITION CHART - DONUT CHART")
df_sel3 = df[['Gross_US','Gross_World','Budget','Rating']].sort_values(by=['Rating'])

# Drop rows with all zeros
hsl = df_sel3.loc[(df_sel3[['Gross_US', 'Gross_World']] != 0).all(axis=1)]
hsl = hsl.groupby(['Rating']).sum()

# Creating plot
fig = plt.figure(figsize=(10, 7))
explode = [0,0.1,0,0.1]
plt.pie(hsl['Gross_US'], labels = hsl.index, explode = explode, autopct='%1.1f%%',
        shadow=False, startangle=90)
plt.axis('equal')

# show plot
st.pyplot(fig)

# 4. DISTRIBUTION - LINE CHART
st.write("4. DISTRIBUTION - LINE CHART")
st.line_chart(
    chart_data2, 
    x='Durasi(Menit)',
    y=['Budget','Gross_US'],
    color=['#FF0000', '#0000FF'],  # Optional
)

# ACTION 1: Get all titles and movie links from TOP PICKS
st.write("ACTION 1: Top Picks Titles and Links")
top_picks = get_top_picks()
st.dataframe(top_picks)

# ACTION 2: Access movie detail pages to extract Box Office Data and Technical Specs
st.write("ACTION 2: Movie Details from Top Picks")
details_list = []
for index, row in top_picks.iterrows():
    title = row['Title']
    link = row['Link']
    box_office_data, tech_specs_data = get_movie_details(link)
    details_list.append({
        'Title': title,
        'Box Office Data': box_office_data,
        'Technical Specs': tech_specs_data
    })

details_df = pd.DataFrame(details_list)
st.dataframe(details_df)
