import aiosqlite


class DataBase:
    def __init__(self, db_name='data/mydatabase.db'):
        self.db_name = db_name

    async def create_table(self):
        """создаем таблицу если еще не существует"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, website_id INTEGER,'
                             'user_type INTEGER, registered INTEGER)')
            await db.commit()

    async def check_user(self, user_id):
        """проверяем наличие пользователя в базе данных по его id"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT user_type FROM users WHERE id = ?', (user_id,)) as cursor:
                user_exist = await cursor.fetchone()
        return user_exist

    async def add_user(self, user_id, status):
        """создаем запись о пользователе с его типом (0 или 1) где 0 это заказчик, а 1 - строитель"""
        user_exist = await self.check_user(user_id)
        async with aiosqlite.connect(self.db_name) as db:
            if not user_exist:
                await db.execute('INSERT INTO users (id, website_id, user_type, registered) VALUES (?, 0, ?, 0)'
                                 ,(user_id, status))
                await db.commit()

    async def get_user_status(self, user_id):
        """получаем тип пользователя через его id"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT user_type FROM users WHERE id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                return None

    async def user_registered(self, user_id):
        """возвращаем статус регистрации пользователя"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT registered FROM users WHERE id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                return None

    async def update_registered_state(self, user_id, user_reg_state):
        """обновляем статус регистрации пользователя"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('UPDATE users SET registered = ? WHERE id = ?', (user_reg_state, user_id)):
                pass
            await db.commit()

    async def update_user_type(self, user_type, user_id):
        """обновляем статус пользователя"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('UPDATE users SET user_type = ? WHERE id = ?', (user_type, user_id)):
                pass
            await db.commit()

    async def update_website_id(self, user_id, website_id):
        """обновляем website_id пользователя на реальный, полученный с api"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('UPDATE users SET website_id = ? WHERE id = ?', (website_id, user_id)):
                pass
            await db.commit()

    async def get_website_id(self, user_id):
        """получаем id пользователя с вебсайта из бд по user_id"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT website_id FROM users WHERE id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                return None
