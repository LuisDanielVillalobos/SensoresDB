USE [Sensores]
GO

/****** Object:  StoredProcedure [dbo].[usp_InsertDataSensor]    Script Date: 14/11/2025 02:41:26 p. m. ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:		LuisDaniel
-- Create date: 08/10/2025
-- Description:	Procedimiento para insertar informacion al sensor
-- =============================================
CREATE PROCEDURE [dbo].[usp_InsertDataSensor] 
	-- Add the parameters for the stored procedure here
	@macSensor varchar(17), 
	@capa tinyint,
	@no_paquete int,
	@distancia1 float,
	@distancia2 float,
	@distancia3 float,
	@temperatura float,
	@humedad float,
	@Q1 float,
	@Q2 float,
	@Q3 float,
	@Q4 float

AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

	INSERT INTO dbo.Data_sensor (
		MAC_Sensor, Capa, No_paquete, Distancia_1, Distancia_2, Distancia_3,
		Temperatura, Humedad, Q1, Q2, Q3, Q4
	)
	VALUES (
		@macSensor, @capa, @no_paquete, @distancia1, @distancia2, @distancia3,
		@temperatura, @humedad, @Q1, @Q2, @Q3, @Q4
	);
END
GO


