import os.path
import yaml
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String


def create_db_engine(config_path):
    config_path = os.path.expanduser(config_path)

    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    db_path = (
        f"postgresql://{config['username']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['db_name']}"
    )
    engine = create_engine(db_path)
    return engine


def create_customer_table(engine):
    metadata_obj = MetaData()
    customer_table = Table(
        "customer",
        metadata_obj,
        Column('id', Integer, primary_key=True),
        Column('lastname', String(5)),
        Column('firstname', String(5)),
        Column('sex', String(2)),
        Column('birthdate', String(8)),
        Column('joindate', String(8))
    )
    metadata_obj.create_all(engine)
