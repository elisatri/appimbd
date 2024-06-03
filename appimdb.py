import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
from matplotlib import pyplot as plt

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

# Set page title and favicon
st.set_page_config(page_title="IMDb Movie Dashboard", page_icon=":clapper:")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page", ["Top Picks", "List of Films", "Dashboard"])

# Main content
if page == "Top Picks":
    # ACTION 1: Get all titles and movie links from TOP PICKS
    st.title("Top Picks Titles and Links")
    top_picks = get_top_picks()
    st.dataframe(top_picks)
    
    # ACTION 2: Access movie detail pages to extract Box Office Data and Technical Specs
    st.title("Movie Details from Top Picks")
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
    
elif page == "List of Films":
    # Display list of films from imdb_primary_data.csv
    st.title("List of Films")
    primary_data = pd.read_csv('imdb_primary_data.csv')
    film_selection = st.selectbox("Select a film", primary_data['Name'].tolist())

    # Get the link to the movie detail page from secondary data
    secondary_data = pd.read_csv('imdb_secondary_data.csv')
    selected_movie = secondary_data.loc[secondary_data['Name'] == film_selection]

    if not selected_movie.empty:
        movie_url = selected_movie['Link'].values[0]

        st.title(f"{film_selection} Details")
        st.markdown(f"IMDb Link: [{film_selection}]({movie_url})")

        box_office_data, tech_specs_data = get_movie_details(movie_url)

        st.subheader("Box Office Data:")
        st.write(box_office_data)

        st.subheader("Technical Specs:")
        st.write(tech_specs_data)
    else:
        st.warning("Movie details not found.")
        
elif page == "Dashboard":
    # 1. COMPARISON CHART - BAR CHART
    st.title("1. COMPARISON CHART - BAR CHART")
    df_sel = df[['Rating','Gross_US', 'Gross_World']].sort_values(by=['Rating'])

    # Drop rows with all zeros
    hsl = df_sel.loc[(df_sel[['Gross_US', 'Gross_World']] != 0).all(axis=1)]

    # Prepare the chart data from panda dataframe for BAR CHART
    chart_data = pd.DataFrame(
        {
            "Rating": hsl['Rating'], "Gross US": hsl['Gross_US'], "Gross World":hsl['Gross_World']
        }
    )

    # BAR CHART
    st.bar_chart(
       chart_data, x="Rating", y=["Gross US", "Gross World"], color=["#FF0000", "#0000FF"]
    )

    # 2. RELATIONSHIP CHART - SCATTER PLOT
    st.title("2. RELATIONSHIP CHART - SCATTER PLOT")
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
        color=['#FF0000', '#0000FF']
    )

    # 3. COMPOSITION CHART - DONUT CHART
    st.title("3. COMPOSITION CHART - DONUT CHART")
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
    st.title("4. DISTRIBUTION - LINE CHART")
    st.line_chart(
        chart_data2, 
        x='Durasi(Menit)',
        y=['Budget','Gross_US'],
        color=['#FF0000', '#0000FF']
    )
