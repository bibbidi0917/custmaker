# Python 'custmaker' package

## How to install
```bash
pip install custmaker
```

## How to use

### 0. Prerequisite

#### a) DB config file

1) Make '.sqlalchemy' folder in your home directory.
2) Make 'config.yaml' file in '.sqlalchemy' directory.
   And then set your local database information in the 'config.yaml'.
   
```
username: username
password: password
host: host
port: port
db_name: db_name
```

#### b) population ratio data
In your local database, you should have firstname, lastname, age, sex ratio data.

ex) sex ratio data

|sex|ratio|
|------|---|
|Male|0.4986|
|Female|0.5014|


### 1. Connect to database
Create database engine using the DB config file.

```python
from custmaker.setting import create_db_engine

# create_db_engine(DB config file path)
engine = create_db_engine('~\\.sqlalchemy\\config.yaml')
```

### 2. Create customer table
Create customer DB table using the DB engine.

```python
from custmaker.setting import create_customer_table

# create_customer_table(DB engine)
create_customer_table(engine)
```
### 3. Create customer data

Create customer data repeatly.

```python
from custmaker.making import create_customer

# create_customer(join_date, # of customer, db_engine_name)
create_customer('20211129', 10, engine)
```


## Dependencies
- PyYAML
- SQLAlchemy
- numpy
- pandas