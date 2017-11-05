from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, CatalogItem, User

engine = create_engine('sqlite:///catalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
user1 = User(name="Rick", email="pickleRick@udacity.com",
             picture='https://vignette.wikia.nocookie.net/rickandmorty/images/7/7b/Picklerick.jpg/revision/latest?cb=20170725205548.png')
session.add(user1)
session.commit()

# Category - Basketball
category1 = Category(id=1, name="Basketball", user_id=1)

session.add(category1)
session.commit()

# Category - Soccer
category2 = Category(id=2, name="Soccer", user_id=1)

session.add(category2)
session.commit()

catalogItem1 = CatalogItem(id=1, title="Jordon's", description="Light and tight!",
                     category_id=1, category=category1, user_id=1)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(id=2, title="AirMax", description="Air bubble technology rocks.",
                     category_id=1, category=category1, user_id=1)

session.add(catalogItem2)
session.commit()

print "Items added!"
