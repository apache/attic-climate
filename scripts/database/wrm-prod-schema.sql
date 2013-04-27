-- MySQL dump 10.11
--
-- Host: localhost    Database: wrm_prod
-- ------------------------------------------------------
-- Server version	5.0.77

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dataset`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `dataset` (
  `dataset_id` int(10) unsigned NOT NULL auto_increment,
  `longName` varchar(120) default NULL,
  `shortName` varchar(60) default NULL,
  `description` text,
  `source` varchar(255) default NULL,
  `referenceURL` varchar(255) default NULL,
  PRIMARY KEY  (`dataset_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `parameter`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `parameter` (
  `parameter_id` int(10) unsigned NOT NULL auto_increment,
  `longName` varchar(120) default NULL,
  `shortName` varchar(60) default NULL,
  `description` text,
  `referenceURL` varchar(255) default NULL,
  `cellMethod` text,
  `timestep` varchar(60) default NULL,
  `start_date` date default NULL,
  `end_date` date default NULL,
  `nx` int default NULL,
  `ny` int default NULL,
  `lon_res` float default NULL,
  `lat_res` float default NULL,
  `missingDataFlag` float default NULL,
  `units` varchar(60) default NULL,
  `verticalUnits` varchar(120) default NULL,
  `database` varchar(80) NOT NULL,
  `dataset_id` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`parameter_id`)
) ENGINE=MyISAM AUTO_INCREMENT=41 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2011-06-05  4:05:33
