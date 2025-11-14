USE [Sensores]
GO

/****** Object:  Table [dbo].[Data_sensor]    Script Date: 14/11/2025 02:40:55 p. m. ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Data_sensor](
	[MAC_Sensor] [varchar](17) NOT NULL,
	[Capa] [tinyint] NOT NULL,
	[No_paquete] [int] NOT NULL,
	[Distancia_1] [float] NOT NULL,
	[Distancia_2] [float] NOT NULL,
	[Distancia_3] [float] NOT NULL,
	[Temperatura] [float] NOT NULL,
	[Humedad] [float] NOT NULL,
	[Q1] [float] NOT NULL,
	[Q2] [float] NOT NULL,
	[Q3] [float] NOT NULL,
	[Q4] [float] NOT NULL,
	[Identificador] [bigint] IDENTITY(1,1) NOT NULL,
	[Fecha] [datetime] NOT NULL,
 CONSTRAINT [PK_Data_sensor] PRIMARY KEY CLUSTERED 
(
	[Identificador] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Data_sensor] ADD  CONSTRAINT [DF_Data_sensor_Fecha]  DEFAULT (getdate()) FOR [Fecha]
GO

