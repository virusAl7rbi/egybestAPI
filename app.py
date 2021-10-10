from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup, SoupStrainer
import requests
import json
import re

app = Flask(__name__)
CORS(app)

def get_all_episode(url):
    base_url = 'https://lack.egybest.org'
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    e_urls = []
    for e in soup.find_all('a', {'class': 'movie'}):
        soup = BeautifulSoup(requests.get(e['href']).text, 'lxml')
        if soup.find('iframe', {'class': 'auto-size'}):
            iframe = soup.find('iframe', {'class': 'auto-size'})['src']
            time_for_e = soup.find_all('td')[12].text
            e_num = e['href'].split('/')[4].split('-ep-')[1]
            rate = soup.find('span', {'itemprop': 'ratingValue'}).text
            data = f"{base_url}{iframe}"
            e_urls.append({
                "number": str(e_num),
                "url": str(data),
                "time": str(time_for_e),
                "rate": str(rate)
            })
    return e_urls


@app.route('/search')
def main():
    result = []
    search_query = str(request.args.get('q')).replace(' ', '%20')
    search_url = f"https://lack.egybest.org/explore/?q={search_query}"
    print(search_url)
    base_url = 'https://lack.egybest.org'
    req = requests.get(search_url).text
    print(req)
    soup = BeautifulSoup(req, 'lxml')
    print(soup)
    main_url = []
    for res in soup.find_all('a', {'class': 'movie'}):
        print(res)
        print(res['href'])
        url = res['href'][:-15]
        main_url.append(url)
    for url in main_url:
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        if url.split("/")[3] == "movie" and soup.find('iframe', {'class': 'auto-size'}):
            watch_url = base_url + soup.find('iframe', {'class': 'auto-size'})['src']
            soup = BeautifulSoup(requests.get(url).text, 'lxml')
            tittle = url.split("/")[4]
            image = "https:" + soup.find('img')['src']
            rate = soup.find('span', {'itemprop': 'ratingValue'}).text
            _type = url.split("/")[3]
            time = soup.find_all('td')[10].text

            data = {
                "title": tittle,
                "image": image,
                "type": _type,
                "rate": rate,
                "time": time,
                "url": watch_url
            }
            result.append(data)
        elif url.split("/")[3] == "series":
            soup = BeautifulSoup(requests.get(url).text, 'lxml')
            sessons = soup.find_all('div', {'class': 'contents movies_small'})
            _type = url.split("/")[3]
            for i in sessons:
                urls = i.find_all('a', {'class': 'movie'})
                for x in urls:
                    if re.search('/season/', str(x)):
                        s_num = x['href'].split('/')[4].split('-season-')[1].split('-')[0]
                        result.append({
                            "season": str(s_num),
                            "type": _type,
                            "episodes": get_all_episode(x['href']),
                            "title": x.find('img')['alt'],
                            "url": x['href'],
                            "image": "https:" + x.find('img')['src'],
                        })
    return jsonify(result)

def test(query):
    main_url = "https://lack.egybest.org"
    search_url = f"{main_url}/explore/?q={query}"
    page_contnet = requests.get(search_url, timeout=3).content
    soup = BeautifulSoup(page_contnet, "lxml", parse_only=SoupStrainer(id="movies"))
    # print(soup)
    for banner in soup.find_all("a"):
        rate = banner.find("i").find('i').text if banner.find("i") else '0'
        try:
            img = banner.find("img")['src']
        except:
            print(banner)

        title = banner.find_all('span')[1].text
        url = banner["href"]
        _type = re.findall(f"{main_url}/(.*)/?", url)[0].split('/')[0]
        print(f"title : {title}\nimg: {img}\nrate: {rate}/10\nurl: {url}\ntype: {_type}\n\n")

test("joker")