# In opensearch_utils/search.py

import logging
from opensearchpy import OpenSearch
from django.conf import settings

logger = logging.getLogger(__name__)

client = OpenSearch(
    hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
    http_auth=None, 
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

def search_recipes(query, filters=None, page=1, size=10, sort_by=None):
    try:
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "ingredients", "directions"],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        }
                    ]
                }
            },
            "size": size,
            "from": (page - 1) * size
        }

        if filters:
            filter_clauses = []
            for key, value in filters.items():
                if key in ['calories', 'rating']:
                    range_filter = {"range": {key: {}}}
                    if 'min' in value:
                        range_filter["range"][key]["gte"] = float(value['min'])
                    if 'max' in value:
                        range_filter["range"][key]["lte"] = float(value['max'])
                    filter_clauses.append(range_filter)
                elif key == 'categories':
                    filter_clauses.append({"terms": {key: value.split(',')}})
                else:
                    filter_clauses.append({"term": {key: value}})
            
            body["query"]["bool"]["filter"] = filter_clauses

        if sort_by:
            body["sort"] = [{sort_by: {"order": "desc"}}]

        logger.debug(f"OpenSearch query: {body}")
        
        response = client.search(index=settings.OPENSEARCH_INDEX, body=body)
        hits = response['hits']['hits']
        total = response['hits']['total']['value']

        logger.info(f"OpenSearch search completed. Found {total} results.")
        
        recipes = [hit['_source'] for hit in hits]
        return recipes, total
    except Exception as e:
        logger.error(f"Error in search_recipes: {str(e)}", exc_info=True)
        raise

def get_recipe(recipe_id):
    try:
        logger.debug(f"Fetching recipe with id: {recipe_id}")
        response = client.get(index=settings.OPENSEARCH_INDEX, id=recipe_id)
        logger.info(f"Successfully fetched recipe with id: {recipe_id}")
        return response['_source']
    except Exception as e:
        logger.error(f"Error retrieving recipe {recipe_id}: {str(e)}", exc_info=True)
        return None