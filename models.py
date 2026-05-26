from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    Date,
    DateTime,
    Boolean,
    Text,
    Table,
    desc,
    BigInteger
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from pydantic import BaseModel
from typing import List, Optional

from datetime import datetime

import uuid
from models import *
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(100),
        nullable=False
    )

    code = Column(
        String(30),
        nullable=False,
        unique=True
    )

    description = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    versions = relationship(
        "CostBaseVersion",
        back_populates="cost_base",
        cascade="all, delete-orphan"
    )


# =========================================
# VERSÕES DAS BASES
# =========================================

class CostBaseVersion(Base):
    __tablename__ = "cost_base_versions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    cost_base_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "cost_bases.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    state_code = Column(
        String(2)
    )

    month = Column(
        Integer,
        nullable=False
    )

    year = Column(
        Integer,
        nullable=False
    )

    is_desonerado = Column(
        Boolean,
        default=False
    )

    source_file_name = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    cost_base = relationship(
        "CostBase",
        back_populates="versions"
    )

    services = relationship(
        "CostService",
        back_populates="version",
        cascade="all, delete-orphan"
    )

    inputs = relationship(
        "CostInput",
        back_populates="version",
        cascade="all, delete-orphan"
    )

    import_jobs = relationship(
        "ImportJob",
        back_populates="version"
    )


# =========================================
# SERVIÇOS / COMPOSIÇÕES
# =========================================

class CostService(Base):
    __tablename__ = "cost_services"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    version_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "cost_base_versions.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    code = Column(
        String(50),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    unit = Column(
        String(20)
    )

    unit_cost = Column(
        Float,
        default=0
    )

    labor_cost = Column(
        Float,
        default=0
    )

    material_cost = Column(
        Float,
        default=0
    )

    equipment_cost = Column(
        Float,
        default=0
    )

    total_cost = Column(
        Float,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    version = relationship(
        "CostBaseVersion",
        back_populates="services"
    )

    compositions = relationship(
        "ServiceComposition",
        back_populates="service",
        cascade="all, delete-orphan"
    )

    budget_items = relationship(
        "BudgetItem",
        back_populates="service"
    )


# =========================================
# INSUMOS
# =========================================

class CostInput(Base):
    __tablename__ = "cost_inputs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    version_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "cost_base_versions.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    code = Column(
        String(50)
    )

    description = Column(
        Text,
        nullable=False
    )

    unit = Column(
        String(20)
    )

    unit_cost = Column(
        Float,
        default=0
    )

    input_type = Column(
        String(30)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    version = relationship(
        "CostBaseVersion",
        back_populates="inputs"
    )

    compositions = relationship(
        "ServiceComposition",
        back_populates="input"
    )

    custom_prices = relationship(
        "CompanyInputPrice",
        back_populates="input"
    )


# =========================================
# COMPOSIÇÃO DOS SERVIÇOS
# =========================================

class ServiceComposition(Base):
    __tablename__ = "service_compositions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "cost_services.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    input_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "cost_inputs.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    coefficient = Column(
        Float,
        default=0
    )

    unit = Column(
        String(20)
    )

    unit_cost = Column(
        Float,
        default=0
    )

    total_cost = Column(
        Float,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    service = relationship(
        "CostService",
        back_populates="compositions"
    )

    input = relationship(
        "CostInput",
        back_populates="compositions"
    )


# =========================================
# PREÇOS CUSTOMIZADOS DE INSUMOS
# =========================================

class CompanyInputPrice(Base):
    __tablename__ = "company_input_prices"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    input_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "cost_inputs.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    supplier_name = Column(
        String(255)
    )

    custom_cost = Column(
        Float,
        nullable=False
    )

    valid_from = Column(Date)

    valid_to = Column(Date)

    notes = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    input = relationship(
        "CostInput",
        back_populates="custom_prices"
    )


# =========================================
# ORÇAMENTOS
# =========================================

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    number = Column(
        String(50),
        nullable=False,
        unique=True
    )

    type = Column(
        String(20),
        nullable=False
    )

    client_name = Column(
        String(255)
    )

    project_name = Column(
        String(255)
    )

    status = Column(
        String(30),
        default="DRAFT"
    )

    total_cost = Column(
        Float,
        default=0
    )

    total_sale = Column(
        Float,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    items = relationship(
        "BudgetItem",
        back_populates="budget",
        cascade="all, delete-orphan"
    )

    bdi_links = relationship(
        "BudgetBDITemplateLink",
        back_populates="budget",
        cascade="all, delete-orphan"
    )

    schedules = relationship(
        "BudgetSchedule",
        back_populates="budget",
        cascade="all, delete-orphan"
    )

# =========================================
# ITENS DO ORÇAMENTO
# =========================================

class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    budget_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budgets.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # =========================================
    # HIERARQUIA
    # =========================================

    parent_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budget_items.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    hierarchy_level = Column(
        Integer,
        default=1
    )

    sort_order = Column(
        Integer,
        default=0
    )

    is_group = Column(
        Boolean,
        default=False
    )

    # =========================================
    # ITEM
    # =========================================

    item_order = Column(Integer)

    item_code = Column(
        String(50)
    )

    description = Column(
        Text,
        nullable=False
    )

    unit = Column(
        String(20)
    )

    quantity = Column(
        Float,
        default=0
    )

    # =========================================
    # CUSTOS
    # =========================================

    # valor original vindo da base SINAPI/SICRO/etc
    base_unit_cost = Column(
        Float,
        default=0
    )

    # valor final editado no orçamento
    unit_cost = Column(
        Float,
        default=0
    )

    bdi_percentage = Column(
        Float,
        default=0
    )

    sale_price = Column(
        Float,
        default=0
    )

    total_cost = Column(
        Float,
        default=0
    )

    total_sale = Column(
        Float,
        default=0
    )

    # =========================================
    # SERVIÇO VINCULADO
    # =========================================

    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "cost_services.id"
        ),
        nullable=True
    )

    # =========================================
    # DATAS
    # =========================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # =========================================
    # RELACIONAMENTOS
    # =========================================

    budget = relationship(
        "Budget",
        back_populates="items"
    )

    service = relationship(
        "CostService",
        back_populates="budget_items"
    )

    parent = relationship(
        "BudgetItem",
        remote_side=[id]
    )


# =========================================
# TEMPLATES BDI
# =========================================

class BudgetBDITemplate(Base):
    __tablename__ = "budget_bdi_templates"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(255),
        nullable=False
    )

    percentage = Column(
        Float,
        nullable=False
    )

    description = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    budget_links = relationship(
        "BudgetBDITemplateLink",
        back_populates="bdi_template"
    )


# =========================================
# RELAÇÃO ORÇAMENTO -> BDI
# =========================================

class BudgetBDITemplateLink(Base):
    __tablename__ = "budget_bdi_template_links"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    budget_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budgets.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    bdi_template_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budget_bdi_templates.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    budget = relationship(
        "Budget",
        back_populates="bdi_links"
    )

    bdi_template = relationship(
        "BudgetBDITemplate",
        back_populates="budget_links"
    )


# =========================================
# IMPORTAÇÕES
# =========================================

class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    cost_base_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "cost_base_versions.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False
    )

    file_name = Column(Text)

    total_services = Column(
        Integer,
        default=0
    )

    total_inputs = Column(
        Integer,
        default=0
    )

    error_message = Column(Text)

    started_at = Column(
        DateTime(timezone=True)
    )

    finished_at = Column(
        DateTime(timezone=True)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    version = relationship(
        "CostBaseVersion",
        back_populates="import_jobs"
    )

# =========================================
# CRONOGRAMAS
# =========================================

class BudgetSchedule(Base):
    __tablename__ = "budget_schedules"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    budget_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budgets.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    name = Column(
        String(255),
        nullable=False
    )

    description = Column(Text)

    start_date = Column(Date)

    end_date = Column(Date)

    baseline_start_date = Column(Date)

    baseline_end_date = Column(Date)

    status = Column(
        String(30),
        default="PLANNING"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    budget = relationship(
        "Budget"
    )

    tasks = relationship(
        "BudgetScheduleTask",
        back_populates="schedule",
        cascade="all, delete-orphan",
        order_by="BudgetScheduleTask.sort_order"
    )

    budget = relationship(
        "Budget",
        back_populates="schedules"
    )



# =========================================
# TAREFAS
# =========================================

class BudgetScheduleTask(Base):
    __tablename__ = "budget_schedule_tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    schedule_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budget_schedules.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    parent_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budget_schedule_tasks.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    budget_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budget_items.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    hierarchy_level = Column(
        Integer,
        default=1
    )

    sort_order = Column(
        Integer,
        default=0
    )

    is_group = Column(
        Boolean,
        default=False
    )

    code = Column(String(50))

    name = Column(
        Text,
        nullable=False
    )

    description = Column(Text)

    task_type = Column(
        String(30),
        default="TASK"
    )

    duration_days = Column(
        Integer,
        default=0
    )

    progress_percentage = Column(
        Float,
        default=0
    )

    start_date = Column(Date)

    end_date = Column(Date)

    actual_start_date = Column(Date)

    actual_end_date = Column(Date)

    baseline_start_date = Column(Date)

    baseline_end_date = Column(Date)

    planned_cost = Column(
        Float,
        default=0
    )

    actual_cost = Column(
        Float,
        default=0
    )

    responsible = Column(String(255))

    color = Column(String(20))

    notes = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    schedule = relationship(
        "BudgetSchedule",
        back_populates="tasks"
    )

    budget_item = relationship(
        "BudgetItem"
    )

    parent = relationship(
        "BudgetScheduleTask",
        remote_side=[id]
    )

    predecessors = relationship(
        "BudgetScheduleDependency",
        foreign_keys="BudgetScheduleDependency.successor_task_id",
        cascade="all, delete-orphan"
    )

    successors = relationship(
        "BudgetScheduleDependency",
        foreign_keys="BudgetScheduleDependency.predecessor_task_id",
        cascade="all, delete-orphan"
    )


# =========================================
# DEPENDÊNCIAS
# =========================================

class BudgetScheduleDependency(Base):
    __tablename__ = "budget_schedule_dependencies"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    schedule_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budget_schedules.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    predecessor_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budget_schedule_tasks.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    successor_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "budget_schedule_tasks.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    dependency_type = Column(
        String(10),
        default="FS"
    )

    lag_days = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    predecessor_task = relationship(
        "BudgetScheduleTask",
        foreign_keys=[predecessor_task_id]
    )

    successor_task = relationship(
        "BudgetScheduleTask",
        foreign_keys=[successor_task_id]
    )

# =========================================================
# PASTAS
# =========================================================

class ProjectFolder(Base):

    __tablename__ = "project_folders"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        Integer,
        ForeignKey("projetos.id", ondelete="CASCADE"),
        nullable=False
    )

    parent_folder_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "project_folders.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    name = Column(String)

    created_by = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow
    )

# =========================================================
# ARQUIVOS
# =========================================================

class ProjectFile(Base):

    __tablename__ = "project_files"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        Integer,
        ForeignKey("projetos.id", ondelete="CASCADE"),
        nullable=False
    )

    folder_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "project_folders.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    file_name = Column(String)

    original_name = Column(String)

    file_url = Column(Text)

    file_size = Column(BigInteger)

    mime_type = Column(String)

    extension = Column(String)

    uploaded_by = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow
    )