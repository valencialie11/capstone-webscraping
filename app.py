from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import re 

app = Flask(__name__)

def scrap(url = "https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31"):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    #Find the key to get the information
    movie = soup.find('div', attrs={'class':'lister-list'}) 
    temp0 = []
    for a in range(0,50):
        votes = movie.find_all('p', attrs={'class':'sort-num_votes-visible'})[a]
        votes = votes.text.strip()
        temp0.append(votes) #append the needed information 
    temp = []
    for b in range(0, 50):
        nm = movie.find_all('h3')[b]
        for wrapper in nm.find_all('a', href = True):
            temp.append(wrapper.text)
    
    temp2 = []
    for c in range(0, 50):
        stuff = movie.find_all('div', attrs = {'class': 'ratings-bar'})[c]
        stuff = stuff.text.strip()
        temp2.append(stuff)
    
    temp3 = []
    for d in range(0,50):
        ratings = movie.find_all('strong')[d]
        ratings = ratings.text.strip()
        temp3.append(ratings)
    temp0 = pd.Series(temp0, name = 'Votes')
    temp = pd.Series(temp, name = 'Movie Name')
    temp2 = pd.Series(temp2, name = 'Meta Score')
    temp3 = pd.Series(temp3, name = 'Ratings')
    df = pd.concat([temp, temp3, temp2, temp0], axis = 1)  #creating the dataframe
    
    df['Votes'] = df['Votes'].str.replace("\n","")
    df['Movie Name'] = df['Movie Name'].str.replace("Gisaengchung","Parasite")
  
    # Function to clean the votes
    def Clean_names(Votes): 
    # Search for | in the name followed by 
    # any characters repeated any number of times 
        if re.search(r'\|.*', Votes): 
  
        # Extract the position of beginning of pattern 
            pos = re.search(r'\|.*', Votes).start() 
  
        # return the cleaned name 
            return Votes[:pos] 
  
        else: 
        # if clean up needed return the same name 
            return Votes
    
    df['Votes'] = df['Votes'].apply(Clean_names) 
    df['Votes'] = df['Votes'].str.replace("Votes:","")
    df['Votes'] = df['Votes'].str.replace(",","")
    df['Meta Score'] = df['Meta Score'].str.replace("\n","")
    df['Meta Score'] = df['Meta Score'].str.replace("Rate this","")
    df['Meta Score'] = df['Meta Score'].str.replace("12345678910","")
    df['Meta Score'] = df['Meta Score'].str.replace("Metascore","")
    df["Meta Score"] = df["Meta Score"].str.split("/").str[1]
    df['Meta Score'] = df['Meta Score'].str.replace("10X","")
   #data wranggling -  try to change the data type to right data type
    df.Ratings = df.Ratings.astype('float64')
    df['Votes'] = df['Votes'].astype('int64')
    #I made it into category because there are missing values and I can't change it to int64
    df['Meta Score'] = df['Meta Score'].astype('category')
    df = df.sort_values('Ratings', ascending = False).set_index('Movie Name')
   #end of data wranggling

    return df

@app.route("/")
def index():
    df = scrap("https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31") #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(10,10),dpi=300)
    ratings1 = df.head(7).iloc[:, 0:1]
    ratings1.plot.bar()
    
    #Do not change this part
    plt.savefig('plot',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
