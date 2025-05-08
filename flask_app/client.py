import requests


import requests

class BookClient:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1/volumes"

    def search_books(self, query, max_results=30):
        params = {"q": query, "maxResults": max_results}
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []

    def retrieve_book_by_id(self, book_id):
        url = f"{self.base_url}/{book_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
