import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from os import getcwd


cwd = getcwd()

engine = sq.create_engine(f'sqlite:///{cwd}/db.sqlite')


Session = sessionmaker(bind=engine)
session_db = Session()


if __name__ == '__main__':
    # query = session_db.execute('select * from vkfinder').all()
    # for i in query:
    #     print(i)

    # q = session_db.execute('drop table vkfinder')

    # q = session_db.execute('DELETE FROM vkfinder')
    # session_db.commit()

    # from models import *
    #
    # q = session_db.query(Vkfinder.url).filter(Vkfinder.user_id == str(3740983)).all()
    # print(len(q))
    # r = [el[0] for el in q]
    # print(r)
    ...
