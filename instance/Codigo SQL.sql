CREATE TABLE IF NOT EXISTS `Usuarios` (
	`id` integer primary key NOT NULL UNIQUE,
	`nombre` TEXT NOT NULL,
	`apellido` TEXT NOT NULL,
	`cedula` TEXT NOT NULL UNIQUE,
	`correo` TEXT NOT NULL,
	`token` TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `Organizadores` (
	`id` integer primary key NOT NULL UNIQUE,
	`nombre` TEXT NOT NULL,
	`id_usuario` INTEGER NOT NULL,
FOREIGN KEY(`id_usuario`) REFERENCES `Usuarios`(`id`)
);
CREATE TABLE IF NOT EXISTS `Eventos` (
	`id` integer primary key NOT NULL UNIQUE,
	`nombre` TEXT NOT NULL,
	`fecha` TEXT NOT NULL,
	`edad_minima` INTEGER NOT NULL,
	`id_organizador` INTEGER NOT NULL,
FOREIGN KEY(`id_organizador`) REFERENCES `Organizadores`(`id`)
);
CREATE TABLE IF NOT EXISTS `Personas` (
	`id` integer primary key NOT NULL UNIQUE,
	`nombre` TEXT NOT NULL,
	`apellido` TEXT NOT NULL,
	`cedula` TEXT NOT NULL,
	`correo` TEXT NOT NULL,
	`fecha_nacimiento` TEXT NOT NULL,
	`id_organizador` INTEGER NOT NULL,
FOREIGN KEY(`id_organizador`) REFERENCES `Organizadores`(`id`)
);
CREATE TABLE IF NOT EXISTS `Asistencias` (
	`id` integer primary key NOT NULL UNIQUE,
	`id_evento` INTEGER NOT NULL,
	`id_persona` INTEGER NOT NULL,
	`timestamp_llegada` REAL NOT NULL,
FOREIGN KEY(`id_evento`) REFERENCES `Eventos`(`id`),
FOREIGN KEY(`id_persona`) REFERENCES `Personas`(`id`)
);

FOREIGN KEY(`id_usuario`) REFERENCES `Usuarios`(`id`)
FOREIGN KEY(`id_organizador`) REFERENCES `Organizadores`(`id`)
FOREIGN KEY(`id_organizador`) REFERENCES `Organizadores`(`id`)
FOREIGN KEY(`id_evento`) REFERENCES `Eventos`(`id`)
FOREIGN KEY(`id_persona`) REFERENCES `Personas`(`id`)