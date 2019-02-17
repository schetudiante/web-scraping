# Web Scraping
Scripts for collecting text/building corpora for word embedding training. A Pipfile listing required modules
and recommended python version is include. To activate the environment, make sure you have pipenv intalled
then run the command ``pipenv shell``. This should put you into a python3 environment with the correct
modules installed.

Several ``.gitignore``'s are placed throughout the directory tree. This is intentional to prevent raw data
from being pushed to the repository. Modify with caution.

## Current sources
### Breitbart News
According to Wikipedia, 
"Breitbart News Network (known commonly as Breitbart News, Breitbart or Breitbart.com) is a far-right
syndicated American news, opinion and commentary website founded in mid-2007 by conservative commentator
Andrew Breitbart, who conceived it as 'the Huffington Post of the right.' Its journalists are widely 
considered to be ideologically driven, and some of its content has been called misogynistic, xenophobic, 
and racist by liberals and many traditional conservatives alike. The site has published a number of lies, 
conspiracy theories, and intentionally misleading stories."

The scripts and dataset for Breitbart News were lost on a disk failure (take this as a reminder to make
careful backups), so the directory is currently empty.

### Fox News
"Fox News (officially known as the Fox News Channel, commonly abbreviated to FNC) is an American pay 
television news channel owned by the Fox News Group, a division of Fox. Fox News has been described 
as practicing biased reporting in favor of the Republican Party, the George W. Bush and Donald Trump 
administrations and conservative causes while slandering the Democratic Party and spreading harmful 
propaganda intended to negatively affect its members' electoral performances."

The original scripts for Fox News relied on browser automation tools, but a new version is being
written that should run more cleanly and less resource intensively from the command line. The old
version can be found in ``./foxnews/old_scripts``.

An existing dataset containing roughly ~1.7GB of text has been collecting, containing articles up
to around November of 2018.

### Stormfront
"Stormfront is a white nationalist, white supremacist, antisemitic, Holocaust denial, neo-Nazi Internet forum,
and the Web's first major racial hate site. In addition to its promotion of Holocaust denial, Stormfront has 
increasingly become active in the propagation of Islamophobia."

Stormfront has been successfully scraped up to the beginning of 2019 to produce a dataset of ~5GB of text.
