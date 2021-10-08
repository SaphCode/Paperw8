DROP TABLE IF EXISTS historical_performance;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS related;

-- We start by creating a regular SQL table
-- Symbol we say for now 7 characters.
-- Currency is ISO 3 characters: http://currencysystem.com/codes/
CREATE TABLE historical_performance (
  date        DATE              NOT NULL,
  name        VARCHAR(30)       NOT NULL,
  cum_return  FLOAT				NOT NULL,
  PRIMARY KEY (date, name)
);

CREATE TABLE user (
  id 		  	INTEGER 		PRIMARY KEY AUTOINCREMENT,
  username    	VARCHAR(20) 	UNIQUE NOT NULL,
  display_name	VARCHAR(50)		NOT NULL,
  password 	  	TEXT 			NOT NULL
);

-- A post has an author, date, content (markdown), 
CREATE TABLE post (
  id 		  INTEGER 			PRIMARY KEY AUTOINCREMENT,
  author_id	  INTEGER			NOT NULL,
  created	  TIMESTAMP			NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title		  VARCHAR(100)			NOT NULL UNIQUE,
  title_img_parent_dir TEXT		NOT NULL,
  title_img   TEXT				NOT NULL,
  content	  TEXT				NOT NULL,
  last_edit	  TIMESTAMP			NOT NULL,
  category	  VARCHAR(50)			NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user(id)
);

-- Looks like it is one way, but it can be both ways of course, if
-- you use the second column too
CREATE TABLE related (
  id		  INTEGER			NOT NULL,
  related_to_id	  INTEGER			NOT NULL,
  FOREIGN KEY(related_to_id) REFERENCES post(id),
  FOREIGN KEY(id) REFERENCES post(id)
);