import arcpy
from arcpy import env

#Setting the environmental settings
arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:/Users/3857611/Downloads/"


"""
A definition that calculates the social safety by means of crime statistics for 2015 from Statistics Netherlands on a neighborhood level.
"""

def criminalityIndex(table, neighborhoods):    
    inputTable = arcpy.ExcelToTable_conversion(table, "criminalityTable", "")    
    crimeLayer = arcpy.MakeFeatureLayer_management(neighborhoods, "crime_layer")

    #Joining the crime table with the CBS neighborhood dataset table
    arcpy.JoinField_management(crimeLayer, "statcode", inputTable, "STATCODE", ["inwoners", "crimeTotal", "relatCrime"])   
    criminalityFC = arcpy.CopyFeatures_management(neighborhoods, "criminality2015")    
    arcpy.DeleteField_management(criminalityFC, ["AREA", "POLY_AREA", "standStep1", "standCrime"])    
    arcpy.AddGeometryAttributes_management(criminalityFC, "AREA", "", "SQUARE_KILOMETERS")    

    #Calculating the population density on a neighborhood level as equal input for the standardized crime rate
    arcpy.AddField_management(criminalityFC, "standStep1", "FLOAT", 10, 4, "", "", "NULLABLE") 
    arcpy.CalculateField_management(criminalityFC, "standStep1", "[INWONERS] / [POLY_AREA]")    

    #Calculating a standardized crime rate by dividing the total amount of crimes by the population density
    arcpy.AddField_management(criminalityFC, "standCrime", "FLOAT", 10, 4, "", "", "NULLABLE")    
    #To prevent overflow errors, it is avoided that there is a division by 0
    expression1 = "Calculate(!crimeTotal!, !standStep1!, !standCrime!)"
    codeblock1 = """def Calculate(x, y, z):
        if (x != 0 and y != 0):
            z = x / y
        elif (x == 0 or y == 0):
            z = 0
        return z """
    arcpy.CalculateField_management(criminalityFC, "standCrime", expression1, "PYTHON_9.3", codeblock1)
    """
    arcpy.AddField_management(criminalityFC, "crime", "FLOAT", 10, 4, "", "", "NULLABLE")    
    expression2 = "Calculate(!relatCrime!, !crime!)"
    codeblock2 = "def Calculate(x, y):
        if (x == '.'):
            y = 0
        elif (x != '.'):
            y = x
        return y"
    arcpy.CalculateField_management(criminalityFC, "crime", expression2, "PYTHON_9.3", codeblock2)
    arcpy.DeleteField_management(criminalityFC, ["INWONERS_1", "STATCODE_1", "CRIMETOT_1"])
    """
    return criminalityFC
    

#Setting the input variables and executing the script
neighborhoods = "cbs_buurt_2014_gegeneraliseerdPolygon.shp"
table = "neighborhoodCriminality2015.xlsx"

criminalityIndex(table, neighborhoods)
