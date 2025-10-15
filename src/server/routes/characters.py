from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.server.db import characters_collection
from src.server.models import Character

router = APIRouter(prefix="/api/v1/characters", tags=["Characters"])

# ------------------ CRUD ENDPOINTS ------------------


@router.get("", response_model=List[Character])
async def get_all_characters():
    """Retrieve all characters"""
    chars = await characters_collection.find().to_list(length=None)
    return chars


@router.get("/{char_id}", response_model=Character)
async def get_character(char_id: str):
    """Retrieve one character by ID"""
    char = await characters_collection.find_one({"_id": char_id})
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char


@router.post("", status_code=201)
async def create_character(char_id: str, character: Character):
    """Create a new character"""
    existing = await characters_collection.find_one({"_id": char_id})
    if existing:
        raise HTTPException(status_code=400, detail="Character already exists")
    await characters_collection.insert_one({"_id": char_id, **character.model_dump()})
    return JSONResponse(content={"message": f"✅ Created {character.name}"}, status_code=201)


@router.put("/{char_id}")
async def replace_character(char_id: str, character: Character):
    """Replace entire character document"""
    result = await characters_collection.replace_one(
        {"_id": char_id}, {"_id": char_id, **character.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    return {"message": f"Replaced {char_id}"}


@router.delete("/{char_id}")
async def delete_character(char_id: str):
    """Delete a character"""
    result = await characters_collection.delete_one({"_id": char_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    return {"message": f"Deleted {char_id}"}
