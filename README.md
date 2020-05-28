# RecipeParser

This is a project I am doing for fun and to learn about web scraping, natural language processing, and whatever else comes up.

## Goal
Programmatically generate an average/typical recipe by comparing lots of top google search results.
* save time: avoid endless scrolling through food blogs
* get more reliable recipes: generated from lots of highly reviewed recipes
* understand recipes better: visualize relative amounts of ingredients, recipe structure

For example, here is a visualization of the proportion of ingredients in a vegan chocolate cake recipe ([https://www.noracooks.com/vegan-chocolate-cake/](https://www.noracooks.com/vegan-chocolate-cake/)),

and a tree representation of a macaroni and cheese recipe ([https://www.momontimeout.com/best-homemade-baked-mac-and-cheese-recipe/](https://www.momontimeout.com/best-homemade-baked-mac-and-cheese-recipe/)]. Clearly there are some issues, but you get the idea.

Ideally, when the instruction parsing is working better, the tree will be entirely connected and have one root node at the bottom, representing the final product.

![Example pie chart](/images/example_pie_chart.png)
![Example recipe graph](/images/example_recipe_tree.png)

## Usage
`python recipe_parser.py <URL of recipe>`

This will display a pie chart of the ingredients and a tree representation of the recipe as it was interpreted (very inaccurate as of now).

Currently only recipes made with the WordPress Recipe Maker are supported. This is commonly used by food blogs and can be identified by `wprm-` elements in the recipe HTML.


## Outline

### Search
  given a recipe search term e.g. 'mac and cheese', get urls for top results.
    - scrape google search results or find a search engine API? may not be available for free
  
### **Recipe parsing (in progress)**
  given a url, determine if the web page contains a recipe, and if so parse it into ingredients and instructions
### **Natural language processing of recipe instructions (in progress)**
  given the text of a recipe instruction, determine the ingredients mentioned and what is done with them
### Recipe comparison
  given multiple recipes, compare their relative proportions of ingredients and their method
### Recipe clustering
  given a lot of recipes for the same thing, cluster them into groups that have similar ingredients/method
### Recipe averaging
  given a lot of recipes for the same thing, generate an 'average' recipe
### UI
  - accept search input and display recipe data, comparison, average
