"""
Establish a connection to the database
"""

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool


def singleton(class_):
    """Source: https://stackoverflow.com/questions/6760685"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class Connection:
    def __init__(self):
        """Establish a connection to the Postgress database"""
        print("Establishing a connection to the database")

        self.connection_string = "{protocol}://{user}:{password}@{host}/{database}?{query}".format(
            protocol="postgresql+psycopg2",
            **st.secrets.db_credentials,
            query="sslmode=require",
        )

        self.engine = create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
        )

    def get(self):
        """
        Get the connection to the database

        Returns
        -------
        sqlalchemy.engine.base.Engine
            Connection to the database
        """
        return self.engine
