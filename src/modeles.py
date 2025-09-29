from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, Index, Integer, REAL, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TAgregation(Base):
    __tablename__ = 't_agregation'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    type_appel: Mapped[Optional[str]] = mapped_column(Text(2))
    libelle1: Mapped[Optional[str]] = mapped_column(Text)
    periode_cloturee: Mapped[Optional[str]] = mapped_column(Text)
    bat: Mapped[Optional[str]] = mapped_column(Text(3))
    bat_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    rub: Mapped[Optional[str]] = mapped_column(Text(2))
    rub_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    typ: Mapped[Optional[str]] = mapped_column(Text(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(Text(3))
    libelle: Mapped[Optional[str]] = mapped_column(Text(50))
    reference: Mapped[Optional[str]] = mapped_column(Text(50))
    montant: Mapped[Optional[float]] = mapped_column(Float)
    nom_fournisseur: Mapped[Optional[str]] = mapped_column(Text(50))
    debut_periode: Mapped[Optional[float]] = mapped_column(REAL)
    fin_periode: Mapped[Optional[float]] = mapped_column(REAL)
    date_a: Mapped[Optional[float]] = mapped_column(REAL)


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
    periode_cloturee: Mapped[Optional[str]] = mapped_column(Text)
    bat: Mapped[Optional[str]] = mapped_column(Text(3))
    bat_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    rub: Mapped[Optional[str]] = mapped_column(Text(2))
    rub_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    typ: Mapped[Optional[str]] = mapped_column(Text(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    libelle: Mapped[Optional[str]] = mapped_column(Text(50))
    reference: Mapped[Optional[str]] = mapped_column(Text(50))
    montant: Mapped[Optional[float]] = mapped_column(Float)
    nom_fournisseur: Mapped[Optional[str]] = mapped_column(Text(50))
    debut_periode: Mapped[Optional[float]] = mapped_column(REAL)
    fin_periode: Mapped[Optional[float]] = mapped_column(REAL)
    date_a: Mapped[Optional[float]] = mapped_column(REAL)


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


class TOriginelCompletee(Base):
    __tablename__ = 't_originel_completee'
    __table_args__ = (
        Index('ix_t_originel_completee_id', 'id'),
    )

    id: Mapped[Optional[int]] = mapped_column(BigInteger, primary_key=True)
    cle: Mapped[Optional[str]] = mapped_column(Text(150))
    exercice: Mapped[Optional[str]] = mapped_column(Text(4))
    periode_cloturee: Mapped[Optional[str]] = mapped_column(Text(1))
    bat: Mapped[Optional[str]] = mapped_column(Text(3))
    rub: Mapped[Optional[str]] = mapped_column(Text(2))
    typ: Mapped[Optional[str]] = mapped_column(Text(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(Text(50))
    batrubtyp: Mapped[Optional[str]] = mapped_column(Text(8))
    batrub: Mapped[Optional[str]] = mapped_column(Text(5))
    date_a: Mapped[Optional[str]] = mapped_column(Text(10))
    libelle: Mapped[Optional[str]] = mapped_column(Text(50))
    reference: Mapped[Optional[str]] = mapped_column(Text(50))
    montant1: Mapped[Optional[float]] = mapped_column(Float)
    nom_fournisseur: Mapped[Optional[str]] = mapped_column(Text(50))
    rang_doublon: Mapped[Optional[str]] = mapped_column(Text(2))
    groupe: Mapped[Optional[str]] = mapped_column(Text(50))
    montant: Mapped[Optional[float]] = mapped_column(Float)


class TParametres(Base):
    __tablename__ = 't_parametres'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    indicateur: Mapped[Optional[str]] = mapped_column(Text(50))
    valeur: Mapped[Optional[str]] = mapped_column(Text(50))


t_tampon_data = Table(
    'tampon_data', Base.metadata,
    Column('id', BigInteger),
    Column("Type d'appel", Text),
    Column('Libelle', Text),
    Column('Debut de periode', DateTime),
    Column('Fin de periode', DateTime),
    Column('Periode Cloturee', Text),
    Column('Num�ro du batiment', BigInteger),
    Column('Nom du batiment', Text),
    Column('Num�ro de la rubrique', BigInteger),
    Column('Nom de la rubrique', Text),
    Column('Num type charge', BigInteger),
    Column('Nom du type de charge', Text),
    Column('Date', Text),
    Column('Libelle.1', Text),
    Column('Reference', Text),
    Column('Montant � repartir', Float),
    Column('Nom du fournisseur', Text),
    Index('ix_tampon_data_id', 'id')
)


t_tampon_parametres = Table(
    'tampon_parametres', Base.metadata,
    Column('id', BigInteger),
    Column('indicateur', Text),
    Column('valeur', Text),
    Index('ix_tampon_parametres_id', 'id')
)
