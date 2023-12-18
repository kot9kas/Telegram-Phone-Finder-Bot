import aiosqlite

async def create_table():
    async with aiosqlite.connect("telephones.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS telephones (
                            model TEXT,
                            storage TEXT,
                            color TEXT,
                            price INTEGER,
                            country TEXT)""")
        await db.commit()

async def add_telephone(model, storage, color, price, country):
    async with aiosqlite.connect("telephones.db") as db:
        await db.execute("INSERT INTO telephones (model, storage, color, price, country) VALUES (?, ?, ?, ?, ?)",
                         (model, storage, color, price, country))
        await db.commit()

async def get_telephone_by_details(model, storage, color, country):
    async with aiosqlite.connect("telephones.db") as db:
        query = "SELECT * FROM telephones WHERE model = ? AND color = ?"
        params = [model, color]
        if storage:
            query += " AND storage = ?"
            params.append(storage)
        if country:
            query += " AND country = ?"
            params.append(country)
        query += " ORDER BY price ASC LIMIT 3"
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()
async def get_all_telephones():
    async with aiosqlite.connect("telephones.db") as db:
        async with db.execute("SELECT * FROM telephones ORDER BY model ASC, price ASC") as cursor:
            return await cursor.fetchall()
async def delete_telephone(model, storage):
    async with aiosqlite.connect("telephones.db") as db:
        await db.execute("DELETE FROM telephones WHERE model = ? AND storage = ?", (model, storage))
        await db.commit()