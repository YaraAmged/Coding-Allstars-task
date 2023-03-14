import os

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from googletrans import Translator

translator = Translator()
INDEX_FILE_PATH = "./Watch anime online, English anime online - Gogoanime.html"

originalHomePage = open(INDEX_FILE_PATH).read()


def translate_page(html):
    html_soap = BeautifulSoup(html, "html.parser")
    elementsMap = list()
    for ele in html_soap.find_all():
        if ele.name in ["style", "script"]:
            continue
        for i in range(0, len(ele.contents)):
            subEle = ele.contents[i]
            if isinstance(subEle, NavigableString) and len(subEle) > 1:
                elementsMap.append([ele, subEle.string])
    # translate element in iterations
    elementPerIteration = min(20, len(elementsMap))
    print(len(elementsMap))
    iterations = int(len(elementsMap) / elementPerIteration)

    for i in range(0, iterations):
        iterationElements = elementsMap[i *
                                        elementPerIteration:(i + 1)*elementPerIteration]
        print("iteration " + str(i) + " of " + str(iterations))
        results = translator.translate(
            [ele[1] for ele in iterationElements], dest="hi")
        for i in range(0, len(iterationElements)):
            iterationElements[i][0].string = results[i].text

    return str(html_soap)


def writeFile(folderPath, fileName, data):
    if not os.path.exists(folderPath):
        os.makedirs("./output")
    open(folderPath + "/" + fileName, 'w').write(data)


translatedHomePage_soap = BeautifulSoup(
    translate_page(originalHomePage), "html.parser")

anchorTagsOneLevelDeep = translatedHomePage_soap.find_all("a")
for i in range(0, len(anchorTagsOneLevelDeep)):
    ele = anchorTagsOneLevelDeep[i]
    href = ele.get("href")
    if isinstance(ele, Tag) and href is not None and "/" in href:
        if href.startswith("http"):
            res = requests.get(href)
            translatedFile = translate_page(res.text)
    else:
        hrefHtml = open(href).read()
        translatedFile = translate_page(hrefHtml)
        writeFile("./output", str(i)+".html", translatedFile)
        ele["href"] = "./"+str(i)+".html"

writeFile("output", "index.html", str(translatedHomePage_soap))
