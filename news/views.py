from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


from django.shortcuts import render



# Create your views here.
from newsapi import NewsApiClient


def newsPaper(request):
    newsapi = NewsApiClient(api_key='573dab4634604cb0a5bc4a55de0f9e50')
    top = newsapi.get_top_headlines(sources='new-scientist')

    articles = top['articles']
    description = []
    newsTitle = []
    img = []
    url = []

    for i in range(len(articles)):
        newsInfo = articles[i]
        newsTitle.append(newsInfo['title'])
        description.append(newsInfo['description'])
        img.append(newsInfo['urlToImage'])
        url.append(newsInfo['url'])

    Newslist = zip(newsTitle, description, url,img)

    return render(request, 'index.html', context={"Newslist": Newslist})