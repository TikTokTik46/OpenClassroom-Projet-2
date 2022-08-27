import requests
import time
from math import*
import pandas as pd
import os
import concurrent.futures
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

#------------- Liste index / url image -----------

def liste_index_url_image (df):
    list_index = df.index.values.tolist()
    list_url = df["image_url"].to_list()
    liste_index_url = list(zip(list_index, list_url))
    return liste_index_url

# --------- Telechargement des images ------------------------

def telecharger_des_photos(url_index_liste, nom_categorie):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda x: telecharger_une_photo(nom_categorie, x), url_index_liste)

# --------- Telechargement une image ------------------------

def telecharger_une_photo (nom_categorie, url_index_liste):
    f = open("./" + nom_categorie + "/" + nom_categorie + "_" + str(url_index_liste[0]) + '.jpg', 'wb')
    response = requests.get(url_index_liste[1])
    f.write(response.content)
    f.close()

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
    t0 = time.time()
    url_books = category_scrapping(url)
    columns = [
        "product_page_url", "universal_ product_code (upc)", "title", "price_including_tax",
        "price_excluding_tax", "number_available", "product_description", "category", "review_rating",
        "image_url"
    ]
    list_scrapping_books = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda x: list_scrapping_books.append(scrapping_page_livre(x)), url_books)
    df = pd.DataFrame(list_scrapping_books, columns=columns)
    t1 = time.time()
    print("Temps scrapping : "+ str (t1-t0))
    list_categories = df["category"].drop_duplicates().to_list()
    for category in list_categories:
        if not os.path.exists(category):
            os.makedirs(category)
        df_mask = df["category"] == category
        category_df = df[df_mask].reset_index(drop=True)
        category_df.to_csv("./" + category + "/" + category + ".csv", encoding="utf-16")
        telecharger_des_photos(liste_index_url_image(category_df), category)
    print("Temps téléchargement des images : " + str(time.time()-t1))


url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
t_start = time.time()
scrapping_booktoscrap(url)
t_end = time.time()
print("Temps d'exécution du script : " + str(t_end - t_start))
