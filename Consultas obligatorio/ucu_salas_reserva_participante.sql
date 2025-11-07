-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: ucu_salas
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `reserva_participante`
--

DROP TABLE IF EXISTS `reserva_participante`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reserva_participante` (
  `ci_participante` varchar(20) NOT NULL,
  `id_reserva` int NOT NULL,
  `fecha_solicitud_reserva` datetime DEFAULT CURRENT_TIMESTAMP,
  `asistencia` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ci_participante`,`id_reserva`),
  KEY `id_reserva` (`id_reserva`),
  CONSTRAINT `reserva_participante_ibfk_1` FOREIGN KEY (`ci_participante`) REFERENCES `participante` (`ci`),
  CONSTRAINT `reserva_participante_ibfk_2` FOREIGN KEY (`id_reserva`) REFERENCES `reserva` (`id_reserva`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reserva_participante`
--

LOCK TABLES `reserva_participante` WRITE;
/*!40000 ALTER TABLE `reserva_participante` DISABLE KEYS */;
INSERT INTO `reserva_participante` VALUES ('4.111.111-1',1,'2025-11-06 18:20:38',1),('4.111.111-1',2,'2025-11-06 18:20:38',0),('5.222.222-2',3,'2025-11-06 18:20:38',1),('6.333.333-3',1,'2025-11-06 18:20:38',1),('7.444.444-4',4,'2025-11-06 18:20:38',0);
/*!40000 ALTER TABLE `reserva_participante` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-06 18:24:54
