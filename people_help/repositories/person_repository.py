from sqlalchemy.ext.asyncio import AsyncSession
from ..models.person import Person
from ..repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    def __init__(self, session: AsyncSession):
        super().__init__(Person, session)
    
    async def create_person(self, **kwargs) -> Person:
        return await self.create(**kwargs)