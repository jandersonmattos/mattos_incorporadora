from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import SessionLocal
from schemas.budget import BudgetCreate, BudgetScheduleCreate
import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/budgets")
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Budget).filter(models.Budget.number == payload.number).first()
    if exists:
        raise HTTPException(status_code=400, detail="Já existe orçamento com esse número")

    budget = models.Budget(
        number=payload.number,
        type=payload.type,
        client_name=payload.client_name,
        project_name=payload.project_name,
        status="DRAFT",
    )
    db.add(budget)
    db.flush()

    total_cost = 0
    total_sale = 0

    for item in payload.items:
        base_unit_cost = 0
        if item.service_id:
            service = db.query(models.CostService).filter(models.CostService.id == item.service_id).first()
            if not service:
                raise HTTPException(status_code=404, detail=f"Serviço {item.service_id} não encontrado")
            base_unit_cost = service.total_cost or 0

        unit_cost = item.unit_cost if item.unit_cost is not None else base_unit_cost
        quantity = item.quantity or 0
        bdi_percentage = item.bdi_percentage or 0

        total_item_cost = quantity * unit_cost
        sale_price = unit_cost * (1 + (bdi_percentage / 100))
        total_item_sale = sale_price * quantity

        budget_item = models.BudgetItem(
            budget_id=budget.id,
            parent_item_id=item.parent_item_id,
            hierarchy_level=item.hierarchy_level or 1,
            sort_order=item.sort_order or 0,
            is_group=item.is_group or False,
            item_order=item.item_order,
            item_code=item.item_code,
            description=item.description,
            unit=item.unit,
            quantity=quantity,
            base_unit_cost=base_unit_cost,
            unit_cost=unit_cost,
            bdi_percentage=bdi_percentage,
            sale_price=sale_price,
            total_cost=total_item_cost,
            total_sale=total_item_sale,
            service_id=item.service_id,
        )
        db.add(budget_item)
        total_cost += total_item_cost
        total_sale += total_item_sale

    budget.total_cost = total_cost
    budget.total_sale = total_sale
    db.commit()
    db.refresh(budget)

    return {
        "id": str(budget.id),
        "number": budget.number,
        "type": budget.type,
        "client_name": budget.client_name,
        "project_name": budget.project_name,
        "status": budget.status,
        "total_cost": float(budget.total_cost or 0),
        "total_sale": float(budget.total_sale or 0),
    }


@router.get("/budgets")
def get_budgets(db: Session = Depends(get_db)):
    budgets = db.query(models.Budget).all()
    resultado = []

    for budget in budgets:
        total_cost = budget.total_cost or 0
        total_sale = budget.total_sale or 0
        medido = 0
        a_medir = total_sale or total_cost or 0

        resultado.append(
            {
                "id": str(budget.id),
                "numero": budget.number or "",
                "tipo": budget.type or "",
                "cliente": budget.client_name or "",
                "obra": budget.project_name or "",
                "custo": float(total_cost),
                "venda": float(total_sale),
                "medicao": "Venda" if total_sale > 0 else "Custo",
                "medido": float(medido),
                "aMedir": float(a_medir),
                "status": budget.status or "",
                "created_at": budget.created_at,
            }
        )

    return resultado


@router.get("/budgets/{budget_id}")
def get_budget(budget_id: str, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    items = []
    for item in sorted(budget.items, key=lambda x: x.item_order or 0):
        items.append(
            {
                "id": str(item.id),
                "parent_item_id": str(item.parent_item_id) if item.parent_item_id else None,
                "item_order": item.item_order,
                "item_code": item.item_code or "",
                "description": item.description or "",
                "unit": item.unit or "",
                "quantity": float(item.quantity or 0),
                "unit_cost": float(item.unit_cost or 0),
                "bdi_percentage": float(item.bdi_percentage or 0),
                "sale_price": float(item.sale_price or 0),
                "total_cost": float(item.total_cost or 0),
                "total_sale": float(item.total_sale or 0),
                "service_id": str(item.service_id) if item.service_id else None,
            }
        )

    return {
        "id": str(budget.id),
        "number": budget.number or "",
        "type": budget.type or "",
        "client_name": budget.client_name or "",
        "project_name": budget.project_name or "",
        "status": budget.status or "",
        "total_cost": float(budget.total_cost or 0),
        "total_sale": float(budget.total_sale or 0),
        "created_at": budget.created_at,
        "updated_at": budget.updated_at,
        "items": items,
    }


@router.put("/budgets/{budget_id}")
def update_budget(budget_id: str, payload: BudgetCreate, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    exists = db.query(models.Budget).filter(models.Budget.number == payload.number, models.Budget.id != budget.id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Já existe orçamento com esse número")

    budget.number = payload.number
    budget.type = payload.type
    budget.client_name = payload.client_name
    budget.project_name = payload.project_name

    db.query(models.BudgetItem).filter(models.BudgetItem.budget_id == budget.id).delete()

    total_cost = 0
    total_sale = 0

    for item in payload.items:
        base_unit_cost = 0
        if item.service_id:
            service = db.query(models.CostService).filter(models.CostService.id == item.service_id).first()
            if not service:
                raise HTTPException(status_code=404, detail=f"Serviço {item.service_id} não encontrado")
            base_unit_cost = service.total_cost or 0

        unit_cost = item.unit_cost if item.unit_cost is not None else base_unit_cost
        quantity = item.quantity or 0
        bdi_percentage = item.bdi_percentage or 0

        total_item_cost = quantity * unit_cost
        sale_price = unit_cost * (1 + (bdi_percentage / 100))
        total_item_sale = sale_price * quantity

        budget_item = models.BudgetItem(
            budget_id=budget.id,
            parent_item_id=item.parent_item_id,
            hierarchy_level=item.hierarchy_level or 1,
            sort_order=item.sort_order or 0,
            is_group=item.is_group or False,
            item_order=item.item_order,
            item_code=item.item_code,
            description=item.description,
            unit=item.unit,
            quantity=quantity,
            base_unit_cost=base_unit_cost,
            unit_cost=unit_cost,
            bdi_percentage=bdi_percentage,
            sale_price=sale_price,
            total_cost=total_item_cost,
            total_sale=total_item_sale,
            service_id=item.service_id,
        )
        db.add(budget_item)
        total_cost += total_item_cost
        total_sale += total_item_sale

    budget.total_cost = total_cost
    budget.total_sale = total_sale
    db.commit()
    db.refresh(budget)

    return {
        "id": str(budget.id),
        "number": budget.number,
        "type": budget.type,
        "client_name": budget.client_name,
        "project_name": budget.project_name,
        "status": budget.status,
        "total_cost": float(budget.total_cost or 0),
        "total_sale": float(budget.total_sale or 0),
    }


@router.delete("/budgets/{budget_id}")
def delete_budget(budget_id: str, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    db.delete(budget)
    db.commit()

    return {
        "success": True,
        "message": "Orçamento deletado com sucesso",
        "id": str(budget.id),
    }


@router.get("/budgets/{budget_id}/abc")
def get_budget_abc(budget_id: str, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    items = (
        db.query(models.BudgetItem)
        .filter(models.BudgetItem.budget_id == budget_id, models.BudgetItem.is_group == False)
        .order_by(desc(models.BudgetItem.total_cost))
        .all()
    )

    total_cost = sum(item.total_cost or 0 for item in items)
    accumulated = 0
    result = []

    for index, item in enumerate(items):
        item_total = item.total_cost or 0
        participation = (item_total / total_cost) * 100 if total_cost > 0 else 0
        accumulated += participation

        classification = "C"
        if accumulated <= 80:
            classification = "A"
        elif accumulated <= 95:
            classification = "B"

        result.append(
            {
                "rank": index + 1,
                "item_id": str(item.id),
                "item_code": item.item_code,
                "description": item.description,
                "unit": item.unit,
                "quantity": item.quantity,
                "unit_cost": float(item.unit_cost or 0),
                "total_cost": float(item_total),
                "participation_percentage": round(participation, 2),
                "accumulated_percentage": round(accumulated, 2),
                "classification": classification,
                "service_id": str(item.service_id) if item.service_id else None,
                "service_code": item.service.code if item.service else None,
                "service_description": item.service.description if item.service else None,
            }
        )

    total_a = len([x for x in result if x["classification"] == "A"])
    total_b = len([x for x in result if x["classification"] == "B"])
    total_c = len([x for x in result if x["classification"] == "C"])

    return {
        "budget_id": str(budget.id),
        "budget_number": budget.number,
        "project_name": budget.project_name,
        "total_cost": float(total_cost),
        "summary": {
            "total_items": len(result),
            "class_a_items": total_a,
            "class_b_items": total_b,
            "class_c_items": total_c,
        },
        "items": result,
    }


@router.post("/budgets/{budget_id}/schedule")
def create_budget_schedule(budget_id: str, payload: BudgetScheduleCreate, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    db.query(models.BudgetSchedule).filter(models.BudgetSchedule.budget_id == budget_id).delete()

    schedule = models.BudgetSchedule(
        budget_id=budget.id,
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        baseline_start_date=payload.baseline_start_date,
        baseline_end_date=payload.baseline_end_date,
        status=payload.status or "PLANNING",
    )
    db.add(schedule)
    db.flush()

    task_map = {}
    for task in payload.tasks:
        db_task = models.BudgetScheduleTask(
            schedule_id=schedule.id,
            hierarchy_level=task.hierarchy_level or 1,
            sort_order=task.sort_order or 0,
            is_group=task.is_group or False,
            budget_item_id=task.budget_item_id,
            code=task.code,
            name=task.name,
            description=task.description,
            task_type=task.task_type or "TASK",
            duration_days=task.duration_days or 0,
            progress_percentage=task.progress_percentage or 0,
            start_date=task.start_date,
            end_date=task.end_date,
            actual_start_date=task.actual_start_date,
            actual_end_date=task.actual_end_date,
            baseline_start_date=task.baseline_start_date,
            baseline_end_date=task.baseline_end_date,
            planned_cost=task.planned_cost or 0,
            actual_cost=task.actual_cost or 0,
            responsible=task.responsible,
            color=task.color,
            notes=task.notes,
        )
        db.add(db_task)
        db.flush()
        task_map[str(task.temp_id)] = db_task.id

    for task in payload.tasks:
        if task.parent_temp_id:
            db_task_id = task_map.get(str(task.temp_id))
            parent_task_id = task_map.get(str(task.parent_temp_id))
            db.query(models.BudgetScheduleTask).filter(models.BudgetScheduleTask.id == db_task_id).update({"parent_task_id": parent_task_id})

    for dependency in payload.dependencies:
        predecessor_id = task_map.get(str(dependency.predecessor_temp_id))
        successor_id = task_map.get(str(dependency.successor_temp_id))
        if not predecessor_id or not successor_id:
            continue

        db_dependency = models.BudgetScheduleDependency(
            schedule_id=schedule.id,
            predecessor_task_id=predecessor_id,
            successor_task_id=successor_id,
            dependency_type=dependency.dependency_type or "FS",
            lag_days=dependency.lag_days or 0,
        )
        db.add(db_dependency)

    db.commit()
    db.refresh(schedule)

    return {
        "id": str(schedule.id),
        "budget_id": str(schedule.budget_id),
        "name": schedule.name,
        "status": schedule.status,
    }


@router.get("/budgets/{budget_id}/schedule")
def get_budget_schedule(budget_id: str, db: Session = Depends(get_db)):
    schedule = db.query(models.BudgetSchedule).filter(models.BudgetSchedule.budget_id == budget_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Cronograma não encontrado")

    tasks = []
    schedule_tasks = db.query(models.BudgetScheduleTask).filter(models.BudgetScheduleTask.schedule_id == schedule.id).order_by(models.BudgetScheduleTask.sort_order).all()
    for task in schedule_tasks:
        tasks.append(
            {
                "id": str(task.id),
                "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None,
                "budget_item_id": str(task.budget_item_id) if task.budget_item_id else None,
                "hierarchy_level": task.hierarchy_level,
                "sort_order": task.sort_order,
                "is_group": task.is_group,
                "code": task.code,
                "name": task.name,
                "description": task.description,
                "task_type": task.task_type,
                "duration_days": task.duration_days,
                "progress_percentage": float(task.progress_percentage or 0),
                "start_date": task.start_date,
                "end_date": task.end_date,
                "actual_start_date": task.actual_start_date,
                "actual_end_date": task.actual_end_date,
                "baseline_start_date": task.baseline_start_date,
                "baseline_end_date": task.baseline_end_date,
                "planned_cost": float(task.planned_cost or 0),
                "actual_cost": float(task.actual_cost or 0),
                "responsible": task.responsible,
                "color": task.color,
                "notes": task.notes,
            }
        )

    dependencies = []
    schedule_dependencies = db.query(models.BudgetScheduleDependency).filter(models.BudgetScheduleDependency.schedule_id == schedule.id).all()
    for dependency in schedule_dependencies:
        dependencies.append(
            {
                "id": str(dependency.id),
                "predecessor_task_id": str(dependency.predecessor_task_id),
                "successor_task_id": str(dependency.successor_task_id),
                "dependency_type": dependency.dependency_type,
                "lag_days": dependency.lag_days,
            }
        )

    return {
        "id": str(schedule.id),
        "budget_id": str(schedule.budget_id),
        "name": schedule.name,
        "description": schedule.description,
        "status": schedule.status,
        "start_date": schedule.start_date,
        "end_date": schedule.end_date,
        "baseline_start_date": schedule.baseline_start_date,
        "baseline_end_date": schedule.baseline_end_date,
        "tasks": tasks,
        "dependencies": dependencies,
    }


@router.put("/budgets/{budget_id}/schedule")
def update_budget_schedule(budget_id: str, payload: BudgetScheduleCreate, db: Session = Depends(get_db)):
    schedule = db.query(models.BudgetSchedule).filter(models.BudgetSchedule.budget_id == budget_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Cronograma não encontrado")

    schedule.name = payload.name
    schedule.description = payload.description
    schedule.start_date = payload.start_date
    schedule.end_date = payload.end_date
    schedule.baseline_start_date = payload.baseline_start_date
    schedule.baseline_end_date = payload.baseline_end_date
    schedule.status = payload.status or "PLANNING"

    db.query(models.BudgetScheduleDependency).filter(models.BudgetScheduleDependency.schedule_id == schedule.id).delete()
    db.query(models.BudgetScheduleTask).filter(models.BudgetScheduleTask.schedule_id == schedule.id).delete()

    task_map = {}
    for task in payload.tasks:
        db_task = models.BudgetScheduleTask(
            schedule_id=schedule.id,
            hierarchy_level=task.hierarchy_level or 1,
            sort_order=task.sort_order or 0,
            is_group=task.is_group or False,
            budget_item_id=task.budget_item_id,
            code=task.code,
            name=task.name,
            description=task.description,
            task_type=task.task_type or "TASK",
            duration_days=task.duration_days or 0,
            progress_percentage=task.progress_percentage or 0,
            start_date=task.start_date,
            end_date=task.end_date,
            actual_start_date=task.actual_start_date,
            actual_end_date=task.actual_end_date,
            baseline_start_date=task.baseline_start_date,
            baseline_end_date=task.baseline_end_date,
            planned_cost=task.planned_cost or 0,
            actual_cost=task.actual_cost or 0,
            responsible=task.responsible,
            color=task.color,
            notes=task.notes,
        )
        db.add(db_task)
        db.flush()
        task_map[str(task.temp_id)] = db_task.id

    for task in payload.tasks:
        if task.parent_temp_id:
            db_task_id = task_map.get(str(task.temp_id))
            parent_task_id = task_map.get(str(task.parent_temp_id))
            db.query(models.BudgetScheduleTask).filter(models.BudgetScheduleTask.id == db_task_id).update({"parent_task_id": parent_task_id})

    for dependency in payload.dependencies:
        predecessor_id = task_map.get(str(dependency.predecessor_temp_id))
        successor_id = task_map.get(str(dependency.successor_temp_id))
        if not predecessor_id or not successor_id:
            continue

        db_dependency = models.BudgetScheduleDependency(
            schedule_id=schedule.id,
            predecessor_task_id=predecessor_id,
            successor_task_id=successor_id,
            dependency_type=dependency.dependency_type or "FS",
            lag_days=dependency.lag_days or 0,
        )
        db.add(db_dependency)

    db.commit()
    db.refresh(schedule)

    return {
        "success": True,
        "message": "Cronograma atualizado com sucesso",
        "schedule_id": str(schedule.id),
    }
