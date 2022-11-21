import json

import pandas as pd
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pydantic.typing import Optional

from pandahub.api.dependencies import pandahub

router = APIRouter(
    prefix="/variants",
    tags=["variants"]
)


# -------------------------------
#  ROUTES
# -------------------------------

class GetVariantsModel(BaseModel):
    project_id: str

class CreateVariantModel(BaseModel):
    project_id: str
    index: Optional[int] = None

@router.post("/get_variants")
def get_variants(data: GetVariantsModel, ph=Depends(pandahub)):
    project_id = data.project_id
    ph.set_active_project_by_id(project_id)
    db = ph._get_project_database()

    variants = db["net_variant"].find({}, projection={"_id": 0})
    response = {}
    for var in variants:
        response[var.pop("index")] = var
    return response


@router.post("/create_variant")
def create_variant(data: CreateVariantModel, ph=Depends(pandahub)):
    project_id = data.project_id
    ph.set_active_project_by_id(project_id)
    db = ph._get_project_database()
    if not data.index:
        idx_var_db = db["net_variant"].find({}, {"_id": 0, "index": 1}).sort("index", -1).limit(1)
        if idx_var_db.count() == 0:
            data.index = 0
        else:
            data.index = idx_var_db[0]["index"] + 1
    ph.create_variant(data.dict())
