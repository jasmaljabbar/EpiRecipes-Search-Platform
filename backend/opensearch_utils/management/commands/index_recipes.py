from django.core.management.base import BaseCommand
from opensearchpy import OpenSearch, helpers
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Indexes recipe data from an Excel file into OpenSearch'

    def handle(self, *args, **kwargs):
        # OpenSearch connection details (using 'opensearch' as host because of Docker Compose networking)
        host = 'opensearch'
        port = 9200
        # If authentication is enabled, provide credentials
        auth = ('admin', 'admin')

        # Create the OpenSearch client (no SSL/TLS for local Docker setup)
        client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
        )

        # Define the index name
        index_name = 'epirecipes'

        # Define the index mapping
        index_mapping = {
            'mappings': {
                'properties': {
                    'title': {'type': 'text'},
                    'ingredients': {'type': 'text'},
                    'directions': {'type': 'text'},
                    'categories': {'type': 'keyword'},
                    'calories': {'type': 'float'},
                    'rating': {'type': 'float'},
                    'prepTime': {'type': 'integer'},
                    'cookTime': {'type': 'integer'}
                }
            }
        }

        # Create the index if it doesn't exist
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name, body=index_mapping)
            self.stdout.write(f"Index '{index_name}' created.")

        # Function to read recipes from the Excel file
        def read_recipes(file_path):
            # Load the Excel file using pandas
            df = pd.read_csv(file_path)

            # Iterate over rows of the dataframe and yield recipes
            for _, row in df.iterrows():
                yield {
                    "title": row.get('Title', ''),
                    "ingredients": row.get('Ingredients', ''),
                    "directions": row.get('Directions', ''),
                    "categories": row.get('Categories', ''),
                    "calories": row.get('Calories', 0),
                    "rating": row.get('Rating', 0),
                    "prepTime": row.get('PrepTime', 0),
                    "cookTime": row.get('CookTime', 0)
                }

        # Specify the path to the Excel file
        file_path = 'epi_r.csv'  # Replace with your actual file path

        # Indexing the data
        actions = [
            {
                "_index": index_name,
                "_source": recipe
            }
            for recipe in read_recipes(file_path)
        ]

        # Use helpers.bulk to index all the recipes at once
        helpers.bulk(client, actions)
        self.stdout.write("Indexing complete!")
