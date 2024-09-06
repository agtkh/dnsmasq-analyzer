CREATE TABLE `titles` (
  `url` varchar(255) NOT NULL,
  `title` varchar(255) DEFAULT NULL
);
ALTER TABLE `titles`
  ADD PRIMARY KEY (`url`);
COMMIT;
