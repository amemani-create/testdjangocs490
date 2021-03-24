from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


from django.shortcuts import render



# Create your views here.
from newsapi.newsapi_client import NewsApiClient


def newsPaper(request):
    newsapi = NewsApiClient(api_key='573dab4634604cb0a5bc4a55de0f9e50')
    top = newsapi.get_top_headlines( sources='new-scientist')

    articles = top['articles']
    desc = []
    news = []
    img = []

    for i in range(len(articles)):
        newsInfo = articles[i]
        news.append(newsInfo['title'])
        desc.append(newsInfo['description'])
        img.append(newsInfo['urlToImage'])
    Newslist = zip(news, desc, img)

    return render(request, 'news.html', context={"Newslist": Newslist})