CREATE DATABASE  IF NOT EXISTS `수강` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `수강`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: 수강
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course` (
  `course_id` varchar(20) NOT NULL,
  `course_name` varchar(50) NOT NULL,
  `credit` tinyint NOT NULL,
  `min_grade` tinyint NOT NULL,
  `staff_id` varchar(20) NOT NULL,
  PRIMARY KEY (`course_id`),
  KEY `staff_id` (`staff_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course`
--

LOCK TABLES `course` WRITE;
/*!40000 ALTER TABLE `course` DISABLE KEYS */;
INSERT INTO `course` VALUES ('AI101','직업미래와 문제해결',2,1,'S001'),('AI102','전공기초영어2',2,1,'S001'),('AI103','파이썬 응용 프로그래밍',3,1,'S001'),('AI104','C언어',3,1,'S001'),('AI105','마이컴응용',3,1,'S001'),('AI106','인공지능 문제해결 프로젝트',3,1,'S001'),('FET101','커뮤니케이션능력',2,1,'S001');
/*!40000 ALTER TABLE `course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `dept_id` varchar(10) NOT NULL,
  `dept_name` varchar(30) NOT NULL,
  PRIMARY KEY (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES ('AI','AI시스템과'),('ET','전자통신과'),('ETA','전자통신AI공학과'),('FET','융합전자통신과'),('IOT','사물인터넷공학과'),('SW','응용SW학부');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lecture`
--

DROP TABLE IF EXISTS `lecture`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lecture` (
  `lecture_id` varchar(20) NOT NULL,
  `day_of_week` enum('월','화','수','목','금','토') NOT NULL,
  `start_period` tinyint NOT NULL,
  `end_period` tinyint NOT NULL,
  `program_type` enum('전문학사','전공심화','P-TECH') NOT NULL,
  `room_id` varchar(20) NOT NULL,
  `course_id` varchar(20) NOT NULL,
  `prof_id` varchar(20) NOT NULL,
  PRIMARY KEY (`lecture_id`),
  KEY `room_id` (`room_id`),
  KEY `course_id` (`course_id`),
  KEY `prof_id` (`prof_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecture`
--

LOCK TABLES `lecture` WRITE;
/*!40000 ALTER TABLE `lecture` DISABLE KEYS */;
INSERT INTO `lecture` VALUES ('AI101_01','월',1,2,'전문학사','D0416','AI101','P005'),('AI102_01','월',3,4,'전문학사','D0416','AI102','P001'),('AI102_02','월',8,9,'전문학사','D0416','AI102','P001'),('AI103_01','월',6,8,'전문학사','D0301','AI103','P009'),('AI103_02','월',2,4,'전문학사','D0301','AI103','P009'),('AI104_01','화',2,4,'전문학사','D0302','AI104','P003'),('AI104_02','화',6,8,'전문학사','D0302','AI104','P003'),('AI105_01','화',6,8,'전문학사','D0317','AI105','P008'),('AI105_02','화',2,4,'전문학사','D0317','AI105','P008'),('AI106_01','목',2,4,'전문학사','D0317','AI106','P007'),('AI106_02','목',6,8,'전문학사','D0317','AI106','P007'),('FET101_01','토',1,2,'P-TECH','D0416','FET101','P001'),('FET101_02','토',1,2,'P-TECH','D0420','FET101','P003');
/*!40000 ALTER TABLE `lecture` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professor`
--

DROP TABLE IF EXISTS `professor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `professor` (
  `prof_id` varchar(20) NOT NULL,
  `name` varchar(30) NOT NULL,
  `dept_id` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`prof_id`),
  KEY `dept_id` (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professor`
--

LOCK TABLES `professor` WRITE;
/*!40000 ALTER TABLE `professor` DISABLE KEYS */;
INSERT INTO `professor` VALUES ('P001','김재연','AI'),('P002','신익조','AI'),('P003','김영선','AI'),('P004','한종훈','AI'),('P005','김재목','AI'),('P006','김영포','ET'),('P007','강성인','AI'),('P008','서상현','AI'),('P009','김덕령','AI'),('P010','한영식','AI'),('P011','송재진','ET'),('P012','김은원','ET'),('P013','정호일','SW'),('P014','김지예','SW'),('P015','이영걸','SW');
/*!40000 ALTER TABLE `professor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration`
--

DROP TABLE IF EXISTS `registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration` (
  `student_id` varchar(20) NOT NULL,
  `lecture_id` varchar(20) NOT NULL,
  PRIMARY KEY (`student_id`,`lecture_id`),
  KEY `lecture_id` (`lecture_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration`
--

LOCK TABLES `registration` WRITE;
/*!40000 ALTER TABLE `registration` DISABLE KEYS */;
INSERT INTO `registration` VALUES ('20240B208','AI104_02');
/*!40000 ALTER TABLE `registration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room`
--

DROP TABLE IF EXISTS `room`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room` (
  `room_id` varchar(20) NOT NULL,
  `room_name` varchar(50) NOT NULL,
  `building` varchar(50) NOT NULL,
  PRIMARY KEY (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room`
--

LOCK TABLES `room` WRITE;
/*!40000 ALTER TABLE `room` DISABLE KEYS */;
INSERT INTO `room` VALUES ('D0301','IoT창의적 종합 설계실','정보통신관'),('D0302','IoT기기운용실습실','정보통신관'),('D0317','기초회로실험실','정보통신관'),('D0401','통신응용실험실','정보통신관'),('D0402','EDA실험실','정보통신관'),('D0416','창의융합강의실1','정보통신관'),('D0417','안테나실험실','정보통신관'),('D0420','창의융합강의실2','정보통신관'),('J0407','프로그래밍2실습실','전산관');
/*!40000 ALTER TABLE `room` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff`
--

DROP TABLE IF EXISTS `staff`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff` (
  `staff_id` varchar(20) NOT NULL,
  `name` varchar(30) NOT NULL,
  PRIMARY KEY (`staff_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff`
--

LOCK TABLES `staff` WRITE;
/*!40000 ALTER TABLE `staff` DISABLE KEYS */;
INSERT INTO `staff` VALUES ('S001','김교무'),('S002','박학사');
/*!40000 ALTER TABLE `staff` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `student_id` varchar(20) NOT NULL,
  `name` varchar(30) NOT NULL,
  `grade` tinyint NOT NULL,
  `program_type` enum('전문학사','전공심화','P-TECH') NOT NULL,
  `dept_id` varchar(10) NOT NULL,
  PRIMARY KEY (`student_id`),
  KEY `dept_id` (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES ('20230B136','김주화',2,'전문학사','AI'),('20240B208','김진규',2,'전문학사','AI'),('20240B218','서지수',3,'전공심화','AI'),('20240B229','박재희',4,'전공심화','AI');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `login_id` varchar(30) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('student','professor','staff') NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `staff_id` varchar(20) DEFAULT NULL,
  `prof_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `login_id` (`login_id`),
  KEY `student_id` (`student_id`),
  KEY `staff_id` (`staff_id`),
  KEY `prof_id` (`prof_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'S001','1234','staff',NULL,'S001',NULL),(2,'S002','1234','staff',NULL,'S002',NULL),(3,'20240B208','1234','student','20240B208',NULL,NULL),(4,'20230B136','1234','student','20230B136',NULL,NULL),(5,'20240B218','1234','student','20240B218',NULL,NULL),(6,'20240B229','1234','student','20240B229',NULL,NULL),(7,'P001','1234','professor',NULL,NULL,'P001'),(8,'P002','1234','professor',NULL,NULL,'P002'),(9,'P003','1234','professor',NULL,NULL,'P003'),(10,'P004','1234','professor',NULL,NULL,'P004'),(11,'P005','1234','professor',NULL,NULL,'P005'),(12,'P006','1234','professor',NULL,NULL,'P006'),(13,'P007','1234','professor',NULL,NULL,'P007'),(14,'P008','1234','professor',NULL,NULL,'P008'),(15,'P009','1234','professor',NULL,NULL,'P009'),(16,'P010','1234','professor',NULL,NULL,'P010'),(17,'P011','1234','professor',NULL,NULL,'P011'),(18,'P012','1234','professor',NULL,NULL,'P012'),(19,'P013','1234','professor',NULL,NULL,'P013'),(20,'P014','1234','professor',NULL,NULL,'P014'),(21,'P015','1234','professor',NULL,NULL,'P015');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'sugang_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-04 12:54:51
