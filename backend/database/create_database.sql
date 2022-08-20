/*
Scripts for creating the database from scratch.
*/

CREATE TABLE ref_usertype
(
	id INTEGER PRIMARY KEY NOT NULL,
	type TEXT NOT NULL
)

CREATE TABLE user
(
	id TEXT PRIMARY KEY NOT NULL,
	username TEXT NOT NULL,
	user_password TEXT NOT NULL,
	active INT NOT NULL DEFAULT 0,
	time_created TEXT NOT NULL,
	time_updated TEXT NOT NULL,
	updated_by TEXT NOT NULL,
	type INTEGER NOT NULL,
	CONSTRAINT updtd_by_fk FOREIGN KEY (updated_by) REFERENCES user(id)
	CONSTRAINT typ_fk FOREIGN KEY (type) REFERENCES ref_usertype (id)
)

CREATE TABLE log_index
(
	id TEXT NOT NULL PRIMARY KEY,
	name TEXT NOT NULL,
	time_created TEXT NOT NULL,
	time_updated TEXT NOT NULL,
	updated_by TEXT NOT NULL,
    CONSTRAINT uptd_by_fk	FOREIGN KEY (updated_by) REFERENCES user (id)
)


CREATE TABLE field
(
	id TEXT NOT NULL PRIMARY KEY,
	log_id TEXT NOT NULL,
	name TEXT NOT NULL,
	payload TEXT NOT NULL,
	time_created TEXT NOT NULL,
	time_updated TEXT NOT NULL,
	updated_by TEXT NOT NULL,
	 CONSTRAINT uptd_by_fk	FOREIGN KEY (updated_by) REFERENCES user (id),
	 CONSTRAINT lg_id_fk	FOREIGN KEY (log_id) REFERENCES log_index (id)
)

CREATE TABLE log 
(
	id TEXT NOT NULL PRIMARY KEY,
	index_id TEXT NOT NULL,
	time_ingested TEXT NOT NULL, 
	source TEXT NOT NULL,
	CONSTRAINT indx_id_fk FOREIGN KEY (index_id) REFERENCES log_index (id)
)