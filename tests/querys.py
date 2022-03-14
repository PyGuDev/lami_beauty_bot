INSERT_USER = """
insert into users(tg_id, username, last_name, first_name) 
values(%(tg_id)s, %(username)s, %(last_name)s, %(first_name)s)
"""

INSERT_RECORD = """
insert into records(user_id, record_date, record_time)
values(%(user_id)s, %(record_date)s, %(record_time)s)
"""