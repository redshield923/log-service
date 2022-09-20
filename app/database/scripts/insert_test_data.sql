-- SELECT * FROM user

INSERT INTO ref_usertype (type) VALUES ('user')
INSERT INTO ref_usertype (type) VALUES ('admin')
INSERT INTO ref_usertype (type) VALUES ('superadmin')
INSERT INTO user (id, username, password, active, time_created, time_updated, updated_by, type) VALUES (1,'testadmin', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 1, julianday('now'), julianday('now'), 1, 2)
INSERT INTO user (id, username, password, active, time_created, time_updated, updated_by, type) VALUES (2,'testuser', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 1, julianday('now'), julianday('now'), 1, 1)