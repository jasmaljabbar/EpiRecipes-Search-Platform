import json
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

def create_index():
    index_body = {
        'settings': {
            'index': {
                'number_of_shards': 4,
                'number_of_replicas': 2
            }
        },
        'mappings': {
            'properties': {
                'title': {'type': 'text'},
                'ingredients': {'type': 'text'},
                'directions': {'type': 'text'},
                'calories': {'type': 'integer'},
                'rating': {'type': 'float'},
                'protein': {'type': 'float'},
                'fat': {'type': 'float'},
                'sodium': {'type': 'float'},
                # Add more fields as needed
            }
        }
    }
    
    client.indices.create(index=settings.OPENSEARCH_INDEX, body=index_body)

def index_recipe(recipe):
    response = client.index(
        index=settings.OPENSEARCH_INDEX,
        body=recipe,
        id=recipe.get('id'),
        refresh=True
    )
    return response

def bulk_index_recipes(recipes):
    bulk_data = []
    for recipe in recipes:
        bulk_data.append({
            "index": {
                "_index": settings.OPENSEARCH_INDEX,
                "_id": recipe.get('id')
            }
        })
        bulk_data.append(recipe)
    
    response = client.bulk(body=bulk_data, refresh=True)
    return response


def index_from_file(file_path):
    with open(file_path, 'r') as file:
        recipes = json.load(file)
    
    create_index()
    return bulk_index_recipes(recipes)

if __name__ == "__main__":
    # Example usage
    index_from_file('path/to/your/epirecipes.json')