from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class BudgetItemCreate(BaseModel):
    parent_item_id: Optional[str] = None
    hierarchy_level: Optional[int] = 1
    sort_order: Optional[int] = 0
    is_group: Optional[bool] = False
    item_order: Optional[int] = None
    item_code: Optional[str] = None
    description: str
    unit: Optional[str] = None
    quantity: Optional[float] = 0
    unit_cost: Optional[float] = 0
    bdi_percentage: Optional[float] = 0
    service_id: Optional[str] = None

class BudgetCreate(BaseModel):
    number: str
    type: str
    client_name: Optional[str] = None
    project_name: Optional[str] = None
    items: List[BudgetItemCreate]

class BudgetScheduleTaskCreate(BaseModel):
    temp_id: str
    parent_temp_id: Optional[str] = None
    hierarchy_level: Optional[int] = 1
    sort_order: Optional[int] = 0
    is_group: Optional[bool] = False
    budget_item_id: Optional[str] = None
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    task_type: Optional[str] = "TASK"
    duration_days: Optional[int] = 0
    progress_percentage: Optional[float] = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    baseline_start_date: Optional[date] = None
    baseline_end_date: Optional[date] = None
    planned_cost: Optional[float] = 0
    actual_cost: Optional[float] = 0
    responsible: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None

class BudgetScheduleDependencyCreate(BaseModel):
    predecessor_temp_id: str
    successor_temp_id: str
    dependency_type: Optional[str] = "FS"
    lag_days: Optional[int] = 0

class BudgetScheduleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    baseline_start_date: Optional[date] = None
    baseline_end_date: Optional[date] = None
    status: Optional[str] = "PLANNING"
    tasks: List[BudgetScheduleTaskCreate]
    dependencies: List[BudgetScheduleDependencyCreate] = []
