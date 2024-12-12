from bs4 import BeautifulSoup
import requests

html_text = requests.get('https://www.bbc.com/news').text

soup = BeautifulSoup(html_text, 'lxml')

headlines = soup.find_all('h2',class_='sc-8ea7699c-3 kwWByH')

for headline in headlines:
    headline_news = headline.text.strip()
    print(f"Headlines: {headline_news}")