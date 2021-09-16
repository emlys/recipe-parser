# spaCy training

## `annotate.py`
This is an annotation helper script to simplify my workflow of making training data for the tagger and parser components. It uses the default `en_core_web_lg` model to bootstrap the training data, so I only have to re-annotate any mistakes it makes.


### how to use

1. **Pass in a list of sentences.**

For each sentence, spaCy parses the sentence with the default `en_core_web_lg` model. A browser window will open showing the `displaCy` visualization of the sentence, and a Sublime text window will open showing a file called `edit`, which stores the relevant attributes for each token. 

2. **Find any mistakes.** Use the `displaCy` visualization to help find any mistakes in the tagging and parsing. Note: `displaCy` only displays the coarse-grained POS tags.

3. **Correct any mistakes.** If there are any mistakes, edit the `edit` file to reflect correct tagging/parsing, and save the file when done. Note that both the coarse-grained POS tags in the `pos` column and the fine-grained POS tags in the `tag` column must be verified and edited together. When the `edit` file is correct and saved, press `Enter` in the terminal running `annotate.py`.

4. **Double-check.** A new browser tab will open showing the `displaCy` visualization of the edited sentence. Check that this is correct.

- If not correct, press `n` in the terminal running `annotate.py`. This will take you back to step 3 and reopen the `edit` file.

- When it is correct, press `y` in the terminal running `annotate.py`.

5. **Repeat steps 2-4 for each sentence.** Each sentence is individually saved to its own `DocBin` file after you finish working on it, so you can stop after any sentence and not lose work. However you will have to remember where you were in the original list of sentences. Each `DocBin` file is named after the sentence it represents (up to the maximum possible length of 255 characters), with spaces replaced with underscores and the standard `.spacy` extension.



