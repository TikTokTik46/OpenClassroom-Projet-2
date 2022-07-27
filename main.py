import requests
import csv
from bs4 import BeautifulSoup

url_bookstoscrape = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'


# Fontcion pour la création de l'objet soup à partir d'un URL
def url_to_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

# ------------- Scrapping de la page ----------

def scrapping_page_livre(url):

#Récupére la soupe
    soup = url_to_soup(url_bookstoscrape)

# Récupére les informations du tableau
    tableau_info = {}
    th_tables = soup.find_all("th")
    td_tables = soup.find_all("td")
    for th_table, td_table in zip(th_tables, td_tables):
        tableau_info[th_table.string] = td_table.string

# Ajoute l'URL de la page
    book_info = {"product_page_url": url_bookstoscrape}

# Ajoute l'UPC depuis le tableau
    book_info["universal_ product_code (upc)"] = tableau_info["UPC"]

    # Récupére et ajoute le titre du livre
    titles = soup.find_all("h1")
    for title in titles:
        book_info["title"] = title.string

    # Ajoute les prix et le nombre de produits disponible depuis le tableau
    book_info["price_including_tax"] = tableau_info["Price (incl. tax)"]
    book_info["price_excluding_tax"] = tableau_info["Price (excl. tax)"]
    book_info["number_available"] = tableau_info["Availability"]

    # Récupére la description du livre
    descriptions = soup.find_all("p")
    book_info["product_description"] = str(descriptions[3])[3:-3]

    # Récupére la catégorie du livre
    categories = soup.find_all("a")
    for categorie in categories:
        book_info["category"] = categorie.string

    # Ajoute le review ratting depuis le tableau
    book_info["review_rating"] = tableau_info["Number of reviews"]

    # Récupére l'URL de l'image
    pictures = soup.find_all("img")
    for picture in pictures:
        book_info["image_url"] = picture["src"]


print(book_info)
en_tete = list(book_info)
books_info = [book_info]

# Créer un nouveau fichier pour écrire dans le fichier appelé « data.csv »
with open('data.csv', 'w') as fichier_csv:
    # Créer un objet writer (écriture) avec ce fichier
    writer = csv.DictWriter(fichier_csv, fieldnames=en_tete)
    writer.writeheader()
    for elem in books_info:
        writer.writerow(elem)
