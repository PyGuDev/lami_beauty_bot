create table if not exists users(
    id serial primary key,
    tg_id integer not null unique,
    first_name varchar(65) null,
    last_name varchar(65) null,
    username varchar(100) null unique,
    phone varchar(11) null unique
);

create table if not exists records(
    id serial primary key,
    user_id integer,
    record_date date,
    record_time time null,
    created_at date default current_date,
    updated_at date null,
    foreign key (user_id) references users(tg_id)
);

create table if not exists user_event(
    id serial primary key,
    record_id integer,
    event varchar(100) check (event in ('add_date', 'add_time', 'add_phone')),
    foreign key (record_id) references records(id)
)