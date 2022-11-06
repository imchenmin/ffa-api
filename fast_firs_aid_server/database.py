from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://eedtxbzpafwwpv:2b11ddd917be1cbaa9ad3063a4cfa564bc1c4f5739cc9f77ab260e382c81985a@ec2-52-71-69-66.compute-1.amazonaws.com:5432/da84mjkam2mdkf"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()