from selenium import webdriver
import pandas as pd
import os
from datetime import date
import datetime


def scrap_news():
    # getting csv.
    newdf = pd.read_csv('../news_urls/elmundo_urls.csv', index_col=0)
    newurls = newdf['link'].tolist()
    keywordlist = newdf['keyword'].tolist()

    try:
        archivo = pd.read_csv("../DATA_news/elmundo_data.csv", index_col=0)
    except:
        dictarchivo = {'link': [], 'keyword': [], 'newspaper': [], 'title': [], 'date': [], 'text': [], 'author': []}
        archivo = pd.DataFrame(dictarchivo)

    try:
        oldurls = archivo['link'].tolist()
        newurls = [url for url in newurls if url not in oldurls]
    except:
        pass

    titles = []
    dates = []
    content = []
    author = []
    keywords = []

    for e in newurls:

        keywords.append(keywordlist[newurls.index(e)])

        # driver config
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path="../drivers/chromedriver", chrome_options=chrome_options)
        driver.get(e)

        # extracting important data
        try:
            titles.append(str(driver.find_element_by_css_selector('#H1_js_5e0a1bb4fdddffc8888b4625').text))

        except:
            try:
                titles.append(str(driver.find_element_by_xpath('//*[@id="H1_js_5e5ba90021efa0ad2d8b468e"]').text))

            except:
                try:
                    titles.append(str(driver.find_element_by_tag_name('h1').text))
                except:
                    titles.append('None')

        try:
            dates.append(str(driver.find_element_by_css_selector('.ue-c-article__publishdate > time:nth-child(2)').text))

        except:
            dates.append('None')

        try:
            content.append(str(driver.find_element_by_css_selector('.ue-l-article__body').text))

        except:
            content.append('None')

        try:
            author.append(str(driver.find_element_by_css_selector('.ue-c-article__byline-name').text))

        except:
            author.append('None')

        # checking if variables have the same length
        if len(titles) == len(dates) == len(content) == len(author):
            print("Vamos bien")

        else:
            print("Algo va mal")

        driver.close()

    # newdf
    dictdf = {'link': newurls, 'keyword': keywords, 'newspaper': "elmundo", 'title': titles, 'date': dates, 'text': content,
              'author': author}
    newdf = pd.DataFrame(dictdf)
    lista = newdf['link'].tolist()

    if lista != []:
        frames = archivo, newdf
        newdf = pd.concat(frames)
    else:
        newdf = archivo

    newdf.drop_duplicates(keep=False, inplace=True)
    newdf = newdf.reset_index(drop=True)

    # saving df as .csv
    today = date.today()
    nombre_archivo = 'elmundo_data' + '.csv'
    path = '../DATA_news'
    archivo_de_salida = os.path.join(path, nombre_archivo)
    newdf.to_csv(archivo_de_salida)

    return None


def pipeline(lista_keywords):
    starttime = datetime.datetime.now()

    url_extractor(lista_keywords)
    concatenator()
    scrap_news()

    endtime = datetime.datetime.now()
    duration = endtime - starttime
    print(duration)

scrap_news()