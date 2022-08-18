import requests
import time
from math import*
# Libraire Panda permet de créer un tableau facilement
import pandas as pd
import os
from bs4 import BeautifulSoup

# ---------------  Fonction pour la création de l'objet soup à partir d'un URL  ---------------

def url_to_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

# --------- Nombre de pages dans la catégorie ---------------

def nombre_de_pages(url):
    soup = url_to_soup(url)
    nb_livres = int(soup.find("form", class_="form-horizontal").find("strong").text)
    nb_pages = ceil(nb_livres/20)
    return nb_pages

# --------- Telechargement des images ------------------------

def telecharger_photo(urls_photos, nom_categorie):
    i = 1
    for image_url in urls_photos:
        f = open("./" + nom_categorie + "/" + nom_categorie + str(i) + '.jpg', 'wb')
        response = requests.get(image_url)
        f.write(response.content)
        f.close()
        i += 1

# ----------- Récupération des URLs d'une page catégorie ------

def scrapping_urls_page(url):
    soup = url_to_soup(url)
    urls = soup.find("section").find_all("h3")
    url_books = []
    for url_book in urls:
        url_books.append("http://books.toscrape.com/catalogue/" + url_book.find("a")['href'][6:].replace("../", ""))
    return url_books

# ------------ Récupération des URLs de toute une catégorie -----

def category_scrapping(url_category_index):
    nb_pages = nombre_de_pages(url_category_index)
    urls_livres_list = []
    if nb_pages == 1:
        urls_livres_list = scrapping_urls_page(url_category_index)
    else:
        for i in range(1, nb_pages+1):
            urls_livres_list.extend(scrapping_urls_page(url_category_index[:-10] + "page-" + str(i) + ".html"))
    return urls_livres_list

# ------------ Récupére les infromations d'une page livre -------

def scrapping_page_livre(url):
    # Récupére la soupe correpondante au tableau
    soup = url_to_soup(url)
    tr_retour = soup.find_all("tr")

    # Ajoute l'URL)
    url_list = url

    # Récupére et ajoute le titre du livre
    title = soup.find("h1").text

    # Recupération UPC
    upc = tr_retour[0].text[4:-2]

    # Price (excel. tax)
    price_no_tax = tr_retour[2].text[19:-2]

    # Price (incl. tax)
    price_with_tax = tr_retour[3].text[19:-2]

    # Availability
    availability = tr_retour[5].text[24:-12]

    # Rating
    rating = soup.find("div", class_="col-sm-6 product_main").find_all("p")[2]["class"][1]

    # Récupére l'URL de l'image
    img_url = "http://books.toscrape.com" + soup.find("img")['src'][5:]

    # Récupére la description
    try:
        description = soup.find(text="Product Description").find_next("p").text
    except AttributeError:
        description = "None"

    # Récupére la catégorie
    category = soup.find("ul", class_="breadcrumb").find_all("a")[2].text

    livre_scrap = [
        url_list, upc, title, price_with_tax, price_no_tax,
        availability, description, category, rating, img_url
    ]
    return livre_scrap

# ----------- Création des dossier par Catégories et des CSV à partir d'un DataFrame PANDAS --------

def scrapping_booktoscrap(url):
    url_books = category_scrapping(url)
    columns = [
        "product_page_url", "universal_ product_code (upc)", "title", "price_including_tax",
        "price_excluding_tax", "number_available", "product_description", "category", "review_rating",
        "image_url"
    ]
    list_scrapping_books = []
    for url_book in url_books:
        list_scrapping_books.append(scrapping_page_livre(url_book))
    df = pd.DataFrame(list_scrapping_books, columns=columns)
    list_categories = df["category"].drop_duplicates().to_list()
    for category in list_categories:
        if not os.path.exists(category):
            os.makedirs(category)
        df_mask = df["category"] == category
        category_df = df[df_mask]
        category_df.to_csv("./" + category + "/" + category + ".csv", encoding="utf-16")
        telecharger_photo(category_df["image_url"].to_list(), category)


url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
t_start = time.time()
scrapping_booktoscrap(url)
t_end = time.time()
print(t_end - t_start)
