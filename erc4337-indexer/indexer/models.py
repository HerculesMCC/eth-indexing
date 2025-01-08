from sqlalchemy import create_engine, Column, String, Boolean, BigInteger, Integer # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)

class UserOperation(Base):
    __tablename__ = 'user_operations'

    id = Column(Integer, primary_key=True)
    user_op_hash = Column(String, unique=True, index=True)
    sender = Column(String, index=True)
    paymaster = Column(String, index=True)
    nonce = Column(String)
    success = Column(Boolean)
    actual_gas_cost = Column(BigInteger)
    actual_gas_used = Column(BigInteger)
    block_number = Column(BigInteger, index=True)
    timestamp = Column(BigInteger)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)