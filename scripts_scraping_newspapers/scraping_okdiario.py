import os
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from selenium.webdriver.common.keys import Keys
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import glob
from selenium.webdriver.firefox.options import Options


def url_extractor(lista):
    print("okdiario...")
    # select every keyword in the list
    for keyword in lista:
        listing_links = []
        missmatch = 0
        duplicate = 0

        # reading csv to check existing links
        try:
            archivo = "../news_urls/okdiario_urls/" + keyword + " Éxito en la búsqueda.csv"

        except:
            archivo = "../news_urls/okdiario_urls/" + keyword + " No hay resultados para: " + keyword + ".csv"

        try:
            df = pd.read_csv(archivo)

        except:
            df = pd.DataFrame([], columns=['link'])  # if df do not exist, make a new one.

        # transform the .csv to list
        dflist = df['link'].tolist()

        # setting driver
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(executable_path="../drivers/geckodriver", options=options)
        driver.get('https://okdiario.com/buscador/?q=' + keyword)

        print('buscando con... ' + keyword)

        # arrange the news by date
        driver.find_element_by_class_name('gsc-option-selector').click()
        time.sleep(0.1)
        driver.find_element_by_xpath("//*[text()='Date']").click()
        time.sleep(0.1)

        # If the keyword is misspelled, this find the google suggestion
        resultados = driver.find_elements_by_css_selector('div.gs-spelling:nth-child(2)')

        for i in resultados:
            if i.text == 'Ver resultados de ' + keyword:
                print('no se ha podido encontrar resultados con la keyword, posiblemente esté mal escrita: ' + keyword)
                missmatch = 1

            else:
                # saving links
                links = driver.find_elements_by_class_name('gs-title')
                for link in links:
                    # if the link is an existing link, stop the loop and set duplicate to 1
                    if str(link.get_attribute('href')) in dflist:
                        duplicate = 1
                        break

                    else:
                        listing_links.append(str(link.get_attribute('href')))


        # Getting number of labels
        labels = driver.find_elements_by_css_selector(".gsc-cursor")
        pagenumbers = 0
        for label in labels:
            time.sleep(0.1)
            pagenumbers = int(label.text) + 1

        # Working on every label
        for e in range(2, pagenumbers):
            # if we reach an existing link, the loop stop
            if duplicate == 1:
                break
            else:
                pass
            time.sleep(1)

            # find labels
            labels = driver.find_elements_by_css_selector(".gsc-cursor .gsc-cursor-page")

            # fixing the mismatching label
            fixlabel = 0
            for label in labels:
                time.sleep(0.1)
                fixlabel = int(label.text) + 1

            # no results or misspelled keyword close the driver.
            if missmatch == 1:
                driver.close()
                break

            # extract non-existent urls in every label, if the driver is in the last one, close.
            elif e >= fixlabel:
                links = driver.find_elements_by_class_name('gs-title')
                for link in links:
                    if str(link.get_attribute('href')) in dflist:
                        duplicate = 1
                        break

                    else:
                        listing_links.append(str(link.get_attribute('href')))

                driver.close()
                break
            else:
                # scroll down 3 times to pop up the labels buttons
                actions = ActionChains(driver)
                for _ in range(3):
                    actions.send_keys(Keys.PAGE_DOWN).perform()
                    time.sleep(0.1)

                links = driver.find_elements_by_class_name('gs-title')
                for link in links:
                    if str(link.get_attribute('href')) in dflist:
                        duplicate = 1
                        break

                    else:
                        listing_links.append(str(link.get_attribute('href')))

                WebDriverWait(driver, 1000000).until(ec.element_to_be_clickable((By.XPATH,
                                                                                 '/html/body/div[2]/div[2]/div/div['
                                                                                 '2]/div/div/div/div/div[5]/div['
                                                                                 '2]/div/div/div[2]/div/div[' + str(
                                                                                     e) + ']'))).click()
                time.sleep(1)

        # cleaning listing_links, cleaning Nones, adding new links to existing links, and dropping duplicates
        listing_links = [x for x in listing_links if x != 'None']
        listing_links = listing_links + dflist
        listing_links = list(dict.fromkeys(listing_links))

        # creating status
        if len(listing_links) == 0:
            status = 'No hay resultados para: ' + keyword

        else:
            status = "Éxito en la búsqueda"

        # Making the DF
        df = pd.DataFrame(listing_links, columns=['link'])
        df['keyword'] = keyword
        df['status'] = status

        # Saving as .csv
        nombre_archivo = keyword + ' ' + status + '.csv'
        path = '../news_urls/okdiario_urls'
        archivo_de_salida = os.path.join(path, nombre_archivo)
        df.to_csv(archivo_de_salida)

        try:
            driver.close()

        except:
            continue

    return None


def concatenator():
    # this one make a concatenation of the links of each keyword
    path = '../news_urls/okdiario_urls'
    e = glob.glob(path + "/*.csv")
    dfs = []
    for i in e:
        dfs.append(pd.read_csv(i))

    scrap_total = pd.concat(dfs, axis=0)
    scrap_total = scrap_total[['link', 'keyword']]

    scrap_total.to_csv('../news_urls/okdiario_urls.csv')

    return


def scrap_news():
    # getting csv.
    newdf = pd.read_csv('../news_urls/okdiario_urls.csv', index_col=0)
    newurls = newdf['link'].tolist()
    keywordlist = newdf['keyword'].tolist()

    try:
        archivo = pd.read_csv("../DATA_news/okdiario_data.csv", index_col=0)
    except:
        dictarchivo = {'link': [], 'newspaper': [], 'title': [], 'date': [], 'text': [], 'author': [], 'keyword': []}
        archivo = pd.DataFrame(dictarchivo)

    try:
        oldurls = archivo['link'].tolist()
        newurls = [url for url in newurls if url not in oldurls]
    except:
        pass

    titles = []
    dates = []
    content = []
    autor = []
    keywords = []
    newspaper = []
    count = 1

    # pick link column to iterate links.
    for e in newurls:
        print(str(count) + '/' + str(len(newurls)))
        count = count + 1
        keywords.append(keywordlist[newurls.index(e)])

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path="../drivers/chromedriver", chrome_options=chrome_options)
        driver.get(e)


        # extraction
        try:
            titles.append(str(driver.find_element_by_class_name('entry-title').text))
        except:
            titles.append('None')

        try:
            dates.append(str(driver.find_element_by_class_name('date').text))
        except:
            dates.append('None')

        try:
            contenido = str(driver.find_element_by_class_name('entry-content').text)
            content.append(contenido)
        except:
            contenido = "None"
            content.append(contenido)

        try:
            autor.append(str(driver.find_element_by_xpath('//*[@id="postContent"]/article/section[1]/address/ul/li['
                                                          '1]/strong/a').text))
        except:
            autor.append('None')
            time.sleep(0.2)

        newspaper.append('okdiario')
        driver.close()

    # newdf
    dictdf = {'link': newurls, 'keyword': keywords, 'newspaper': newspaper, 'title': titles, 'date': dates, 'text': content, 'author': autor}
    newdf = pd.DataFrame(dictdf)
    lista = newdf['link'].tolist()

    if lista != []:
        frames = archivo, newdf
        newdf = pd.concat(frames)
    else:
        newdf = archivo

    newdf.drop_duplicates(keep=False, inplace=True)
    newdf = newdf.reset_index(drop=True)

    # save the df as .csv
    nombre_archivo = 'okdiario_data' + '.csv'
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
