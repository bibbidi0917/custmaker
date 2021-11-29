import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, select
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    lastname = Column(String(5))
    firstname = Column(String(5))
    sex = Column(String(2))
    birthdate = Column(String(8))
    joindate = Column(String(8))


class KoreanLastname(Base):
    __tablename__ = 'korean_lastname'

    lastname = Column(String(5), primary_key=True)
    ratio = Column(Float(8))


class KoreanFirstname(Base):
    __tablename__ = 'korean_firstname'

    firstname = Column(String(5), primary_key=True)
    ratio = Column(Float(8))


class AgeStat(Base):
    __tablename__ = 'age_stat'

    age = Column(String(5), primary_key=True)
    ratio = Column(Float(8))


class RegionStat(Base):
    __tablename__ = 'region_stat'

    region = Column(String(8), primary_key=True)
    ratio = Column(Float(8))


class SexStat(Base):
    __tablename__ = 'sex_stat'

    sex = Column(String(2), primary_key=True)
    ratio = Column(Float(8))


def _create_random_data(dataframe, count):
    value = dataframe.iloc[:, 0].to_numpy()
    prob = dataframe.iloc[:, 1].to_numpy()
    prob /= prob.sum()
    return np.random.choice(value, count, p=prob)


def _calculate_birthyear(data):
    return str(datetime.today().year - int(data[:-1]) + 1)


def create_customer(joindate_d, count, engine):
    session = Session(engine)
    conn = engine.connect()

    # sex
    sex_stat_df = pd.read_sql(select(SexStat), conn)
    new_sex = _create_random_data(sex_stat_df, count)

    # lastname
    lastname_df = pd.read_sql(select(KoreanLastname), conn)
    new_lastname = _create_random_data(lastname_df, count)

    # firstname
    firstname_df = pd.read_sql(select(KoreanFirstname), conn)
    new_firstname = _create_random_data(firstname_df, count)

    # birthyear
    age_stat_df = pd.read_sql(select(AgeStat), conn)
    new_birthyear = _create_random_data(age_stat_df, count)
    calc_birth_func = np.vectorize(_calculate_birthyear)
    new_birthyear = calc_birth_func(new_birthyear)
    new_birthdate = []

    # birthdate
    for year_str in new_birthyear:
        year = int(year_str)
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:  # leap year
            gap_days = np.random.randint(0, 366)
        else:
            gap_days = np.random.randint(0, 365)

        time = datetime(year, int('1'), int('1'))
        new_birthdate.append(
            year_str+(time + timedelta(days=gap_days)).strftime('%m%d'))

    for sex_d, lastname_d, firstname_d, birthdate_d in zip(
        new_sex, new_lastname, new_firstname, new_birthdate
    ):
        session.add(
            Customer(
                lastname=lastname_d, firstname=firstname_d, sex=sex_d,
                birthdate=birthdate_d, joindate=joindate_d
            )
        )

    session.flush()
    session.commit()
