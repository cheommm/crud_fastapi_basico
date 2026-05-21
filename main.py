import os
from typing import AsyncGenerator, List, Optional
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, SQLModel, create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DATABASE_URL = f"mysql+aiomysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

app = FastAPI(title="Control de Inventario de Joyería - SQLModel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JewelryItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    categoria: str
    material: str
    precio: float
    stock: int


class JewelryItemUpdate(SQLModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    material: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@app.post("/joyas/", response_model=JewelryItem, status_code=status.HTTP_201_CREATED)
async def create_joya(joya: JewelryItem, session: AsyncSession = Depends(get_session)) -> JewelryItem:
    session.add(joya)
    await session.commit()
    await session.refresh(joya)
    return joya


@app.get("/joyas/", response_model=List[JewelryItem])
async def list_joyas(session: AsyncSession = Depends(get_session)) -> List[JewelryItem]:
    result = await session.execute(select(JewelryItem))
    return result.scalars().all()


@app.get("/joyas/{joya_id}", response_model=JewelryItem)
async def get_joya(joya_id: int, session: AsyncSession = Depends(get_session)) -> JewelryItem:
    result = await session.execute(select(JewelryItem).where(JewelryItem.id == joya_id))
    joya = result.scalar_one_or_none()
    if joya is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Joya no encontrada")
    return joya


@app.put("/joyas/{joya_id}", response_model=JewelryItem)
async def update_joya(joya_id: int, joya_update: JewelryItemUpdate, session: AsyncSession = Depends(get_session)) -> JewelryItem:
    result = await session.execute(select(JewelryItem).where(JewelryItem.id == joya_id))
    joya = result.scalar_one_or_none()
    if joya is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Joya no encontrada")

    update_data = joya_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(joya, key, value)

    session.add(joya)
    await session.commit()
    await session.refresh(joya)
    return joya


@app.delete("/joyas/{joya_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_joya(joya_id: int, session: AsyncSession = Depends(get_session)) -> None:
    result = await session.execute(select(JewelryItem).where(JewelryItem.id == joya_id))
    joya = result.scalar_one_or_none()
    if joya is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Joya no encontrada")

    await session.delete(joya)
    await session.commit()
