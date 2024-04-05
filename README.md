# Project Jurivoc


## Requirements

* Python 3.6


## Installation

1. Clone the repository

```sh
git clone git@github.com:/sparna-git/Jurivoc.git
```

2. Install pip

```sh
sudo apt install python3-pip
```

On Windows, PIP is already included for versions of Python > 3.4.

3. Install virtualenv

```sh
pip install virtualenv 
# You may need to do this on Linux :
# sudo apt install python3.12-venv
```

4. Create virtualenv

```sh
python3.12 -m venv virtualenv
```

5. Activate virtualenv

```sh
Windows : virtualenv/Scripts/activate.bat
Linux : source virtualenv/bin/activate
```

6. Once in the virtual env, install the necessary dependencies from `requirements.txt` :

```sh
pip install -r requirements.txt
```


## Running the Python script

/!\ Make sure you are in the virtualenv !

The command synopsis is the following:

```sh
  python convert_data_jurivoc.py --data <directory input files > --output <directory output> --log <directory log> --previousVersion <directory of previous version>
```

e.g, without a previous version (= initial run):

```sh
python convert_data_jurivoc.py --data inputs --output jurivoc_graph --log jurivoc_log
```

with a previous version :

```sh
python convert_data_jurivoc.py --data inputs --output jurivoc_graph --log jurivoc_log --previousVersion jurivoc_graph_v1
```

The parameters are the following:

- `--data` Directory containing the Jurivoc files. (required) :
  - jurivoc_fre.txt
  - jurivoc_ger.txt
  - jurivoc_ita.txt
  - jurivoc_fre_ger.txt
  - jurivoc_fre_ita.txt
- `--output` Result Directory (required)
- `--log` (optional) Log Directory where the raw dataframes resulting from file parsing will be logged (optional). This directory will also contain a Turtle log of the graph before trying to retrieve the URIs from the previous version.
- `--previousVersion` (optional) directory where the previous version of jurivoc will be read to fetch the previous URIs (that directory is expected to contain the file `jurivoc.ttl` that was the output of the previous run)

## Notes on URI

The URI generation works in 2 steps :

1. In the first step, URIs are given based on the French labels. e.g. `jurivoc:PUBLICATION_ELECTRONIQUE`. The SKOS thesaurus with these URIs is logged into `<log directory>/jurivoc_with_label_uris.ttl`
2. Then, in a second step, 2 things can happen :
  1. Either the parameter `--previousVersion` was *not* provided, indicating that it is the initial run, then a sequential id will be given to every concept based on the alphabetical order of their URI
  2. Either the parameter `--previousVersion` was provided, then an attempt is made to retrieve the previous URI from the previous version :
    - A search is made on the French, Italian and German prefLabel of each concept. If _1_ prefLabel matches, then the URI is retrieved from the previous concept. This means that if 1 or 2 prefLabel have changed, but one stayed the same, the Concept will retain its previous URI
    - If no prefLabel matched, a new URI based on the sequential identifier will be given to the concept 

## Notes

The conversion takes about 15 minutes to complete.

The conversion assumes that the input files are named like the one documented above, to know the language of the labels. Do not rename the files.

The structure of the thesaurus is read from the French variant. The german and italian variants are used to fetch the corresponding labels (pref and alt) and notes, but not the broader/narrower/related.
