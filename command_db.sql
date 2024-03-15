CREATE TABLE public.admins (
    user_id bigint,
    notif boolean DEFAULT FALSE
);

CREATE TABLE public.payment (
    id serial PRIMARY KEY,
    user_id bigint,
    receive integer,
    waiting boolean DEFAULT TRUE, 
    success boolean DEFAULT FALSE,
    code varchar(50),
    date timestamp without time zone
);

CREATE TABLE public.users (
    id serial PRIMARY KEY,
    user_id bigint,
    username VARCHAR(255),
    key_balance interger DEFAULT 0,
    balance integer DEFAULT 0
);

CREATE TABLE public.buy (
    id serial PRIMARY KEY,
    user_id bigint,
    amount integer,
    name VARCHAR(255),
    count integer,
    date timestamp without time zone
);
