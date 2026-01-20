from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func, JSON
from database import Base
import datetime

from core import create_tables, insert_data, drop_tables



class DefaultBase(Base):
    __abstract__ = True

    Id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True, sort_order=-10)
    CreatedAt: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), sort_order=20)
    UpdatedAt: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), onupdate=datetime.datetime.now, sort_order=21)

class HumanBase(DefaultBase):
    __abstract__ = True
    FirstName: Mapped[str] = mapped_column(sort_order=1)
    SecondName: Mapped[str] = mapped_column(sort_order=2)
    Patronomyc: Mapped[str] = mapped_column(sort_order=3)

class ProfessionsTable(DefaultBase):
    __tablename__ = "Professions"
    Name: Mapped[str]

    workers_rel = relationship("WorkersTable", backref="profession_rel")

class WorkersTable(HumanBase):
    __tablename__ = "Workers"

    ProfessionId: Mapped[int] = mapped_column(ForeignKey("Professions.Id"))

    patients = relationship("PatientsTable", backref="workers_rel")
    treatments = relationship("AssignedTreatmentTable", backref="workers_rel")
    visits = relationship("VisitsTable", backref="workers_rel")

class PatientsTable(HumanBase):
    __tablename__ = "Patients"
    Age: Mapped[int]
    SNILS: Mapped[str]
    POLIS: Mapped[str]

    CureDoctorId: Mapped[int] = mapped_column(ForeignKey("Workers.Id"))

    research = relationship("ResearchTable", backref="patients_rel")
    treatments = relationship("AssignedTreatmentTable", backref="patients_rel")
    visits = relationship("VisitsTable", backref="patients_rel")
    pulse_monitoring = relationship("PulseMonitoringTable", backref="patients_rel")

class TypesOfDrugsTable(Base):
    __tablename__ = "DrugTypes"
    Id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    Name: Mapped[str]

    drugs_rel = relationship("DrugsTable", backref="drugtypes_rel")

class DrugsTable(DefaultBase):
    __tablename__ = "Drugs"
    Name: Mapped[str]

    TypeId: Mapped[int] = mapped_column(ForeignKey("DrugTypes.Id"))

    forbidden_groups_rel = relationship("ForbiddenGroupsTable", backref="drugs_rel")


class ResearchTable(DefaultBase):
    __tablename__ = "MedicalResearch"
    Name: Mapped[str]
    State: Mapped[str]
    EventDate: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    Result: Mapped[str]
    
    PatientId: Mapped[int] = mapped_column(ForeignKey("Patients.Id"))

class GroupsTable(Base):
    __tablename__ = "Groups"
    Id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    Name: Mapped[str]

    forbidden_groups_rel = relationship("ForbiddenGroupsTable", backref="groups_rel")

class ForbiddenGroupsTable(Base):
    __tablename__ = "DrugForbiddenGroups"
    Id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)

    DrugId: Mapped[int] = mapped_column(ForeignKey("Drugs.Id"))
    GroupId: Mapped[int] = mapped_column(ForeignKey("Groups.Id"))

class VisitsTable(DefaultBase):
    __tablename__ = "Visits"
    VisitDate: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    PatientId: Mapped[int] = mapped_column(ForeignKey("Patients.Id"))
    DoctorId: Mapped[int] = mapped_column(ForeignKey("Workers.Id"))

    Complain: Mapped[str]
    Symptoms: Mapped[dict] = mapped_column(JSON)

    TreatmentId: Mapped[int] = mapped_column(ForeignKey("AssignedTreatment.Id"))

class AssignedTreatmentTable(DefaultBase):
    __tablename__ = "AssignedTreatment"
    TreatmentDate: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    TreatmentScheme: Mapped[dict] = mapped_column(JSON)

    PatientId: Mapped[int] = mapped_column(ForeignKey("Patients.Id"))
    DoctorId: Mapped[int] = mapped_column(ForeignKey("Workers.Id"))

    visits = relationship("VisitsTable", backref="treatment_rel")

class PulseMonitoringTable(DefaultBase):
    __tablename__ = "PulseMonitoring"
    PatientId: Mapped[int] = mapped_column(ForeignKey("Patients.Id"))
    Value: Mapped[int] = mapped_column(nullable=1)

create_tables()

