import disnake
from disnake.ext import commands, tasks
import asyncio
from datetime import datetime
import random
import mach

bot = commands.Bot(command_prefix=".",help_command=None , intents=disnake.Intents.all(), test_guilds=[1207013223476498472])

target_channel_id = 1207169583166005288 # Замените на ID целевого канала

@bot.event
async def on_ready():
    await bot.change_presence(status=disnake.Status.idle)
    print(f'Бот {bot.user.name} готов к работе!')
    change_status.start()

@tasks.loop(seconds=10)
async def change_status():
    guild = bot.get_guild(1207013223476498472)  # Замените ID вашего сервера
    time = datetime.now().strftime('%H:%M')
    status = f'👥: {guild.member_count} | {time} МСК'
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=status))

@bot.event
async def on_member_join(member):
    # Отправляем эмбед с приветственным сообщением и разноцветной линией
    colors = [0x00ff00, 0x0000ff, 0xff0000, 0x9400d3, 0xffff00, 0xffa500, 0xffc0cb, 0x808080]
    color = random.choice(colors)
    embed = disnake.Embed(
        title="Добро пожаловать на сервер!",
        description=f"Привет, {member.mention}! Мы рады видеть тебя на нашем сервере.",
        color=color
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Присоединился {member.joined_at}")
    embed.add_field(name="Правила сервера", value="Пожалуйста, ознакомьтесь с правилами сервера.")
    channel = member.guild.system_channel
    if channel:
        await channel.send(embed=embed)

@bot.slash_command(description='Вам выпадет либо орёл либо решка.')
async def coin(ctx):
    result = random.choice(["Орел", "Решка"])
    await ctx.send(f"Выпало: {result}")
    
@bot.slash_command(description='Информация о командах бота.')
async def help(ctx):
    await ctx.send(f"```Привет! Я бездомный котик, которого пригласили сюда работать стражем! ```"
                   "```Вот мои основные команды: ```"
                   "```/экономика - Полный список команд экономики. ```"
                   "```/модерация - Полный список команд модераторов. ```"
                   "```/профиль - Посмотреть основную информацию о себе или другом участнике. ```"
                   "```/сервер - Информация о сервере. ```"
                   "```К сожалению мой код не дописан и некоторые команды могут не работать и работать, но неккоректно. Извините за неудобства! ```")

@bot.event
async def on_message(message):
    if message.author == bot.user:  # Проверяем, что сообщение отправлено ботом
        return
    if not isinstance(message, disnake.Message):
        return
    if message.type == disnake.MessageType.application_command:
        return
    if message.channel.id == target_channel_id and not message.content.startswith('/'):
        await message.delete()
        await message.send("Извините, но этот канал создан только для команд! Для общения используйте общий чат!", ephemeral=True)
    await bot.process_commands(message)

@bot.slash_command(description="Удаляет указанное количество сообщений")
async def clear(ctx, количество: int):
    if количество <= 0:
        await ctx.send("Количество сообщений должно быть больше нуля.", ephemeral=True)
        return
    messages = await ctx.channel.history(limit=количество).flatten()
    await ctx.channel.delete_messages(messages)
    await ctx.send(f"Успешно удалено {количество} сообщений.", ephemeral=True)

@bot.slash_command(description='Выключает бота.')
@commands.is_owner()
async def off(ctx):
    await ctx.send("Секунду, бот завершает все свои процессы...", ephemeral=True)
    await bot.close()

@bot.slash_command(description='Подать заявку на staff-а.')
async def staff(ctx: disnake.ApplicationCommandInteraction):
    # Ставим утилиту удалению
    await ctx.send(f"Я создал для вас канал с критериями и анкетой!", ephemeral=True)
    # Проверяем наличие категории
    category_id = 1218234548333187164  # ID категории, где будет создан канал
    category = disnake.utils.get(ctx.guild.categories, id=category_id)
    if category:
        # Создаем текстовый канал с ограниченным доступом
        overwrites = {
            ctx.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            ctx.author: disnake.PermissionOverwrite(read_messages=True),
            ctx.guild.get_role(1207017289816219668): disnake.PermissionOverwrite(read_messages=True),
            ctx.guild.get_role(1217434371087400961): disnake.PermissionOverwrite(read_messages=True),
            ctx.guild.default_role: disnake.PermissionOverwrite(read_messages=False)
        }
        channel = await category.create_text_channel(name=f"・💼・{ctx.author}", overwrites=overwrites)
        await channel.send(f"{ctx.author.mention}, вот анкета на саппорта!)\n"
                           "Критерии:\n"
                           "1. Возраст от 12 лет.\n"
                           "2. Уровень >=3. \n"
                           "3. Адекватность.\n"
                           "4. Коммуникабельность.\n"
                           "5. Стрессоустойчивость.\n"
                           "6. Знание наших правил и правил дискорда.\n"
                           "Анкета:\n"
                           "1. Ваше ФИО/Возраст\n"
                           "2. Вы имели когда то опыт в данной должности?\n"
                           "3. Знание наших правил и правил дискорда.\n"
                           "4. Когда Вы готовы пройти собеседование?\n"
                           "*Если на вашу заявку долго не отвечают пинганите роль @staff!*\n"
                           "***Для staff-а: Закрыть канал команда '/close'.***")

@bot.slash_command(description="Закрыть канал")
async def close(ctx: disnake.ApplicationCommandInteraction):
    allowed_roles = [1207017289816219668, 1217434371087400961]  # ID ролей, которым разрешено использовать команду
    member_roles = [role.id for role in ctx.author.roles]
    if ctx.channel.category_id == 1218234548333187164 and any(role in allowed_roles for role in member_roles):
        await ctx.channel.delete()
    else:
        await ctx.response.send_message("У вас нет прав для закрытия этого канала", ephemeral=True)

@bot.slash_command(description='Подать репорт.')
async def report(ctx: disnake.ApplicationCommandInteraction):
    # Ставим утилиту удалению
    await ctx.send(f"Я создал для вас канал с инструкцией!", ephemeral=True)
    # Проверяем наличие категории
    category_id = 1218234548333187164  # ID категории, где будет создан канал
    category = disnake.utils.get(ctx.guild.categories, id=category_id)
    if category:
        # Создаем текстовый канал с ограниченным доступом
        overwrites = {
            ctx.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            ctx.author: disnake.PermissionOverwrite(read_messages=True),
            ctx.guild.get_role(1207017289816219668): disnake.PermissionOverwrite(read_messages=True),
            ctx.guild.get_role(1217434371087400961): disnake.PermissionOverwrite(read_messages=True),
            ctx.guild.default_role: disnake.PermissionOverwrite(read_messages=False)
        }
        channel = await category.create_text_channel(name=f"・🔔・{ctx.author}", overwrites=overwrites)
        await channel.send(f"{ctx.author.mention}, вот анкета на подачу репорта)\n"
                           "Анкета:\n"
                           "1. Ник нарушителя (Если есть, если нет то указываете 'None').\n"
                           "2. Описание ситуации/вопроса.\n"
                           "3. Док-ва (Если репорт на нарушителя).\n"
                           "*Если на ваш репорт долго не отвечают пинганите роль @staff!*\n"
                           "***Для staff-а: Закрыть канал команда '/close'.***")

# Запустить бота
bot.run('token')