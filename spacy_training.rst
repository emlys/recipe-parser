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


# Assumptions and reasoning behind recipe parsing rules

1. Recipe instructions are given in the imperative. `spaCy` part-of-speech tagging does not identify the imperative tense as such. I am inferring that word is in the imperative tense if (1) it is a verb in the infinitive :``word.tag_ == 'VB'`` , and (2) it has no subject: ``child.dep_ != 'nsubj' for child in word.children``.

2. The instruction's imperative verb should be the root. (always?)

3. The instruction's imperative verb is often the first word of the sentence, but doesn't have to be:
    ***Mix** ingredients together in a small bowl* or *In a small bowl, **mix** ingredients together*.

4. Recipe text can contain sentences that are not instructions. These sentences often explain techniques, describe what things should look like, and give tips or optional steps. For now, I'm assuming it's safe to ignore these. Recipes for the same thing can differ in terms of how much extraneous information and advice they give; this shouldn't affect their similarity to the algorithm.







