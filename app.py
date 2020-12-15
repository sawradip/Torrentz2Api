from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello_world():
    return "Hello Gal"

def parse_page(search_term):

    base_url = "https://torrentz2eu.me/search.php?q="
    serach_url = base_url + search_term.replace(' ', '+')

    source = requests.get(serach_url).text
    soup = BeautifulSoup(source, 'lxml')
    
    table = soup.find('tbody')

    if table is None:
        return None

    media_list = table.find_all('tr')
    parsed_list = []
    for media in media_list:
        row = {}

        name = media.find('td', {'data-title':'Name'}).span.text
        size = media.find('td', {'data-title':'Size'}).text
        seeders = media.find('td', {'data-title':'Seeds'}).text
        leechers = media.find('td', {'data-title':'Leeches'}).text
        magnet_link = media.a.get("href")

        row['name'] = name
        row['size'] = size
        row['seed'] = seeders
        row['leech'] = leechers
        row['magnet_link'] = magnet_link

        parsed_list.append(row)

    return parsed_list

class Search(Resource):
    def post(self):
        postedData = request.get_json()

        name = postedData["name"]
        year = postedData["year"]

        if ('name' not in postedData):
            retJSON = {
                "status_code":301,
                "message" : "Invalid request! " + name
            }
            print(12)
        else:
            if ('year' not in postedData):
                search_term = name
            else:
                search_term = name + ' ' + year
            print(10)
            parsed_data = parse_page(search_term)

            if (parsed_data is None):
                retJSON = {
                    "status": 302,
                    "message":"No results found"
                }
            else:
                retJSON = {
                    "status": 200,
                    "message":parsed_data
                }
        return jsonify(retJSON)

api.add_resource(Search, '/search')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port='5000', debug = True)

