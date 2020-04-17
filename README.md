# datasources-etl

This repository contains scripts developed as part of an exploration
of data required for initial mapping and the scripts required to
automate data acquisition and transformation tasks to populate a Crash
Move Folder.

A few assumptions for development:

* Scripts are developed in Python
* Data transformations rely, where possible, exclusively on Python
  libraries or shell one-liners


## Setting up the environment 

* Create a conda environment and activate it:
```
conda create --name datasources-etl 
activate datasources-etl 
```
* Install the requirements:
```
conda install --file requirements.txt
```
* Some packages are not available through conda. Install them using pip:
```
pip install -r requirements-pip.txt 
```

## Installing and Running

* To install datasources-etl and set up the entry points fun:
```
pip install .
```

* To execute a rule using snakemake:
```
snakemake ${RULE_NAME}
```
