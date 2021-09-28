DROP TABLE IF EXISTS historical_performance;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

-- We start by creating a regular SQL table
-- Symbol we say for now 7 characters.
-- Currency is ISO 3 characters: http://currencysystem.com/codes/
CREATE TABLE historical_performance (
  date        DATE              NOT NULL,
  symbol      VARCHAR(8)        NOT NULL,
  cum_return  FLOAT				NOT NULL,
  PRIMARY KEY (date, symbol)
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
  title		  VARCHAR(100)		NOT NULL UNIQUE,
  content	  TEXT				NOT NULL,
  last_edit	  TIMESTAMP			NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user(id)
);