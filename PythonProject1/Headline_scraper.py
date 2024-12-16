from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
from bs4 import BeautifulSoup
import requests
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Variables to store the scraped headlines and subtext
scraped_headlines = []
scraped_subtext = []
scraped_otherReads = []

def scrape_news():
    """
    Function to scrape news from BBC and update the global headlines and subtext lists.
    """
    global scraped_headlines, scraped_subtext, scraped_otherReads
    try:
        # Fetch and parse the HTML
        html_text = requests.get('https://www.bbc.com/news').text
        soup = BeautifulSoup(html_text, 'lxml')
        
        # Scrape headlines and subtexts
        headlines = soup.find_all('h2', class_='sc-8ea7699c-3 kwWByH')
        paras = soup.find_all('p', class_='sc-f98732b0-0 iQbkqW')
        other_reads = soup.find_all('h2', class_='sc-8ea7699c-3 dhclWg')
        
        # Extract and store the text
        scraped_headlines = [headline.text.strip() for headline in headlines]
        scraped_subtext = [para.text.strip() for para in paras]
        scraped_otherReads = [other_read.text.strip() for other_read in other_reads]

        # Log the number of items scraped
        print(f"Scraped {len(scraped_headlines)} headlines and {len(scraped_subtext)} subtexts.")
    except Exception as e:
        print(f"Error occurred during scraping: {e}")

@app.route('/news', methods=['GET'])
def get_news():
    """
    API endpoint to fetch the latest scraped news and other reads.
    """
    # Combine headlines and subtexts into a list of dictionaries for main news
    news = [
        {"headline": scraped_headlines[i], "subtext": scraped_subtext[i]}
        for i in range(min(len(scraped_headlines), len(scraped_subtext)))  # Handle mismatch in list lengths
    ]

    # Structure the response with separate keys for main news and other reads
    response = {
        "news": news,  # Main news section
        "other_reads": scraped_otherReads  # Other reads section
    }

    return jsonify(response)



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
