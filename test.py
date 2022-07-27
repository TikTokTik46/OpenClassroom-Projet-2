import requests
import numpy as np
from math import*
# Libraire Panda permet de créer un tableau facilement
import pandas as pd
from bs4 import BeautifulSoup

# ---------------  Fontcion pour la création de l'objet soup à partir d'un URL  ---------------

def url_to_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

# ------------- Scrapping de la page ----------

def scrapping_page_livre(url):
    # Récupére la soupe correpondante au tableau
    soup = url_to_soup(url)
    tr_retour = soup.find_all("tr")

    # Ajoute l'URL)
    url_list = url

    # Récupére et ajoute le titre du livre
    title = soup.find_all("h1")[0].text

    # Recupération UPC
    UPC = tr_retour[0].text[4:-2]

    # Price (excel. tax)
    Price_no_tax = tr_retour[2].text[19:-2]

    # Price (incl. tax)
    Price_with_tax = tr_retour[3].text[19:-2]

    # Availability
    availability = tr_retour[5].text[24:-12]

    # Rating
    rating = soup.find("div", class_="col-sm-6 product_main").find_all("p")[2]["class"][1]

    # Récupére l'URL de l'image
    img_url = soup.find("img")['src']

    # Récupére la description
    description = soup.find("div", id="content_inner").find_all("p")[3].text

    # Récupére la catégorie
    category = soup.find("ul", class_="breadcrumb").find_all("a")[2].text

    livre_scrap = {"product_page_url": url_list, "universal_ product_code (upc)": UPC, "title": title,
                   "price_including_tax": Price_with_tax, "price_excluding_tax": Price_no_tax,
                   "number_available": availability, "product_description": description, "category": category,
                   "review_rating": rating, "image_url": img_url}
    return livre_scrap

# ------------ Scrapping URL des livres d'une page catégorie ---

def scrapping_urls_page(url):
    soup = url_to_soup(url)
    urls = soup.find("section").find_all("h3")
    url_books = []
    for url_book in urls:
         url_books.append("http://books.toscrape.com/catalogue/" + url_book.find("a")['href'][9:])
    return url_books

# ----------- Scrapping des catégories -------

def scrapping_categories(url):
    soup = url_to_soup(url)
    categories_soup = soup.find("ul", class_="nav nav-list").find("ul").find_all("li")
    dict_categories = {}
    for categorie in categories_soup:
        dict_categories[categorie.find("a").text[62:-54]] = "http://books.toscrape.com/catalogue/category/" + categorie.find("a")['href'][19:]
    return dict_categories

# --------- Nombre de pages dans la catégorie -------------

def nombre_de_pages(url):
    soup = url_to_soup(url)
    nb_livres = int(soup.find("form", class_="form-horizontal").find("strong").text)
    nb_pages = ceil(nb_livres/20)
    return nb_pages

# --------- Ecrire les données dans le CSV -------------

def export_csv(dict_info,nom_csv="default"):
    dataset = pd.DataFrame.from_dict(dict_info)
    print(dataset)
    dataset.to_csv(nom_csv+".csv")

#----- Concatener les donnés de plusieurs pages url de catégories sur un DICT -------

def concatener_les_infos(url_liste):
    tableau_scrapping = {}
    for url in url_liste:
        scrap_page = scrapping_page_livre(url)
        for key in scrap_page.keys():
            tableau_scrapping.setdefault(key, []).append(scrap_page[key])
    return tableau_scrapping

#--------- Récupérer toutes les URL d'une catégorie a partir de l'URL de sa page index--------

def category_scrapping(url_category_index):
    nb_pages = nombre_de_pages(url_category_index)
    urls_livres_list = []
    if nb_pages == 1:
        urls_livres_list = scrapping_urls_page(url_category_index)
    else:
        for i in range(1, nb_pages+1):
            urls_livres_list.extend(scrapping_urls_page(url_category_index[:-10]+"page-" + str(i) + ".html"))
    return urls_livres_list


#------------- FINAL BOSS : Récupérer toutes les informations de booktoscrape par catégorie sur des CSV différent -----

def booktoscrape_scrapping(url_booktoscrape):
    categories = scrapping_categories(url_booktoscrape)
    nom_categories = list(categories.keys())
    url_categories = list(categories.values())
    for i in range(len(nom_categories)):
        books_url = category_scrapping(url_categories[i])
        concatener_books_categorie = concatener_les_infos(books_url)
        export_csv(concatener_books_categorie, nom_categories[i])
        print(concatener_books_categorie)
    return books_url


url = "http://books.toscrape.com/index.html"
print(booktoscrape_scrapping(url))

