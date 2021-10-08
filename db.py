import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker


engine = sq.create_engine('sqlite://///home/james/PycharmProjects/vkfinder_bot/db.sqlite')
# TODO: ссылка должна быть на относительный путь, поправить к докеру

Session = sessionmaker(bind=engine)
session_db = Session()


if __name__ == '__main__':
    # query = session_db.execute('select * from vkfinder').all()
    # for i in query:
    #     print(i)

    # q = session_db.execute('drop table vkfinder')

    q = session_db.execute('DELETE FROM vkfinder')
    session_db.commit()

    # from models import *
    #
    # q = session_db.query(Vkfinder.url).filter(Vkfinder.user_id == str(3740983)).all()
    # print(len(q))
    # r = [el[0] for el in q]
    # print(r)
    ...
