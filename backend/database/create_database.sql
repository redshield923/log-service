CREATE TABLE "ref_usertype" (
	"id"	INTEGER,
	"type"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

insert into ref_usertype (type) VALUES ('user')
insert into ref_usertype (type) VALUES ('admin')

insert into ref_usertype (type) VALUES ('superadmin')


CREATE TABLE "user" (
	"id"	INTEGER,
	"username"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	"active"	INT NOT NULL DEFAULT 0,
	"time_created"	TEXT NOT NULL,
	"time_updated"	TEXT NOT NULL,
	"updated_by"	int NOT NULL,
	"type"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	CONSTRAINT "typ_fk" FOREIGN KEY("type") REFERENCES "ref_usertype"("id"),
	CONSTRAINT "updtd_by_fk" FOREIGN KEY("updated_by") REFERENCES "user"("id")
);

CREATE TABLE "log_index" (
	"name"	TEXT,
	"time_created"	TEXT NOT NULL,
	"time_updated"	TEXT NOT NULL,
	"updated_by"	int NOT NULL,
	PRIMARY KEY("name"),
	CONSTRAINT "uptd_by_fk" FOREIGN KEY("updated_by") REFERENCES "user"("id")
);

CREATE TABLE "log" (
	"id"	INTEGER,
	"index_name"	text NOT NULL,
	"time_ingested"	TEXT NOT NULL,
	"source"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	CONSTRAINT "indx_id_fk" FOREIGN KEY("index_name") REFERENCES "log_index"("name")
);

CREATE TABLE "field" (
	"id"	INTEGER,
	"log_id"	int NOT NULL,
	"name"	TEXT NOT NULL,
	"payload"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	CONSTRAINT "lg_id_fk" FOREIGN KEY("log_id") REFERENCES "log"("id")
);

insert into user (id, username, password, active, time_created, time_updated, updated_by, type) values
 (1,'benjamin', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 1, julianday('now'), julianday('now'), 1, 2)