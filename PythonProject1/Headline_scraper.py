from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
from bs4 import BeautifulSoup
import requests
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Variable to store the scraped headlines
scraped_headlines = []

def scrape_news():
    """
    Function to scrape news from BBC and update the global headlines list.
    """
    global scraped_headlines
    try:
        html_text = requests.get('https://www.bbc.com/news').text
        soup = BeautifulSoup(html_text, 'lxml')
        headlines = soup.find_all('h2', class_='sc-8ea7699c-3 kwWByH')
        scraped_headlines = [headline.text.strip() for headline in headlines]
        print(f"Scraped {len(scraped_headlines)} headlines.")  # Log for debugging
    except Exception as e:
        print(f"Error occurred during scraping: {e}")

@app.route('/news', methods=['GET'])
def get_news():
    """
    API endpoint to fetch the latest scraped news.
    """
    return jsonify({"headlines": scraped_headlines})

if __name__ == '__main__':
    # Scheduler setup
    scheduler = BackgroundScheduler()
    scheduler.add_job(scrape_news, 'interval', minutes=10)  # Run every 10 minutes
    scheduler.start()

    # Run the first scrape immediately
    scrape_news()

    # Start the Flask app
    try:
        app.run(debug=True, host='0.0.0.0', port=10000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
