from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from uuid import uuid4

app = FastAPI()

#schemas
class NotesCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class NoteOut(BaseModel):
    id: str
    title: str
    content: str


#-----Fake DB ------
'''
the fake database is a dictionary, the keys are str and values are NoteOut objects ->> i expect this to map a string ID
to a NoteOut model. ={} -> This actually creates a dictionary'''

notes_db: Dict[str, NoteOut] = {}

#--- Routes

@app.post("/notes", response_model=NoteOut, status_code=201)
def create_notes(payload: NotesCreate):
    note_id = str(uuid4())
    note = NoteOut(id=note_id, **payload.dict())
    notes_db[note_id] = note
    return note



@app.get("/notes",response_model=list[NoteOut])
def list_notes():
    return list(notes_db.values())


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_notes(note_id:str):
    note = notes_db.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id:str, payload:NoteUpdate):
    note = notes_db.get(note_id)
    #note= NoteOut(id="abc123", title="A", content="B") - a pydantic model
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data= note.dict() #convert the existing object into dict, because Pydantic model not meant to be mutated directly
    '''
    updated_data = note.dict()
    updated_data = {
    "id":"abc123",
    "title": "A",
    "content: "B" }
    '''

    for key, value in payload.dict(exclude_unset=True).items(): #exclude_unset= True ensures that fields which are not sent are excluded.
        update_data[key] = value

    updated_note = NoteOut(**update_data)
    notes_db[note_id] = updated_note
    return updated_note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str):
    if note_id not in notes_db:
        raise HTTPException(status_code=404, detail="Note not found")


    del notes_db[note_id]


