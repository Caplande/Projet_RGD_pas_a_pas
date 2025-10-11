from sqlalchemy import Column, Integer, Text, Float, Boolean, Date, DateTime, Numeric, INTEGER, TEXT, BIGINT, REAL, FLOAT, VARCHAR, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TBaseData(Base):
    __tablename__ = 't_base_data'
    id = Column(INTEGER, primary_key=True)
    type_appel = Column(TEXT(2))
    exercice = Column(TEXT(4))
    periode_cloturee = Column(TEXT)
    bat = Column(TEXT(3))
    bat_tit = Column(TEXT(50))
    rub = Column(TEXT(2))
    rub_tit = Column(TEXT(50))
    typ = Column(TEXT(3))
    typ_tit = Column(TEXT(50))
    date_a = Column(REAL)
    libelle = Column(TEXT(50))
    reference = Column(TEXT(50))
    montant = Column(FLOAT)
    nom_fournisseur = Column(TEXT(50))
    rang_doublon = Column(TEXT(2))
    groupe = Column(TEXT(50))
    cle = Column(VARCHAR)
