# omdb_service.py
import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get OMDb API key
API_KEY = os.getenv("OMDB_API_KEY")
OMDB_URL = "http://www.omdbapi.com/"


def fetch_movie_data(title):
    """
    Fetch raw movie data from OMDb API by title.

    Args:
        title (str): The movie title to search for

    Returns:
        dict: Raw JSON response from OMDb or error dict
    """
    if not API_KEY:
        logger.error("❌ OMDb API key is missing.")
        return {"Error": "OMDb API key not found."}

    try:
        url = f"{OMDB_URL}?apikey={API_KEY}&t={title}"
        logger.info(f"🔍 Fetching data for '{title}' from OMDb...")
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                logger.info(f"✅ Successfully fetched data for '{title}'")
                return data
            else:
                error_msg = data.get("Error", "Movie not found")
                logger.warning(f"⚠️ OMDb returned an error: {error_msg}")
                return {"Error": error_msg}
        else:
            logger.error(f"🔴 Failed with status code {response.status_code}")
            return {"Error": f"Request failed with status code {response.status_code}"}

    except Exception as e:
        logger.exception(f"🔥 Error fetching data for '{title}': {e}")
        return {"Error": str(e)}


def extract_movie_data(raw_data):
    """
    Extract relevant fields from raw OMDb response.

    Args:
        raw_data (dict): Raw data from OMDb

    Returns:
        dict: Processed movie data with keys matching ORM fields
    """
    try:
        # Grab fields, providing sensible defaults
        title    = raw_data.get("Title", "N/A")
        director = raw_data.get("Director", "N/A")
        year_str = raw_data.get("Year", "0")
        genre    = raw_data.get("Genre", "N/A")
        rating_str = raw_data.get("imdbRating", "0")
        poster   = raw_data.get("Poster", "")

        # Convert types
        year   = int(year_str) if year_str.isdigit() else 0
        rating = float(rating_str) if rating_str.replace('.', '', 1).isdigit() else 0.0

        return {
            "id":      raw_data.get("imdbID", ""),
            "name":    title,
            "director": director,
            "year":    year,
            "rating":  rating,
            "genre":   genre,
            "poster":  poster
        }
    except Exception as e:
        logger.exception(f"🔥 Error extracting data: {e}")
        return {"Error": str(e)}


# ==================== #
#     Test Function    #
# ==================== #

if __name__ == "__main__":
    print("🎬 OMDb Service Test Script")
    print("----------------------------")

    movie_title = input("Enter a movie title to search on OMDb: ").strip()
    if not movie_title:
        print("❗ No title entered. Exiting.")
    else:
        raw_data = fetch_movie_data(movie_title)
        if raw_data and "Error" not in raw_data:
            movie_data = extract_movie_data(raw_data)
            print("\n✅ Movie Data Retrieved:\n")
            for key, value in movie_data.items():
                print(f"{key}: {value}")
        else:
            print("\n❌ Failed to retrieve movie data:")
            print(raw_data.get("Error", "Unknown error"))