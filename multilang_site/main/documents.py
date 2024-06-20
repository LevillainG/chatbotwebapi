from elasticsearch import Elasticsearch, helpers
from main.models import Article

# Full URL with scheme, host, and port
es = Elasticsearch("http://localhost:9200")

def bulk_indexing():
    articles = Article.objects.all()
    actions = [
        {
            "_index": "articles",
            "_type": "_doc",
            "_id": article.id,
            "_source": {
                "title": article.title,
                "content": article.content,
                "publication_date": article.publication_date,
            },
        }
        for article in articles
    ]
    helpers.bulk(es, actions)

