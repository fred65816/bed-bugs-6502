create table declarations (
    declaration_num integer primary key,
    declaration_date text not null,
    inspection_date text,
    extermination_num integer,
    treatment_start_date text,
    treatment_end_date text,
    neighborhood_id integer not null,
    x_coord real,
    y_coord real,
    longitude real,
    latitude real,
    is_visible integer,
    foreign key(neighborhood_id) references neighborhoods(id)
);

create table declarations_extra (
    declaration_num integer primary key,
    address varchar(100) not null,
    first_name varchar(50) not null,
    last_name varchar(50) not null,
    description varchar(200)
);

create table neighborhoods (
    id integer primary key,
    name varchar(100),
    neighborhood_code varchar(3),
    district_id integer,
    foreign key(district_id) references districts(id)
);

create table districts (
    id integer primary key,
    name varchar(100)
);

create table profiles (
    id integer primary key,
    first_name varchar(50) not null,
    last_name varchar(50) not null,
    email varchar(50) not null unique,
    salt varchar(32) not null,
    hash varchar(128) not null,
    picture blob
);

create table profiles_neighborhoods (
    profile_id integer not null,
    neighborhood_id integer not null,
    primary key(profile_id, neighborhood_id),
    foreign key(profile_id) references profiles(id),
    foreign key(neighborhood_id) references neighborhoods(id)
);
