from sqlalchemy import create_engine
from api.models.user import Base


def reset_database(db_url):
    engine = create_engine(db_url, echo=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    DB_URL = "mysql+pymysql://root:root_password@database:3306/demo?charset=utf8"
    reset_database(DB_URL)