# Training the spaCy model for recipes

## Method
Part-of-speech tagging and dependency parsing are the most relevant parts of the spaCy workflow right now.

### Selecting sample data
In order to get a pretty representative selection of recipe text, I randomly selected recipe names from *The Joy of Cooking* (2006). An [online random number generator](https://www.random.org/integers/) was used to generate 100 random integers in the range 30-955 inclusive, the range of pages in *The Joy of Cooking* between the introduction and appendices. I looked up each page number and selected the first complete recipe on the page. Of these, 16 pages didn't have any recipe on them, leaving me with 84 recipe names.

For each recipe name (minus punctuation), I Googled "<recipe name> recipe" and clicked on the top result that was (1) actually a recipe, and (2) not behind a paywall e.g. cooking.nytimes.com. I copied out the steps of each recipe, split them into one sentence per line, and pasted them into a spreadsheet (`full_sample_dataset.csv`) for a total of 1,141 sentences of sample data.

### Labeling sample data

The spaCy documentation on how much data is necessary: 
> If you want to train a model from scratch, you usually need at least a few hundred examples for both training and evaluation. To update an existing model, you can already achieve decent results with very few examples – as long as they’re representative.
...
> As a rule of thumb, you should allocate at least 10% of your project resources to creating training and evaluation data. If you’re looking to improve an existing model, you might be able to start off with only a handful of examples. Keep in mind that you’ll always want a lot more than that for evaluation – especially previous errors the model has made. 

Since I'm staring with the `en_core_web_md model`, and updating it to perform better on recipes, I decided to start with a relatively small subset of the sample data I collected. I used the python `random` module to select 50 of the 1,141 sample sentences and used the `en_core_web_md` model to label them. I saved the labeled sentences in the JSON format spaCy uses for training data. I then used `displacy` to visualize the part-of-speech and dependency labels assigned by the default model, and corrected  


# References used for part-of-speech and dependency labels

* https://github.com/clir/clearnlp-guidelines/blob/master/md/specifications/dependency_labels.md , the exact dependency labels that spaCy uses with not-so-helpful definitions

* https://spacy.io/api/annotation#json-input , spaCy's list of English part-of-speech tags

* http://www.mathcs.emory.edu/~choi/doc/cu-2012-choi.pdf , *Guidelines for the CLEAR Style Constituent to Dependency Conversion*, Choi and Palmer 2012. Outdated in some places.

* https://universaldependencies.org/u/dep/xcomp.html , the Universal Dependency scheme. Different from the CLEAR English dependencies, but has some overlap and helpful examples.

* https://nlp.stanford.edu/software/dependencies_manual.pdf , the Stanford typed dependencies manual. Different from the CLEAR English dependencies, but has some overlap and helpful examples.


# Recipe HTML format

Of the 84 sample recipes, 21 were created with [WordPress Recipe Maker](https://bootstrapped.ventures/wp-recipe-maker/), 3 with [Tasty Recipes](https://www.wptasty.com/tasty-recipes), 2 with [MediaVine](https://www.mediavine.com/products/create/), and 1 with [EasyRecipe](https://easyrecipeplugin.com/). The others had custom HTML formatting.


# Assumptions and reasoning behind recipe parsing rules

1. Recipe instructions are given in the imperative. `spaCy` part-of-speech tagging does not identify the imperative tense as such. I am inferring that word is in the imperative tense if (1) it is a verb in the infinitive :``word.tag_ == 'VB'`` , and (2) it has no subject: ``child.dep_ != 'nsubj' for child in word.children``.

    a. Recipe instructions should always (?) have a direct object, but it may be implied. For example: "Mix the batter. Pour into pan." *batter* is the implicit direct object of the second sentence. We can handle this case by keeping track of the last known direct object, and carrying it forward when an imperative lacks a ``dobj`` of its own.

2. The instruction's imperative verb should be the root. (always?)

3. The instruction's imperative verb is often the first word of the sentence, but doesn't have to be:
    ***Mix** ingredients together in a small bowl* or *In a small bowl, **mix** ingredients together*.

## Parsing ingredients from steps

Case 1: Action performed on one ingredient. e.g. "*Sift the flour*". 

Case 2: Action performed on a list of ingredients e.g. "*Stir together the eggs, milk, and butter*".

Case 3. Action performed on a combination of ingredients from a previous step. e.g. "*Fold the egg mixture*", "*Add into the bowl with the eggs*".




4. Recipe text can contain sentences that are not instructions. These sentences often explain techniques, describe what things should look like, and give tips or optional steps. For now, I'm assuming it's safe to ignore these. Recipes for the same thing can differ in terms of how much extraneous information and advice they give; this shouldn't affect their similarity to the algorithm.

5. Recipes are characterized by the following factors, from most to least important: (1) ingredients and their relative quantities; (2) actions in recipe steps e.g. 'mix', 'saute', 'blend'; (3) the order in which ; and (4) technique e.g. qualifiers on steps such as 'mix thoroughly', 'bake until golden brown and bubbly'. Technique is important of course, but I think it's not likely to be the differentiating factor between different recipes. 

6. Therefore, I'm focusing on the imperative sentences in a recipe. If it's possible to identify the action verb and subject ingredient(s) in each step, that should be enough to represent the recipe as a tree structure. Later on, the tree could be annotated with extra information from the recipe.


recipe ::= [sentence]  

sentence ::= step | extra

step ::= imperative --dobj--> [object] | imperative

imperative : token such that ``token.tag_ == 'VB'`` and ``child.dep_ != 'nsubj' for child in token.children``

object ::= ingredient | mixture

ingredient : matches an ingredient in the recipe ingredients list

mixture : matches a previous node in the recipe tree

extra : a modfiying sentence or phrase that explains further but isn't critical to the recipe structure



### Algorithm for finding direct object(s) of a token

get_objects(token):
    objects = []
    for child in token.children:
        if child.dep_ == 'dobj':
            objects.append(child)
            objects += get_conjugates(child)
    return objects

get_conjugates(token):
    conjugates = []
    for child in token.children:
        if child.dep_ == 'conj':
            return [child] + get_conjugates(child)


### Algorithm for identifying ingredients

identify_item(token, ingredients):
    matches = []
    for ing in ingredients:
        if token in ing:
            matches.append(ing)

    if len(matches) == 0:
        # token is not an ingredient
    elif len(matches) == 1:
        # token matches 1 ingredient
        return matches[0]
    else:
        # token matches multiple things
        # need to narrow it down
        token.subtree



# Data structure

A recipe can be described by a directed tree graph where the leaves are the ingredients, nodes are recipe instructions, and the root is the finished product.




