from newspaper import Article
import nltk

nltk.download('punkt_tab')

def get_newspaper3k_extraction(url):
    article = Article(url)
    article.download()
    article.parse()
    return article

article = get_newspaper3k_extraction('https://edition.cnn.com/2025/06/20/middleeast/trump-iran-strike-delay-israel-latam-intl')
article.nlp()
print(article.summary)