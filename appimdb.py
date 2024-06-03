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

# Load IMDb primary data CSV
try:
    df = pd.read_csv('imdb_primary_data.csv')

    df['Rating'] = df['Rating'].astype("string")
    df['Name'] = df['Name'].astype("string")
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')  # Coerce errors to NaN

    # Streamlit App
    st.title("IMDb Movie Analysis")

    # 1. COMPARISON CHART - BAR CHART
    st.write("1. COMPARISON CHART - BAR CHART")
    df_sel = df[['Rating', 'Gross_US', 'Gross_World']].sort_values(by=['Rating'])

    # Drop rows with missing values
    df_sel.dropna(subset=['Gross_US', 'Gross_World'], inplace=True)

    # Prepare the chart data for BAR CHART
    chart_data = pd.DataFrame(
        {
            "Rating": df_sel['Rating'], "Gross US": df_sel['Gross_US'], "Gross World": df_sel['Gross_World']
        }
    )

    # BAR CHART
    st.bar_chart(
       chart_data, x="Rating", y=["Gross US", "Gross World"], color=["#FF0000", "#0000FF"]
    )

    # 2. RELATIONSHIP CHART - SCATTER PLOT
    st.write("2. RELATIONSHIP CHART - SCATTER PLOT")
    df_sel2 = df[['Gross_US', 'Gross_World', 'Durasi(Menit)', 'Budget', 'Rating']].sort_values(by=['Durasi(Menit)'])

    # Drop rows with missing values
    df_sel2.dropna(subset=['Gross_US', 'Gross_World'], inplace=True)

    # Scale down the numbers in columns
    df_sel2['Gross_US'] = df_sel2['Gross_US'] / 1000000
    df_sel2['Gross_World'] = df_sel2['Gross_World'] / 1000000
    df_sel2['Budget'] = df_sel2['Budget'] / 1000000

    # Prepare the data for plotting
    chart_data2 = pd.DataFrame(df_sel2, columns=["Gross_US", "Gross_World", "Durasi(Menit)", "Budget", "Rating"])

    # SCATTER PLOT
    st.scatter_chart(
        chart_data2, 
        x='Durasi(Menit)',
        y=['Budget', 'Gross_US'],
        size='Gross_World',
        color=['#FF0000', '#0000FF']
    )

    # 3. COMPOSITION CHART - DONUT CHART
    st.write("3. COMPOSITION CHART - DONUT CHART")
    df_sel3 = df[['Gross_US', 'Gross_World', 'Budget', 'Rating']].sort_values(by=['Rating'])

    # Drop rows with missing values
    df_sel3.dropna(subset=['Gross_US', 'Gross_World'], inplace=True)

    # Group by Rating and sum up values
    hsl = df_sel3.groupby(['Rating']).sum()

    # Creating plot
    fig = plt.figure(figsize=(10, 7))
    explode = [0, 0.1, 0, 0.1]
    plt.pie(hsl['Gross_US'], labels=hsl.index, explode=explode, autopct='%1.1f%%', shadow=False, startangle=90)
    plt.axis('equal')

    # show plot
    st.pyplot(fig)

    # 4. DISTRIBUTION - LINE CHART
    st.write("4. DISTRIBUTION - LINE CHART")
    st.line_chart(
        chart_data2, 
        x='Durasi(Menit)',
        y=['Budget', 'Gross_US'],
        color=['#FF0000', '#0000FF']
    )

    # ACTION 1: Get all titles and movie links from TOP PICKS
    st.write("ACTION 1: Top Picks Titles and Links")
    top_picks = get_top_picks()
    st.dataframe(top_picks)

    # ACTION 2: Access movie detail pages to extract Box Office Data and Technical Specs
    st.write("ACTION 2: Movie Details from Top Picks")

    film_selection = st.selectbox("Select a movie title to see details:", top_picks['Title'].values)
    selected_movie = top_picks[top_picks['Title'] == film_selection]

    if not selected_movie.empty and 'Link' in selected_movie.columns:
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
except KeyError as e:
    st.error(f"Error: {str(e)}")
except FileNotFoundError:
    st.error("Error: CSV file not found. Please check if 'imdb_primary_data.csv' exists.")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
