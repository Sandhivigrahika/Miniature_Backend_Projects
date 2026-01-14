from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic import Field, field_validator
from typing import Dict
from uuid import uuid4
from enum import Enum as PyEnum

app = FastAPI()


class Role(PyEnum):
    user= "user"
    admin= "admin"


class EmployeeCreate(BaseModel):
    name: str  = Field(..., min_length=2, max_length=100)
    designation: str = Field(..., min_length=2, max_length=100)
    role: Role
    address: str = Field(..., min_length=2, max_length=100)

    @field_validator("name", "designation", "address")
    @classmethod
    def strip_and_validation(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("must not be empty or whitespace")
        return v

class EmployeeOut(BaseModel):
    id: str
    name: str
    designation: str
    role: Role
    address: str

class EmployeeUpdate(BaseModel):
    name: str | None = None
    designation: str | None = None
    role: Role | None = None
    address: str | None = None






employee_db : Dict[str, EmployeeOut] = {}


#Services

def create_employee_service(payload: EmployeeCreate):
    employee_id = str(uuid4())
    employee = EmployeeOut(id=employee_id, **payload.dict())
    employee_db[employee_id] = employee

    return employee

def list_employees_service():
    return list(employee_db.values())


def remove_employee_service(employee_id: str):
    if employee_id not in employee_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    del employee_db[employee_id]



def update_employee_service(employee_id: str, payload: EmployeeUpdate):
    employee = employee_db.get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    update_employee_details = employee.dict() #this will convert the pydantic object into a dict

    for key, value in payload.dict(exclude_unset=True).items():
        update_employee_details[key] = value


    updated_employee_details =EmployeeOut(**update_employee_details)
    employee_db[employee_id]= updated_employee_details
    return updated_employee_details







#routes
@app.post("/employees", response_model=EmployeeOut, status_code=201) #201 created
async def create_employee_route(payload: EmployeeCreate):
    return create_employee_service(payload)


@app.get("/employees",response_model=list[EmployeeOut], status_code=200) # 200 ok
async def list_employees_route():
    return list_employees_service()

@app.delete("/employees/{employee_id}", response_model=dict, status_code=204) #204 no content
async def delete_employee_route(employee_id: str):
    remove_employee_service(employee_id)
    return {"message" : "Employee deleted successfully"}

@app.patch("/employee/{employee_id}", response_model=EmployeeOut, status_code=200)
async def update_employee_route(employee_id: str):
    return update_employee_service(employee_id)






