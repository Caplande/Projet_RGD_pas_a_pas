from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, Float, Index, Integer, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class TAgregation(Base):
    __tablename__ = 't_agregation'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    type_appel: Mapped[Optional[str]] = mapped_column(Text(2))
    libelle1: Mapped[Optional[str]] = mapped_column(Text)
    debut_periode: Mapped[Optional[str]] = mapped_column(Text(10))
    fin_periode: Mapped[Optional[str]] = mapped_column(Text(10))
    periode_cloturee: Mapped[Optional[str]] = mapped_column(Text)
    bat: Mapped[Optional[str]] = mapped_column(Text(3))
    bat_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    rub: Mapped[Optional[str]] = mapped_column(Text(2))
    rub_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    typ: Mapped[Optional[str]] = mapped_column(Text(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    date: Mapped[Optional[str]] = mapped_column(Text(10))
    libelle: Mapped[Optional[str]] = mapped_column(Text(50))
    reference: Mapped[Optional[str]] = mapped_column(Text(50))
    montant: Mapped[Optional[float]] = mapped_column(Float)
    nom_fournisseur: Mapped[Optional[str]] = mapped_column(Text(50))


class TClesRepartition(Base):
    __tablename__ = 't_cles_repartition'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    base_rep: Mapped[Optional[str]] = mapped_column(Text(20))
    E: Mapped[Optional[float]] = mapped_column(Float)
    R: Mapped[Optional[float]] = mapped_column(Float)
    G: Mapped[Optional[float]] = mapped_column(Float)
    V: Mapped[Optional[float]] = mapped_column(Float)
    ASL: Mapped[Optional[float]] = mapped_column(Float)
    ER: Mapped[Optional[float]] = mapped_column(Float)
    ERG: Mapped[Optional[float]] = mapped_column(Float)
    Verif: Mapped[Optional[int]] = mapped_column(BigInteger)


class TData(Base):
    __tablename__ = 't_data'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    type_appel: Mapped[Optional[str]] = mapped_column(Text(2))
    libelle1: Mapped[Optional[str]] = mapped_column(Text)
    debut_periode: Mapped[Optional[str]] = mapped_column(Text(10))
    fin_periode: Mapped[Optional[str]] = mapped_column(Text(10))
    periode_cloturee: Mapped[Optional[str]] = mapped_column(Text)
    bat: Mapped[Optional[str]] = mapped_column(Text(3))
    bat_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    rub: Mapped[Optional[str]] = mapped_column(Text(2))
    rub_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    typ: Mapped[Optional[str]] = mapped_column(Text(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    date: Mapped[Optional[str]] = mapped_column(Text(10))
    libelle: Mapped[Optional[str]] = mapped_column(Text(50))
    reference: Mapped[Optional[str]] = mapped_column(Text(50))
    montant: Mapped[Optional[float]] = mapped_column(Float)
    nom_fournisseur: Mapped[Optional[str]] = mapped_column(Text(50))


class TLexiqueBat(Base):
    __tablename__ = 't_lexique_bat'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    bat: Mapped[Optional[str]] = mapped_column(Text(3))
    bat_tit: Mapped[Optional[str]] = mapped_column(Text(50))


class TLexiqueBatrub(Base):
    __tablename__ = 't_lexique_batrub'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    batrub: Mapped[Optional[str]] = mapped_column(Text(6))
    batrub_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    base_rep: Mapped[Optional[str]] = mapped_column(Text(20))
    entites: Mapped[Optional[str]] = mapped_column(Text(30))
    rgpt_entites: Mapped[Optional[str]] = mapped_column(Text(30))


t_t_lexique_cles = Table(
    't_lexique_cles', Base.metadata,
    Column('cle', Text),
    Column('groupe', Text)
)


class TLexiqueRub(Base):
    __tablename__ = 't_lexique_rub'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    rub: Mapped[Optional[str]] = mapped_column(Text(2))
    rub_tit: Mapped[Optional[str]] = mapped_column(Text(50))


class TLexiqueTyp(Base):
    __tablename__ = 't_lexique_typ'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    typ: Mapped[Optional[str]] = mapped_column(Text(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    typ_ambigu: Mapped[Optional[bool]] = mapped_column(Boolean)


class TListeGroupes(Base):
    __tablename__ = 't_liste_groupes'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    groupe: Mapped[Optional[str]] = mapped_column(Text(50))
    recurrent: Mapped[Optional[int]] = mapped_column(BigInteger)


t_t_originel_completee = Table(
    't_originel_completee', Base.metadata,
    Column('id', BigInteger),
    Column('cle', Text),
    Column('exercice', Text(4)),
    Column('periode_cloturee', Text(1)),
    Column('bat', Text(3)),
    Column('rub', Text(2)),
    Column('typ', Text(3)),
    Column('typ_tit', Text(50)),
    Column('batrubtyp', Text(10)),
    Column('batrub', Text(6)),
    Column('date', Text(10)),
    Column('libelle', Text(50)),
    Column('reference', Text(50)),
    Column('montant1', Float),
    Column('nom_fournisseur', Text(50)),
    Column('rang_doublon', Text(2)),
    Column('groupe', Text(50)),
    Column('montant', Float),
    Index('ix_t_originel_completee_id', 'id')
)


class TParametres(Base):
    __tablename__ = 't_parametres'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    indicateur: Mapped[Optional[str]] = mapped_column(Text(50))
    valeur: Mapped[Optional[str]] = mapped_column(Text(20))
