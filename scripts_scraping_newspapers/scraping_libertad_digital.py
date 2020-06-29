from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
import glob
import os
from datetime import date
import datetime
import re


def url_extractor(lista):
    print("libertad digital...")
    # select every keyword in the list
    for keyword in lista:

        # spaces to %20, we want it to change urls.
        keyword.replace(" ", "%20")
        listing_links = []
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path="../drivers/chromedriver", chrome_options=chrome_options)
        driver.get(
            'https://www.libertaddigital.com/c.php?op=buscar&cof=FORID%3A11&ie=ISO-8859-1&q='
            + keyword + '#gsc.tab=0&gsc.q=' + keyword + '&gsc.page=1')

        print('buscando con... ' + keyword)

        time.sleep(0.5)
        try:
            # with this, the mouse move over a button, to simulate human move to not to be banned.
            action = ActionChains(driver)
            onit = driver.find_element_by_xpath('//*[@id="cmp-main-message"]/div/div[3]/span[2]/button/span')
            time.sleep(0.1)
            action.move_to_element(onit).perform()
            time.sleep(0.1)
            onit.click()
        except:
            continue

        duplicate = 0
        # save urls if does not exist
        links = driver.find_elements_by_class_name('gs-title')
        for link in links:
            time.sleep(0.1)
            listing_links.append(str(link.get_attribute('href')))

        # Getting number of labes
        time.sleep(0.1)
        labels = driver.find_elements_by_css_selector(".gsc-cursor .gsc-cursor-page")

        # get number of labels
        pagenumbers = 0
        for label in labels:
            time.sleep(0.1)
            pagenumbers = int(label.text) + 1

        # Working on every label
        for e in range(2, pagenumbers):
            time.sleep(0.5)
            print(e)
            fixlabel = 0
            labels = driver.find_elements_by_css_selector(".gsc-cursor .gsc-cursor-page")
            try:
                for label in labels:
                    time.sleep(0.1)
                    fixlabel = int(label.text) + 1
            except:
                continue
            time.sleep(0.1)

            # extract non-existent urls in every label, if the driver is in the last one, close.
            if e == fixlabel:
                links = driver.find_elements_by_class_name('gs-title')
                for link in links:
                    time.sleep(0.1)
                    listing_links.append(str(link.get_attribute('href')))
                driver.close()
                break

            else:
                # scroll to pop up buttons.
                actions = ActionChains(driver)
                for _ in range(3):
                    actions.send_keys(Keys.PAGE_DOWN).perform()
                    time.sleep(0.3)

                links = driver.find_elements_by_class_name('gs-title')
                for link in links:
                    try:
                        listing_links.append(str(link.get_attribute('href')))
                    except:
                        time.sleep(1)
                        try:
                            listing_links.append(str(link.get_attribute('href')))
                        except:
                            continue
                time.sleep(0.1)

                # with this, the mouse move over a button, to simulate human move to not to be banned.
                try:
                    action2 = ActionChains(driver)
                    onit2 = driver.find_element_by_xpath('//*[@id="___gcse_1"]/div/div/div/div[5]/div[2]/div['
                                                         '1]/div/div[ '
                                                         '2]/div/div[' + str(e) + ']')
                    time.sleep(0.1)
                    action2.move_to_element(onit2).perform()
                    time.sleep(0.1)
                    onit2.click()

                except:
                    try:
                        # this one is like a double tap, sometimes the page doesn't get the first.
                        WebDriverWait(driver, 10).until(
                            ec.element_to_be_clickable((By.XPATH, '//*[@id="___gcse_1"]/div'
                                                                  '/div/div/div[5]/div['
                                                                  '2]/div[1]/div/div['
                                                                  '3]/div/div[' + str(e)
                                                        + ']'))).click()
                    except:
                        continue

        # cleaning listing_links
        listing_links = [x for x in listing_links if x != 'None']
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
        today = date.today()
        nombre_archivo = keyword + ' ' + status + '.csv'
        path = '../news_urls/libertaddigital_urls'
        archivo_de_salida = os.path.join(path, nombre_archivo)
        df.to_csv(archivo_de_salida)

        # try to close the driver if is not.
        try:
            driver.close()
        except:
            continue
    return None


def concatenator():
    # this one make a concatenation of the links of each keyword
    path = '../news_urls/libertaddigital_urls'
    e = glob.glob(path + "/*.csv")
    dfs = []
    for i in e:
        dfs.append(pd.read_csv(i))

    scrap_total = pd.concat(dfs, axis=0)
    scrap_total = scrap_total[['link', 'keyword', 'status']]

    scrap_total.to_csv('../news_urls/libertad_digital_urls.csv')

    return None


def scrap_news():
    # getting csv.
    newdf = pd.read_csv('../news_urls/libertad_digital_urls.csv', index_col=0)
    newurls = newdf['link'].tolist()
    keywordlist = newdf['keyword'].tolist()

    try:
        archivo = pd.read_csv("../DATA_news/libertad_digital_data.csv", index_col=0)
    except:
        dictarchivo = {'link': [],'keyword': [], 'newspaper': [], 'title': [], 'date': [], 'text': [], 'author': []}
        archivo = pd.DataFrame(dictarchivo)

    try:
        oldurls = archivo['link'].tolist()
        newurls = [url for url in newurls if url not in oldurls]
    except:
        pass

    urls = list(dict.fromkeys(newurls))
    titles = []
    dates = []
    content = []
    author = []
    keywords = []
    count = 1

    # pick link column to iterate links.
    for e in newurls:

        time.sleep(0.5)
        keywords.append(keywordlist[newurls.index(e)])

        # if and elif to avoid urls with useless images, commits, etc.
        if re.findall('bitacora', e):
            titles.append('None')
            dates.append('None')
            content.append('None')
            author.append('None')

            continue

        elif re.findall('.jpg', e):
            titles.append('None')
            dates.append('None')
            content.append('None')
            author.append('None')

            continue

        elif re.findall('/foros/', e):
            titles.append('None')
            dates.append('None')
            content.append('None')
            author.append('None')

            continue

        elif re.findall('www.libremercado.com', e):
            titles.append('None')
            dates.append('None')
            content.append('None')
            author.append('None')

            continue

        elif re.findall('/fonoteca/', e):
            titles.append('None')
            dates.append('None')
            content.append('None')
            author.append('None')

            continue

        else:
            # this take the urls with \d.html to split and select the first part of the split.
            if re.findall('(\/\d.html)', e):
                e = e.rsplit('/', 1)[0]

            else:
                pass
            print(str(count) + '/' + str(len(newurls)))
            count = count + 1

            # driver config
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(executable_path="../drivers/chromedriver", chrome_options=chrome_options)
            driver.get(e)

            # extraction
            try:
                titles.append(str(driver.find_element_by_tag_name('h1').text))

            except:
                titles.append('None')

            try:
                dates.append(str(driver.find_element_by_tag_name('time').text))

            except:
                dates.append('None')

            try:
                contenido = str(driver.find_element_by_class_name('.texto > span:nth-child(2) > p:nth-child(1)').text)
            except:
                contenido = ''
            try:
                content.append(str(driver.find_element_by_css_selector(
                    '#infinito > div > div.contenedor.conlateral > div:nth-child(1) > div.texto.principal.selectionShareable > span').text))

            except:
                try:
                    content.append(str(driver.find_element_by_css_selector(
                        'body > div.contenedor.interior > div.contenedor.conlateral > div:nth-child(1) > div.texto.principal.selectionShareable > span').text))

                except:
                    try:
                        content.append(str(driver.find_element_by_css_selector(
                            'body > div.interior.suplemento > div.contenedor.conlateral > div:nth-child(1) > div.texto.principal.selectionShareable').text))
                    except:
                        content.append('None')
                        print("No hay contenido extraible en " + e)
            try:
                author.append(str(driver.find_element_by_class_name('firma').text))
            except:
                author.append('None')
                time.sleep(0.2)


        driver.close()

    # newdf
    dictdf = {'link': newurls,'keyword': keywords, 'newspaper': "libertad_digital", 'title': titles, 'date': dates, 'text': content,
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

    # fixing covid 19 advice
    try:
        newdf['content'] = newdf['content'].str.replace('^Necesitamos tu colaboraci.*', '', regex=True)
        newdf['content'] = newdf['content'].str.replace('^Si eres seguidor de Libertad.*', '', regex=True)
        newdf['content'] = newdf['content'].str.replace('^Por la emergencia del coronavirus.*', '', regex=True)
        newdf['content'] = newdf['content'].str.replace('^QUIERO COLABORAR.*', '', regex=True)

    except:
        pass

    # saving the df as .csv
    nombre_archivo = 'libertad_digital_data' + '.csv'
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
