GET_USER = """
    select id, tg_id, username, last_name, first_name, phone 
    from users
    where tg_id = :tg_id;
"""

SAVE_USER = """
    insert into users(tg_id, first_name, last_name, username)
    values(:tg_id, :first_name, :last_name, :username);
"""

UPDATE_USER = """
    update users
    set
        first_name = :first_name,
        last_name = :last_name,
        username = :username,
        phone = :phone
    where tg_id = :tg_id;
"""

SAVE_RECORD = """
insert into records(user_id, record_date, record_time)
    values
        (:user_id, :record_date, :record_time)
"""

GET_RECORDS_BY_USER_ID = """
select id, user_id, record_date, record_time, created_at, updated_at 
from records
where user_id=:user_id and created_at between :start_date and :end_date
order by created_at;
"""

GET_RECORDS_WITH_USER = """
select r.id, r.user_id,
    u.username, u.phone,
    u.last_name, u.first_name,
    r.record_date, r.record_time,
    r.created_at, r.updated_at 
from records r 
    left join users u 
    on r.user_id = u.tg_id
where r.user_id=:user_id and r.created_at between :start_date and :end_date
order by created_at;
"""

GET_RECORDS = """
select
    r.id, r.user_id, u.username,
    u.last_name, u.first_name, u.phone,
    r.record_date, r.record_time, r.created_at,
    r.updated_at
from records r
left join users u
on r.user_id = u.tg_id
order by r.record_date;
"""

UPDATE_RECORD_DATE = """
update records
set 
    record_date = :record_date,
    updated_at = :updated_at
where
    id = :id
"""

UPDATE_RECORD_TIME = """
update records
set 
    record_time = :record_time,
    updated_at = :updated_at
where
    id = :id
"""

GET_RECORD_EVENT = """
select id, record_id, event from record_event
where record_id = :record_id;
"""

SAVE_RECORD_EVENT = """
insert into record_event(record_id, event)
values (:record_id, :event);
"""

UPDATE_RECORD_EVENT = """
update record_event
    set event = :event
where record_id = :record_id;  
"""