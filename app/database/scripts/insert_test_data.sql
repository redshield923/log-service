-- SELECT * FROM user

INSERT INTO ref_usertype (type) VALUES ('user')
INSERT INTO ref_usertype (type) VALUES ('admin')
INSERT INTO ref_usertype (type) VALUES ('superadmin')
INSERT INTO user (id, username, password, active, time_created, time_updated, updated_by, type) VALUES (1,'testadmin', '$argon2id$v=19$m=65536,t=3,p=4$lGQxm45YoJiMzopOT61bkA$tYVNFK/TJ0Mm7qFEeSAnGXCEM9Q7gRl/yE+pfN9JoQk', 1, julianday('now'), julianday('now'), 1, 2)
INSERT INTO user (id, username, password, active, time_created, time_updated, updated_by, type) VALUES (2,'testuser', '$argon2id$v=19$m=65536,t=3,p=4$lGQxm45YoJiMzopOT61bkA$tYVNFK/TJ0Mm7qFEeSAnGXCEM9Q7gRl/yE+pfN9JoQk', 1, julianday('now'), julianday('now'), 1, 1)