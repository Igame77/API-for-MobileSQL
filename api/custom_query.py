from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table
import re
from pydantic import BaseModel


class CustomQueryManager:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine = engine
        self.router = router
        self.tags = ['Custom Queries']

    def _validate_sql(self, query: str) -> bool:
        """Проверяет безопасность SQL-запроса"""
        # Разрешаем только SELECT запросы для безопасности
        query_upper = query.strip().upper()

        # Запрещенные операции
        dangerous_patterns = [
            r'\bDROP\b',
            r'\bDELETE\b',
            r'\bUPDATE\b',
            r'\bINSERT\b',
            r'\bALTER\b',
            r'\bTRUNCATE\b',
            r'\bEXEC\b',
            r'\bEXECUTE\b',
            r'\bCREATE\b',
            r'--',
            r';',
            r'/\*',
            r'\*/'
        ]

        # Проверяем, что это SELECT запрос
        if not query_upper.startswith('SELECT'):
            return False

        # Проверяем на опасные паттерны
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return False

        return True

    def setup(self):

        class QueryRequest(BaseModel):
            query: str
            limit: int = 100
            isImage: bool = False

        @self.router.post('/custom/query', tags=self.tags)
        async def execute_custom_query(request: QueryRequest):
            """
            Выполняет кастомный SQL запрос (только SELECT)

            Args:
                query: SQL запрос (только SELECT)
                limit: Максимальное количество возвращаемых строк
                isImage: Возвращать ли результат как изображение
            """
            query = request.query
            limit = request.limit
            isImage = request.isImage

            # Валидация запроса
            if not self._validate_sql(query):
                raise HTTPException(
                    status_code=400,
                    detail="Недопустимый SQL запрос. Разрешены только SELECT запросы без опасных операций."
                )

            # Добавляем LIMIT если его нет
            if 'LIMIT' not in query.upper():
                query = f"{query.rstrip(';')} LIMIT {limit}"

            try:
                async with self.async_engine.connect() as conn:
                    result = await conn.execute(text(query))

                    if isImage:
                        res = result.fetchall()
                        return  get_image_from_table(res, isImage)
                    else:
                        rows = result.fetchall()

                        # Преобразуем в список словарей для удобства
                        columns = result.keys()
                        data = []
                        for row in rows:
                            data.append(dict(zip(columns, row)))

                        return {
                            "success": True,
                            "columns": list(columns),
                            "data": data,
                            "row_count": len(data)
                        }

            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ошибка выполнения запроса: {str(e)}"
                )

        @self.router.get('/custom/tables', tags=self.tags)
        async def get_all_tables():
            """Возвращает список всех таблиц в базе данных"""
            async with self.async_engine.connect() as conn:
                result = await conn.execute(
                    text("SHOW TABLES")
                )
                tables = [row[0] for row in result.fetchall()]
                return {"tables": tables}

        @self.router.get('/custom/table/{table_name}/schema', tags=self.tags)
        async def get_table_schema(table_name: str):
            """Возвращает схему таблицы"""
            async with self.async_engine.connect() as conn:
                result = await conn.execute(
                    text(f"DESCRIBE `{table_name}`")
                )
                schema = []
                for row in result:
                    schema.append({
                        "field": row[0],
                        "type": row[1],
                        "null": row[2],
                        "key": row[3],
                        "default": row[4],
                        "extra": row[5]
                    })
                return {"table": table_name, "schema": schema}