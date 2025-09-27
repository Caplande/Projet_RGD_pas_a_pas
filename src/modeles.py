from typing import Optional
from sqlalchemy import BigInteger, Boolean, Float, Index, Integer, Text, String, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date


class Base(DeclarativeBase):
    pass


class TAgregation(Base):
    __tablename__ = 't_agregation'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    type_appel: Mapped[Optional[str]] = mapped_column(String(2))
    libelle1: Mapped[Optional[str]] = mapped_column(Text)
    debut_periode: Mapped[date] = mapped_column(Date)
    fin_periode: Mapped[date] = mapped_column(Date)
    periode_cloturee: Mapped[Optional[str]] = mapped_column(Text)
    bat: Mapped[Optional[str]] = mapped_column(String(3))
    bat_tit: Mapped[Optional[str]] = mapped_column(String(50))
    rub: Mapped[Optional[str]] = mapped_column(String(2))
    rub_tit: Mapped[Optional[str]] = mapped_column(String(50))
    typ: Mapped[Optional[str]] = mapped_column(String(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(String(50))
    date_a: Mapped[date] = mapped_column(Date)
    libelle: Mapped[Optional[str]] = mapped_column(String(50))
    reference: Mapped[Optional[str]] = mapped_column(String(50))
    montant: Mapped[Optional[float]] = mapped_column(Float)
    nom_fournisseur: Mapped[Optional[str]] = mapped_column(String(50))


class TClesRepartition(Base):
    __tablename__ = 't_cles_repartition'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    base_rep: Mapped[Optional[str]] = mapped_column(String(20))
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
    type_appel: Mapped[Optional[str]] = mapped_column(String(2))
    libelle1: Mapped[Optional[str]] = mapped_column(Text)
    debut_periode: Mapped[date] = mapped_column(Date)
    fin_periode: Mapped[date] = mapped_column(Date)
    periode_cloturee: Mapped[Optional[str]] = mapped_column(Text)
    bat: Mapped[Optional[str]] = mapped_column(String(3))
    bat_tit: Mapped[Optional[str]] = mapped_column(String(50))
    rub: Mapped[Optional[str]] = mapped_column(String(2))
    rub_tit: Mapped[Optional[str]] = mapped_column(String(50))
    typ: Mapped[Optional[str]] = mapped_column(String(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(String(50))
    date_a: Mapped[date] = mapped_column(Date)
    libelle: Mapped[Optional[str]] = mapped_column(String(50))
    reference: Mapped[Optional[str]] = mapped_column(String(50))
    montant: Mapped[Optional[float]] = mapped_column(Float)
    nom_fournisseur: Mapped[Optional[str]] = mapped_column(String(50))


class TLexiqueBat(Base):
    __tablename__ = 't_lexique_bat'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    bat: Mapped[Optional[str]] = mapped_column(String(3))
    bat_tit: Mapped[Optional[str]] = mapped_column(String(50))


class TLexiqueBatrub(Base):
    __tablename__ = 't_lexique_batrub'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    batrub: Mapped[Optional[str]] = mapped_column(String(6))
    batrub_tit: Mapped[Optional[str]] = mapped_column(String(50))
    base_rep: Mapped[Optional[str]] = mapped_column(String(20))
    entites: Mapped[Optional[str]] = mapped_column(String(30))
    rgpt_entites: Mapped[Optional[str]] = mapped_column(String(30))


class TLexiqueCles(Base):
    __tablename__ = 't_lexique_cles'

    cle: Mapped[Optional[str]] = mapped_column(Text, primary_key=True)
    groupe: Mapped[Optional[str]] = mapped_column(String(50))


class TLexiqueRub(Base):
    __tablename__ = 't_lexique_rub'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    rub: Mapped[Optional[str]] = mapped_column(String(2))
    rub_tit: Mapped[Optional[str]] = mapped_column(String(50))


class TLexiqueTyp(Base):
    __tablename__ = 't_lexique_typ'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    typ: Mapped[Optional[str]] = mapped_column(String(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(String(50))
    typ_ambigu: Mapped[Optional[bool]] = mapped_column(Boolean)


class TListeGroupes(Base):
    __tablename__ = 't_liste_groupes'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    groupe: Mapped[Optional[str]] = mapped_column(String(50))
    recurrent: Mapped[Optional[int]] = mapped_column(BigInteger)


class TOriginelCompletee(Base):
    __tablename__ = 't_originel_completee'
    __table_args__ = (
        Index('ix_t_originel_completee_id', 'id'),
    )

    id: Mapped[Optional[int]] = mapped_column(BigInteger, primary_key=True)
    cle: Mapped[Optional[str]] = mapped_column(Text)
    exercice: Mapped[Optional[str]] = mapped_column(String(4))
    periode_cloturee: Mapped[Optional[str]] = mapped_column(String(1))
    bat: Mapped[Optional[str]] = mapped_column(String(3))
    rub: Mapped[Optional[str]] = mapped_column(String(2))
    typ: Mapped[Optional[str]] = mapped_column(String(3))
    typ_tit: Mapped[Optional[str]] = mapped_column(String(50))
    batrubtyp: Mapped[Optional[str]] = mapped_column(String(10))
    batrub: Mapped[Optional[str]] = mapped_column(String(6))
    date_a: Mapped[date] = mapped_column(Date)
    libelle: Mapped[Optional[str]] = mapped_column(String(50))
    reference: Mapped[Optional[str]] = mapped_column(String(50))
    montant1: Mapped[Optional[float]] = mapped_column(Float)
    nom_fournisseur: Mapped[Optional[str]] = mapped_column(String(50))
    rang_doublon: Mapped[Optional[str]] = mapped_column(String(2))
    groupe: Mapped[Optional[str]] = mapped_column(String(50))
    montant: Mapped[Optional[float]] = mapped_column(Float)


class TParametres(Base):
    __tablename__ = 't_parametres'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    indicateur: Mapped[Optional[str]] = mapped_column(String(50))
    valeur: Mapped[Optional[str]] = mapped_column(String(20))
