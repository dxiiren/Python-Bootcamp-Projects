from flask import Flask, request, render_template
import requests

app = Flask(__name__)

#JOKE API
class JokeAPI:

    #Dictionary for languages
    language = {"english": "en", "czech": "cs", "german": "de", "spanish": "es", "french": "fr"}

    #List of joke categories
    category = ["Programming", "Misc", "Dark", "Pun", "Spooky", "Christmas"]

    def __init__(self):
        self.base_url = "https://v2.jokeapi.dev/joke/"

    def displayJoke(self,url):

        try:
            # Call the API by opening the url and reading the data.
            response = requests.get(url)

            # Initialize an empty variable to store jokes
            joke_text = ""
            title = "\n~ The Joke ~\n"

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                joke_data = response.json()

                #for cases there is multiple joke
                if 'jokes' in joke_data:
                    # If 'jokes' key exists, treat it as multiple jokes
                    for joke in joke_data['jokes']:
                        if joke["type"] == "single":
                            joke_text += f"\nThe joke: {joke['joke']}\n"
                        else:
                            joke_text += title + f"\nFirst Part\t: {joke['setup']}\nSecond part\t: {joke['delivery']}\n"

                else:
                    # If 'jokes' key doesn't exist, treat it as a single joke
                    if joke_data["type"] == "single":
                        joke_text = f"\nThe joke: {joke_data['joke']}\n"
                    else:
                        joke_text = title + f"\nFirst Part\t: {joke_data['setup']}\nSecond part\t: {joke_data['delivery']}\n"                
                    
                return joke_text
            else:
                return {"error": "Failed to fetch a joke from the JokeAPI."}

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}
        
    def randomJoke(self):
        url = self.base_url + "Any?blacklistFlags=nsfw,religious,racist,sexist,explicit&format=json"
        return self.displayJoke(url)
    
    def specificJoke(self, **kwargs):
         # Build the URL with optional parameters
        url = self.base_url
        
        if 'category' in kwargs and kwargs['category'] in self.category:
            url += f"{kwargs['category']}?blacklistFlags=nsfw,religious,racist,sexist,explicit&type=twopart"
        else:
            url += "Any?blacklistFlags=nsfw,religious,racist,sexist,explicit&type=twopart"
            
        #fill other optional parameter
        for key, value in kwargs.items():
            if key == 'amount':
                url += f"&amount={value}"
                
            elif key == 'type' and value in self.joke_type:
                url += f"&type={value}"
                
            elif key == 'language' and value in self.language:
                url += f"&lang={self.language[value]}"
                
        #get in json format + display
        url += "&format=json"
        return self.displayJoke(url)

#COUNTRY API
class CountriesAPI:
    
    def __init__(self):
        self.base_url = "https://restcountries.com/v3.1"

    def searchByName(self, data):
        url = self.base_url + "/name/" + data.lower()
        return url
    
    def searchByCurrency(self, data):
        url = self.base_url + "/currency/" + data.lower()
        return url

    def searchByLanguage(self, data):
        url = self.base_url + "/lang/" + data.lower()
        return url

    def searchByCapitalCity(self, data):
        url = self.base_url + "/capital/" + data.lower()
        return url

    def createCountry(self, url):
        
        try:
            # Call the API by opening the URL and reading the data.
            response = requests.get(url)

            if response.status_code == 200:
                data = {}
                response = response.json()[0]

                data['name'] = response['name']['common']
                data['currencies'] = dict(response['currencies'])
                data['capital'] = response['capital'][0]
                data['region'] = response['region']
                data['subregion'] = response['subregion']
                data['languages'] = dict(response['languages'])
                data['population'] = response['population']
                data['timezones'] = response['timezones']

                country = Country(data)
                return country
            else:
                return {"error": "Failed to fetch a country from the Country API."}

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

class Country:
    
    def __init__(self, data):
        self.name = data["name"]
        self.currencies = data["currencies"]
        self.capital = data["capital"]
        self.region = data["region"]
        self.subregion = data["subregion"]
        self.languages = data["languages"]
        self.population = data["population"]
        self.timezones = data["timezones"]

    def printCountryData(self):
        
        data = ""
        data += f"\nName: {self.name}" 
        data += f"\nCurrencies: {', '.join(self.currencies.keys())}" 
        data += f"\nCapital: {self.capital}" 
        data += f"\nRegion: {self.region}" 
        data += f"\nSubregion: {self.subregion}" 
        data += f"\nLanguages: {', '.join(self.languages.values())}" 
        data += f"\nPopulation: {self.population}" 
        data += f"\nTimezones: {', '.join(self.timezones)}" 

        return data

# define class 
joke_api = JokeAPI()
country_api = CountriesAPI()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/random_joke', methods=['GET'])
def random_joke():
    joke = joke_api.randomJoke()
    return render_template('joke.html', joke=joke)

@app.route('/specific_joke', methods=['GET', 'POST'])
def specific_joke():
    if request.method == 'POST':
        # Get parameters from the form submission
        amount = int(request.form['amount'])
        language = request.form['language']
        category = request.form['category']

        joke = joke_api.specificJoke(amount=amount, language=language, category=category)

        if "error" in joke:
            return render_template('error.html', error_message=joke["error"])
        else:
            return render_template('joke.html', joke=joke)

    return render_template('specific_joke_form.html')

@app.route('/country', methods=['GET', 'POST'])
def country():
    country = None  # Initialize country as None
    
    if request.method == 'POST':
        # Get the selected search type and search term from the form
        search_type = request.form['search_type']
        search_term = request.form['search_term']

        if search_type == 'name':
            url = country_api.searchByName(data=search_term)
        elif search_type == 'currency':
            url = country_api.searchByCurrency(data=search_term)
        elif search_type == 'language':
            url = country_api.searchByLanguage(data=search_term)
        elif search_type == 'capital':
            url = country_api.searchByCapitalCity(data=search_term)
        else:
            return render_template('error.html', error_message='Invalid search type.')

        country = country_api.createCountry(url)

        if isinstance(country, dict) and "error" in country:
            return render_template('error.html', error_message=country["error"])

        return render_template('country.html', 
            country=country,  # Pass the country object to the template
            name=country.name if country else None,   #if country not not none assign country.name , if yes that assign none
            currencies=country.currencies if country else None,
            capital=country.capital if country else None,
            region=country.region if country else None,
            subregion=country.subregion if country else None,
            languages=country.languages if country else None,
            population=country.population if country else None,
            timezones=country.timezones if country else None)

    return render_template('country_form.html')


if __name__ == "__main__":
    app.run(debug=True)
