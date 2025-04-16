create if not exists schema library;  
use library; 

create table users(
    id int auto_increment primary key,
    name varchar(100) not null,
    email varchar(100) not null,
    password varchar(256) not null,
    genre enum('Man', 'Woman', 'Other') not null,
    role enum('President', 'Staff', 'Client') not null,
    created_at datetime
);

create table books(
    id int auto_increment primary key,
    title varchar(100) not null,
    author varchar(100) not null,
    genre varchar(100) not null,
    publisher varchar(100) not null,
    publication_date date not null,
    language enum('English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese') not null,
    description text not null,
    keywords text not null,
    position varchar(50) not null,
    copy int not null,
    note text not null,    
    created_at date not null
);

create table courses(
    id int auto_increment primary key,
    name varchar(100) not null,
    subtitle varchar(100) not null,
    description text not null,
    teacher varchar(100) not null,
    language enum('English', 'Spanish', 'French', 'German', 'Italian') not null,
    level enum('Beginner', 'Intermediate', 'Advanced') not null,
    period text not null,
    place varchar(100) not null,
    price decimal(10,2) not null,
    seats int not null
);

create table loans(
    id int auto_increment primary key,  
    start date not null,
    end date,
    status enum("Pending confirmation", "Confirmed", "Soon to expire", "Expired", "Extended", "Terminated") not null,
    book_id int not null,
    user_id int not null,
    foreign key (user_id) references users(id),
    foreign key (book_id) references books(id)
);

create table bookings(
    id int auto_increment primary key,
    created_at date not null,   
    status enum("Reservation pending", "Payment requested", "Payment received", "Reservation confirmed", "Reservation cancelled") not null,
    course_id int not null,
    user_id int not null,
    foreign key (course_id) references courses(id),
    foreign key (user_id) references users(id)
);

create table messages(
    id int auto_increment primary key,
    name varchar(50) not null,
    message text not null,
    created_at datetime,
);

create table questions(
    id int auto_increment primary key,
    data text not null,
    question text not null,
    created_at datetime,
    user_id int not null,
    foreign key (user_id) references users(id)
); 

create table answers(
    id int auto_increment primary key,
    object text not null,
    body text not null,
    created_at datetime,
    user_id int not null,
    question_id int not null,
    foreign key (user_id) references users(id),
    foreign key (question_id) references questions(id)  
);