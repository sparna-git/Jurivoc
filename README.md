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

# Running the Python script

/!\ Make sure you are in the virtualenv !

The command synopsis is the following:

```python
  python convert_data_jurivoc.py --data <directory input files > --output <directory output> --log <directory log>
```

e.g:

```python
python convert_data_jurivoc.py --data inputs --output jurivoc_graph --log jurivoc_output
```

The parameters are the following:

- `--data` Directory containing Jurivoc files. (required)
- `--output` Result Directory (required)
- `--log` Log Directory (optional)