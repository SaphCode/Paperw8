DROP TABLE IF EXISTS historical_performance;

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
  id 		  SERIAL 		PRIMARY KEY,
  username    VARCHAR(50) 	UNIQUE NOT NULL,
  password 	  TEXT 			NOT NULL
);


-- A post has an author, date, content (markdown), 
CREATE TABLE post {
  id		  SERIAL PRIMARY KEY,
  author_id	  INTEGER			NOT NULL,
  created	  TIMESTAMP			NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title		  VARCHAR(100)		NOT NULL,
  content	  TEXT				NOT NULL,
  last_edit	  DATE				NULL,
  FOREIGN KEY (author_id) REFERENCES user(id)
};