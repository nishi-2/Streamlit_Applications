import streamlit as st
import requests
from bs4 import BeautifulSoup
from scrape import get_data

st.title("Web Scraping")
st.write("Enter a URL to scrape its content - ")

url_input = st.text_input("Enter URL")


if st.button("Scrape"):
    if url_input:
        content = get_data(url_input)
        if content:
            st.subheader("Scraped Content:")
            st.write(content)
        else:
            st.warning("No content found or an error occurred.")
    else:
        st.warning("Please enter a valid URL.")