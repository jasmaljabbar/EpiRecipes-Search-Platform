from opensearchpy import OpenSearch
from django.conf import settings

client = OpenSearch(
    hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
    http_auth=None, 
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

def search_recipes(query, filters=None, page=1, size=10):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title", "ingredients", "directions"]
            }
        },
        "size": size,
        "from": (page - 1) * size
    }

    if filters:
        body["post_filter"] = {
            "bool": {
                "must": [{"term": {key: value}} for key, value in filters.items()]
            }
        }

    response = client.search(index=settings.OPENSEARCH_INDEX, body=body)
    hits = response['hits']['hits']
    total = response['hits']['total']['value']

    recipes = [hit['_source'] for hit in hits]
    return recipes, total

def get_recipe(recipe_id):
    try:
        response = client.get(index=settings.OPENSEARCH_INDEX, id=recipe_id)
        return response['_source']
    except Exception as e:
        print(f"Error retrieving recipe: {e}")
        return None