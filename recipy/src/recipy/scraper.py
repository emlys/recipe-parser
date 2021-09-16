import requests
import re
import bs4
from bs4 import BeautifulSoup


headers = {'User-Agent': 'Mozilla/5.0 (compatible)'}


def scrape_google_search(query):
    """Scrape result URLs from a google search.

    Args:
        query (str): term to search on google

    Returns:
        list(str): list of URLs
    """
    search_url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    urls = []
    tags = soup.find_all('h3')  # search result titles are h3s
    for tag in tags:
        if tag.parent.has_attr('href'):
            # first 7 characters are /url?q=
            url = tag.parent['href'][7:]
            # remove trailing nonsense google things
            base_url = url.split('&sa=')[0]
            urls.append(base_url)

    return urls


def scrape_allrecipes(soup):
    ingredient_tags = soup.find_all(
        'span', class_='ingredients-item-name')
    instruction_tags = soup.find(
        'ul', class_='instructions-section').find_all('p')
    return ingredient_tags, instruction_tags


def scrape_bbc_good_food(soup):
    ingredient_tags = soup.find(
        'section', class_='recipe__ingredients').find_all('li')
    instruction_tags = soup.find(
        'section', class_='recipe__method-steps').find_all('p')
    return ingredient_tags, instruction_tags


def scrape_delish(soup):
    ingredient_tags = soup.find_all('div', class_='ingredient-item')
    instruction_tags = soup.find(
        'div', class_='direction-lists').find_all('li')
    return ingredient_tags, instruction_tags


def scrape_epicurious(soup):
    ingredient_tags = soup.find_all('li', class_='ingredient')
    instruction_tags = soup.find_all('p', class_='preparation_step')
    if not instruction_tags:
        instruction_tags = soup.find_all('li', class_='preparation_step')

    # ingredient_section = soup.find(
    #     'div', class_='recipe__ingredient-list').find('div')
    # ingredient_numbers = ingredient_section.find_all('p')
    # ingredient_names = ingredient_section.find_all('div')

    return ingredient_tags, instruction_tags


def scrape_fine_cooking(soup):
    ingredient_tags = soup.find(
        'div', class_='recipe__ingredients').find_all('li')
    instruction_tags = soup.find(
        'div', class_='recipe__preparation').find_all('li')
    return ingredient_tags, instruction_tags


def scrape_food(soup):
    ingredient_tags = soup.find_all(
            'div', class_='recipe-ingredients__ingredient')
    instruction_tags = soup.find_all(
            'li', class_='recipe-directions__step')
    return ingredient_tags, instruction_tags


def scrape_food_52(soup):
    ingredient_tags = soup.find(
        'div', class_='recipe__list--ingredients').find_all('li')
    instruction_tags = soup.find_all('li', class_='recipe__list-step')
    return ingredient_tags, instruction_tags


def scrape_food_and_wine(soup):
    ingredient_tags = soup.find_all(
            'li', class_='ingredients-item')
    instruction_containers = soup.find_all(
        'li', class_='instructions-section-item')
    instruction_tags = [tag.find('p') for tag in instruction_containers]
    return ingredient_tags, instruction_tags


def scrape_food_network(soup):
    # first tag is 'select all' so remove it
    ingredient_tags = soup.find_all(
        'span', class_='o-Ingredients__a-Ingredient--CheckboxLabel')[1:]
    instruction_tags = soup.find_all('li', class_='o-Method__m-Step')
    return ingredient_tags, instruction_tags


def scrape_king_arthur_baking(soup):
    ingredient_tags = soup.find(
        'div', class_='ingredient-section').find_all('li')
    instruction_tags = soup.find(
        'div', class_='field--recipe-steps').find_all('p')
    return ingredient_tags, instruction_tags


def scrape_liquor(soup):
    ingredient_tags = soup.find_all(
        'li', class_='structured-ingredients__list-item')
    instruction_tags = soup.find(
            'div', class_='structured-project__steps').find_all('p')
    return ingredient_tags, instruction_tags


def scrape_martha_stewart(soup):
    ingredient_tags = soup.find_all('span', class_='ingredients-item-name')
    instruction_tags = soup.find(
        'ul', class_='instructions-section').find_all('p')
    return ingredient_tags, instruction_tags


def scrape_myrecipes(soup):
    ingredient_tags = soup.find_all('span', class_='ingredients-item-name')
    instruction_tags = soup.find(
        'ul', class_='instructions-section').find_all('p')
    return ingredient_tags, instruction_tags


def scrape_ny_times_cooking(soup):
    ingredient_tags = soup.find(
        'ul', class_='recipe-ingredients').find_all('li')
    instruction_tags = soup.find(
        'ol', class_='recipe-steps').find_all('li')
    return ingredient_tags, instruction_tags


def scrape_saveur(soup):
    ingredient_tags = soup.find_all('li', class_='ingredient')
    instruction_tags = soup.find_all('li', class_='instruction')
    return ingredient_tags, instruction_tags


def scrape_serious_eats(soup):
    ingredient_tags = soup.find_all('li', class_=re.compile(
        'ingredient|structured-ingredients__list-item'))
    instruction_tags = soup.find(
            'div', class_='structured-project__steps').find_all('p')
    return ingredient_tags, instruction_tags


def scrape_simply_recipes(soup):
    ingredient_tags = soup.find_all('li', class_='ingredient')
    try:
        instruction_tags = soup.find(
            class_='comp section--instructions section').find_all(
                'p', class_='comp mntl-sc-block mntl-sc-block-html')
    except AttributeError:
        instruction_tags = soup.find(
            'div', class_='structured-project__steps').find_all('p')
    return ingredient_tags, instruction_tags


def scrape_southern_living(soup):
    ingredient_tags = soup.find_all(
            'li', class_='ingredients-item')
    instruction_containers = soup.find_all(
            'li', class_='instructions-section-item')
    instruction_tags = [tag.find('p') for tag in instruction_containers]
    return ingredient_tags, instruction_tags


def scrape_taste_of_home(soup):
    ingredient_tags = soup.find(
        'ul', class_='recipe-ingredients__list').find_all('li')
    instruction_tags = soup.find_all(
        'li', class_='recipe-directions__item')
    return ingredient_tags, instruction_tags


def scrape_the_kitchn(soup):
    ingredient_tags = soup.find_all('li', class_='Recipe__ingredient')
    instruction_tags = soup.find_all('li', class_='Recipe__instructionStep')
    return ingredient_tags, instruction_tags


def scrape_the_pioneer_woman(soup):
    ingredient_tags = soup.find_all('li', class_='ingredient-item')
    instructions_container = soup.find('div', class_='direction-lists')
    instruction_tags = instructions_container.find_all('li')
    if not instruction_tags:
        instruction_tags = [instructions_container]
    return ingredient_tags, instruction_tags


def scrape_the_spruce_eats(soup):

    ingredient_tags = soup.find_all('li', class_='ingredient')
    if not ingredient_tags:
        ingredient_tags = soup.find_all(
            'li', class_='structured-ingredients__list-item')

    try:
        instruction_tags = soup.find(
            class_='comp section--instructions section').find_all(
                'p', class_='comp mntl-sc-block mntl-sc-block-html')
    except AttributeError:
        instruction_tags = soup.find(
            'div', class_='structured-project__steps').find_all('p')

    return ingredient_tags, instruction_tags


def scrape_recipe_url(url):
    """
    Try to scrape ingredients and instructions from a web page.

    Tries, in order:
    - certain popular websites with known format
    - certain popular wordpress recipe templates
    -

    Args:
        url: URL of webpage to parse
    Returns:
        Recipe object
    """
    # get what's between the second and third slashes
    domain = url.split('/')[2]
    response = requests.get(url, headers=headers)
    if response.status_code not in [200, 201]:
        print(f'GET request to {url} failed: code {response.status_code}')
    soup = BeautifulSoup(response.text, 'lxml')
    # print(url)
    # because some of the formats use chained functions, it's not
    # convenient to implement a lazy dictionary.
    # going with if/else for now
    ingredient_tags, instruction_tags = None, None

    # these sites do not contain actual recipes
    bad_domains = [
        'youtube.com',
        'www.eatyourbooks.com',
        'www.yummly.com'
    ]

    site_specific_scrapers = {
        'cooking.nytimes.com': scrape_ny_times_cooking,
        'food52.com': scrape_food_52,
        'www.allrecipes.com': scrape_allrecipes,
        'www.bbcgoodfood.com': scrape_bbc_good_food,
        'www.delish.com': scrape_delish,
        'www.epicurious.com': scrape_epicurious,
        'www.finecooking.com': scrape_fine_cooking,
        'www.food.com': scrape_food,
        'www.foodandwine.com': scrape_food_and_wine,
        'www.foodnetwork.com': scrape_food_network,
        'www.kingarthurbaking.com': scrape_king_arthur_baking,
        'www.liquor.com': scrape_liquor,
        'www.marthastewart.com': scrape_martha_stewart,
        'www.myrecipes.com': scrape_myrecipes,
        'www.saveur.com': scrape_saveur,
        'www.seriouseats.com': scrape_serious_eats,
        'www.simplyrecipes.com': scrape_simply_recipes,
        'www.southernliving.com': scrape_southern_living,
        'www.tasteofhome.com': scrape_taste_of_home,
        'www.thekitchn.com': scrape_the_kitchn,
        'www.thepioneerwoman.com': scrape_the_pioneer_woman,
        'www.thespruceeats.com': scrape_the_spruce_eats
    }

    template_specific_scrapers = [
        scrape_wordpress_recipe_maker_recipe,
        scrape_wordpress_tasty_recipe,
        scrape_wordpress_mediavine_create_recipe,
        scrape_wordpress_zoom_recipe,
        scrape_recipe_shopper_recipe
    ]

    # first see if it's a site with a known format
    if domain in site_specific_scrapers:
        try:
            ingredient_tags, instruction_tags = (
                site_specific_scrapers[domain](soup))
        except AttributeError:
            print(f'Not a {domain} recipe.')
            return
        if not (ingredient_tags and instruction_tags):
            print(f'Not a {domain} recipe.')
            return

    # then see if the site is using a template with a known format
    else:
        for scraper in template_specific_scrapers:
            try:
                ingredient_tags, instruction_tags = scraper(soup)
                break
            except ValueError:
                continue
        # then try to identify the recipe by searching the tags
        else:
            print(url)
            try:
                ingredient_tags, instruction_tags = find_recipe(soup)
            except ValueError:
                print('Could not find recipe in page')

    if ingredient_tags and instruction_tags:
        # make a list of ingredients
        ingredients = [i.get_text().strip() for i in ingredient_tags]
        instructions_list = []
        # Make sure sentences are separated by a period to help spaCy out
        for i in instruction_tags:
            text = i.get_text().strip()
            if not text.endswith('.'):
                text += '.'
            instructions_list.append(text)
        instructions = ' '.join(instructions_list)
        # Replace all colons and semicolons with periods. spaCy seems to do
        # better when these are separate sentences.
        instructions = instructions.replace(';', '.')
        instructions = instructions.replace(':', '.')
        return ingredients, instructions
    else:
        # print('Could not find recipe')
        return


def scrape_wordpress_mediavine_create_recipe(soup):
    """
    Return True if soup contains a WordPress Tasty recipe.

    Args:
        soup: BeautifulSoup representation of webpage with recipe

    Returns:
        ingredients, instructions tuple

    Raises:
        ValueError if MV Create tags are not found
    """
    ingredients_container = soup.find(class_='mv-create-ingredients')
    instructions_container = soup.find(class_='mv-create-instructions')

    if ingredients_container and instructions_container:
        ingredient_tags = ingredients_container.find_all('li')
        instruction_tags = instructions_container.find_all('li')
        if ingredient_tags and instruction_tags:
            return ingredient_tags, instruction_tags

    raise ValueError('Not a MediaVine Create recipe')


def scrape_wordpress_recipe_maker_recipe(soup):
    """
    Scrape ingredients and instructions from a WordPress recipe.

    Args:
        soup (bs4.BeautifulSoup): representation of webpage with recipe

    Returns:
        ingredients, instructions tuple

    Raises:
        ValueError if WPRM tags are not found
    """
    ingredient_tags = soup.find_all('li', class_='wprm-recipe-ingredient')
    instruction_tags = soup.find_all(
        'div', class_='wprm-recipe-instruction-text')
    if ingredient_tags and instruction_tags:
        return ingredient_tags, instruction_tags
    raise ValueError('Not a WPRM recipe')


def scrape_wordpress_tasty_recipe(soup):
    """
    Scrape ingredients and instructions from a WordPress Tasty recipe.

    Args:
        soup (bs4.BeautifulSoup): representation of webpage with recipe

    Returns:

    """
    ingredients_container = soup.find(
        'div',
        class_=re.compile(
            'tasty-recipe-ingredients|'
            'tasty-recipes-ingredients|'
            'tasty-recipes-ingredients-body'))
    instructions_container = soup.find(
        'div',
        class_=re.compile(
            'tasty-recipe-instructions|'
            'tasty-recipes-instructions|'
            'tasty-recipes-instructions-body'))
    if ingredients_container and instructions_container:
        ingredient_tags = ingredients_container.find_all('li')
        instruction_tags = instructions_container.find_all('li')
        if not instruction_tags:
            instruction_tags = instructions_container.find_all('p')

        if ingredient_tags and instruction_tags:
            return ingredient_tags, instruction_tags
    raise ValueError('Not a Wordpress Tasty recipe')


def scrape_wordpress_zoom_recipe(soup):
    ingredient_tags = soup.find_all('span', class_='wpzoom-rcb-ingredient-name')
    instruction_tags = soup.find_all('li', class_='direction-step')
    if ingredient_tags and instruction_tags:
        return ingredient_tags, instruction_tags
    raise ValueError('Not a Wordpress Zoom recipe')


def scrape_recipe_shopper_recipe(soup):
    ingredients_container = soup.find(
        'fieldset', class_='ingredients-section__fieldset')
    instructions_container = soup.find(
        'fieldset', class_='instructions-section__fieldset')
    if ingredients_container and instructions_container:
        ingredient_tags = ingredients_container.find_all('li')
        instruction_tags = instructions_container.find_all('p')
        if ingredient_tags and instruction_tags:
            return ingredient_tags, instruction_tags
    raise ValueError('Not a Recipe Shopper recipe')


def find_recipe(soup):

    ingredient_header = soup.find(string=re.compile(
        '^Ingredients:?\s*$', flags=re.IGNORECASE))
    patterns = [
        '^Instructions:?\s*$',
        '^Directions:?\s*$',
        '^Steps:?\s*$',
        '^Preparation:?\s*$',
        '^Method:?\s*$'
    ]
    for pattern in patterns:
        instructions_header = soup.find(string=re.compile(
            pattern, flags=re.IGNORECASE))
        if instructions_header:
            break

    print('!!!')
    print(ingredient_header)
    print(instructions_header)

    # if ingredient_header:
    #     # print('next elements:', list(ingredient_header.next_elements)[:5])
    #     next_tag = None
    #     for next_elem in ingredient_header.next_elements:
    #         if isinstance(next_elem, bs4.element.Tag):
    #             next_tag = next_elem
    #             break
    #     # print('next tag:', next_tag, next_tag.name)

    #     if next_tag.name in {'ul', 'ol', 'dl'}:
    #         next_list = next_tag
    #     else:
    #         next_list = next_tag.find(re.compile('ul|ol|dl'))
    #     # print('next list:', next_list)
    #     if next_list:
    #         print('ingredients:')
    #         list_items = next_list.find_all('li|dt')
    #         for i in list_items:
    #             print(' '.join(list(i.stripped_strings)))

        # tag = ingredient_header
        # while isinstance(tag, bs4.NavigableString) or not tag.next_sibling:
        #     tag = tag.parent
        # print(tag)
        # print('next:', repr(str(tag.next_sibling)))

    # if instructions_header:
    #     # print('next elements:', list(instructions_header.next_elements)[:5])
    #     next_tag = None
    #     for next_elem in instructions_header.next_elements:
    #         if isinstance(next_elem, bs4.element.Tag):
    #             next_tag = next_elem
    #             break
    #     # print('next tag:', next_tag)
    #     if next_tag.name in {'ul', 'ol'}:
    #         next_list = next_tag
    #     else:
    #         next_list = next_tag.find(re.compile('ul|ol'))
    #     # print('next list:', next_list)
    #     if next_list:
    #         print('instructions:')
    #         list_items = next_list.find_all('li')
    #         for i in list_items:
    #             print(' '.join(list(i.stripped_strings)))

    def is_real(element):
        print(element, type(element), repr(str(element)))
        if isinstance(element, bs4.element.NavigableString):
            if str(element).isspace():
                return False
        else:
            print(list(element.strings))
            if not list(element.strings):
                return False
        return True


    if instructions_header:
        if isinstance(instructions_header, bs4.element.NavigableString):
            instructions_header = instructions_header.parent

        if (instructions_header.previous_sibling and
                any(is_real(e) for e in instructions_header.previous_siblings)):
            # print(instructions_header, repr(instructions_header.previous_sibling), type(instructions_header.previous_sibling))
            # print('has previous sibling already')
            container = instructions_header.next_sibling
            while isinstance(container, bs4.element.NavigableString):
                # print('repr:', repr(container), type(container))
                container = container.next
        else:
            container = instructions_header
            # print('*', repr(container))
            # print('**', repr(container.previous_sibling))
            prev = None
            while not prev:
                container = container.parent
                # print('*', repr(container))
                prev = container.previous_sibling
                while isinstance(prev, bs4.element.NavigableString) and str(prev).isspace():
                    prev = prev.previous_sibling
                # print('**', repr(prev))
            # print('final previous sibling:', prev)

        print('instructions:', ' '.join([s.strip() for s in container.strings]))



    # if not tags:
    #     return None, None

    # tag = tags[0]

    # def like_ingredient(tag):
    #     text = re.sub('\s+', ' ', tag.get_text().strip())

    #     if len(text) > 50:
    #         return False
    #     print(repr(text))
    #     # define some regular expressions to help identify numbers
    #     integer = '(\d+)'
    #     fraction = f'{integer}/{integer}|[½⅓⅔¼¾⅛⅜⅝⅞]'
    #     # an integer and a fraction separated by ' ' or ' and ' or '-'
    #     # '-' can also be a range, but if it's an integer followed by a
    #     # fraction, it's safe to assume it's a mixed fraction.
    #     mixed_fraction = f'{integer}(?: | and |-)?{fraction}'
    #     decimal = f'({integer}\.{integer})'

    #     for pattern in [mixed_fraction, fraction, decimal, integer]:
    #         pattern += ' (.*)$'
    #         match = re.match(re.compile(pattern), text)
    #         if match:
    #             print('match:', text)
    #             return True

    #     return False



    # print('***')
    # next_list = tag.find_next('ul')
    # for child in next_list.contents:
    #     if child.name == 'li':
    #         print(repr(child.get_text().strip().replace('\n', ' ')))
    # print('***')

    # ingredient_regex = '^([0123456789½⅓⅔¼¾⅛⅜⅝⅞]+)(.*?) (.*)$'
    # print(repr(tag.find_next(like_ingredient).get_text()))
    # # for tag in soup.find_all(like_ingredient):
    #     print(tag.get_text())
    # print(tag.find_all_next('div', string=re.compile(ingredient_regex)))

    # for n in tag.find_all_next():
    #     print(n.string, n.get_text())

    # while not tag.next_sibling:
    #     tag = tag.parent
    #     print(tag.string)

    # while tag.next_sibling:
    #     print('next sibling:', tag)
    #     if tag.next_sibling.name == 'ul':
    #         print(tag.next_sibling)
    #         for child in tag.next_sibling.contents:
    #             if child.name == 'li':
    #                 print(child.get_text().replace('\n', ' '))
    #         break
    #     tag = tag.next_sibling
    return None, None

