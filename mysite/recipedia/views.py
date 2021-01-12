import requests
import pprint
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .recipe_parser import RecipeParser


API_KEY = 'AIzaSyChJO55OhJ6pVYpCBR1lw8EdIN5MCUBS50'
SEARCH_ENGINE_ID = 'febc45db5bc3cbafd'
parser = RecipeParser()



def index(request):
    return HttpResponse("Hello world!")

def find_and_parse_recipes(request):
    print(request)
    print(request.GET)

    query = request.GET['query']
    if query.startswith('http'):
        urls = [query]
    else:
        urls = search(query)

    recipes = get_recipes(urls, parser)
 
    ingredients = []
    # for node in recipes[0].ingredient_nodes:
    #     node_dict = node.as_dict()
    #     node_dict['magnitude'] = node.ingredients[0].quantity.magnitude
    #     node_dict['unit'] = str(node.ingredients[0].quantity.units)
    #     ingredients.append(node_dict)


    for ingredient in recipes[0].ingredients:
        ingredient_dict = {}
        ingredient_dict['magnitude'] = ingredient.quantity.magnitude
        ingredient_dict['unit'] = str(ingredient.quantity.units)
        ingredient_dict['name'] = ingredient.name
        ingredients.append(ingredient_dict)

            
    response = JsonResponse({
        'ingredients': ingredients,
        'steps': [node.step.as_dict() for node in recipes[0].order[len(recipes[0].ingredient_nodes):]],
        'graph': [node.as_dict() for node in recipes[0].order]
    })
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


def format_ingredients(nodes):
    """Format a list of ingredient Nodes into a dictionary for JSON response.
    Args:
        nodes (list): list of ingredient Nodes

    Returns:
        ingredients dictionary in the format:
        {
            0: {
                id: 0,
                magnitude: 2,
                unit: 'cup',
                name: 'flour'
            }
        }
    """
    ingredients_dict = {}
    for node in nodes:
        ingredient = node.ingredients[0]
        node_dict = {}
        node_dict['id'] = node.name
        node_dict['magnitude'] = ingredient.quantity.magnitude
        node_dict['unit'] = str(ingredient.quantity.units)
        node_dict['name'] = ingredient.name
        ingredients_dict[node.name] = node_dict
    return ingredients_dict

def format_steps(nodes):
    """Format a list of step Nodes into a dictionary for JSON response.
    Args:
        nodes (list): list of step Nodes

    Returns:
        steps dictionary in the format:
        {
            1: {
                id: 1,
                parents: [0],
                ingredients: [0],
                text: [
                    {word: 'Mix', nodeRef: None},
                    {word: 'the', nodeRef: None},
                    {word: 'flour', nodeRef: 0}
                ],
                verbIndex: 0
            }
        }
    """
    steps_dict = {}
    for node in nodes:
        node_dict = {}
        node_dict['id'] = node.name
        node_dict['parents'] = [parent.name for parent in node.parents]

def search(query, number=10):
    """Web search for a query.

    The implementation of this function may change since I'm not sure what is
    the best option for a web search API. Options include:
        - Google Custom Search API
        - scraping Google Search
        - entireweb API

    Args:
        query (string): term to search 
        number (int): number of search results to get

    Returns:
        list of URL results
    """
    response = requests.get(
        f'https://www.googleapis.com/customsearch/v1?key={API_KEY}&'
        f'cx={SEARCH_ENGINE_ID}&num={number}&q={query}')
    results = response.json()['items']

    urls = [result['link'] for result in results]
    return urls

def get_recipes(urls, parser):
    """Turn a list of urls into a list of Recipe objects.

    Args:
        urls (list[string]): list of urls to access
        parser (RecipeParser): RecipeParser object that instantiates all
            Recipes using the same spacy instance and pint unit registry.
    Returns:
        list[Recipe]: list of Recipe objects derived from the urls.
    """

    recipes = []

    for url in urls:
        recipes.append(parser.parse(url))
    return recipes
        



