# Project Jurivoc


## Requirements

* Python 3.12


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

with a previous versio:

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
- `--previousVersion` (optional) directory where the previous version of jurivoc will be read to fetch the previous URIs

## Notes

The conversion takes about 15 minutes to complete.

The conversion assumes that the input files are named like the one documented above, to know the language of the labels. Do not rename the files.

The structure of the thesaurus is read from the French variant. The german and italian variants are used to fetch the corresponding labels (pref and alt) and notes, but not the broader/narrower/related.
