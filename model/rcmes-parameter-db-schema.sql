-- Water Resources Management 
-- Climate Model Evaluation Database Schema
-- 
-- 7/28/2010
--
-- Authors: ahart, cgoodale
-- 
-- Database: `wrm_data`
-- Generation Time: Jul 12, 2010 at 10:08 AM
-- Server version: 5.1.44
-- PHP Version: 5.3.2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- Database: `wrm_dev`
--
-- --------------------------------------------------------

--
-- Table structure for table `dataPoint`
--

CREATE TABLE `dataPoint` (
  `datapoint_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `granule_id` int(10) unsigned NOT NULL,
  `dataset_id` int(10) unsigned NOT NULL,
  `parameter_id` int(10) unsigned NOT NULL,
  `time` datetime DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `vertical` double DEFAULT NULL,
  `value` double DEFAULT NULL,
  PRIMARY KEY (`datapoint_id`),
  INDEX ( `parameter_id` , `time` , `latitude` , `longitude` )
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `dataset`
--

CREATE TABLE `dataset` (
  `dataset_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `longName` varchar(120) DEFAULT NULL,
  `shortName` varchar(60) DEFAULT NULL,
  `description` text,
  `source` varchar(255) DEFAULT NULL,
  `referenceURL` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`dataset_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- Table structure for table `dpMap`
--

CREATE TABLE `dpMap` (
  `dataset_id` int(10) unsigned NOT NULL,
  `parameter_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`dataset_id`,`parameter_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `granule`
--

CREATE TABLE `granule` (
  `granule_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `dataset_id` int(10) unsigned DEFAULT NULL,
  `filename` varchar(255) NOT NULL,
  PRIMARY KEY (`granule_id`),
  KEY `dataset_id` (`dataset_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- Table structure for table `parameter`
--

CREATE TABLE `parameter` (
  `parameter_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `dataset_id` int(10) unsigned NOT NULL,
  `longName` varchar(120) DEFAULT NULL,
  `shortName` varchar(60) DEFAULT NULL,
  `description` text,
  `referenceURL` varchar(255) DEFAULT NULL,
  `cellMethod` text,
  `missingDataFlag` float DEFAULT NULL,
  `units` varchar(60) DEFAULT NULL,
  `verticalUnits` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`parameter_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
