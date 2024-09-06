CREATE TABLE `queries` (
  `domain_name` varchar(126) NOT NULL,
  `source` varchar(126) NOT NULL,
  `count` int(11) NOT NULL DEFAULT 1,
  `last` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
);
ALTER TABLE `queries`
  ADD PRIMARY KEY (`domain_name`,`source`);
COMMIT;
