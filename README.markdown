# Huluobo

A very minimalistic RSS reader.

![screenshot](https://github.com/mfussenegger/Huluobo/raw/master/docs/huluobo.png)


## Installation

Requirements:

 - python33 (recommended) or
 - python27

For Python27 see requirements27.txt  
For Python33 see requirements.txt

    pip install -r requirements.txt

Before the first run it is necessary to create the configuration file and
initialize the database. Any database that is supported by SQLAlchemy should
work.

    cp config.example.py config.py

Edit the file and specify the database connection string. Then create the tables with:

    python schema.py


## Run Huluobo

    python index.py --port=8000
