import sqlite3
import pandas as pd
import os
from utils import cprint

class SQLiteDBHelper:
    def __init__(self, db_name, fresh_start=False, csv_path=None):
        self.db_name = db_name
        self.connection = self.create_connection()
        
        if fresh_start:
            cprint('Deleting Tables')
            self.delete_tables() # Protected from None Deletion
            cprint('Creating Tables')
            self.create_tables() # Protected from Duplication
            cprint(f'Initializing Tables using {csv_path}')
            self.init_tables(csv_path)

    def create_tables(self):
        """Create the necessary tables for the schema."""
        create_polygon_table = """
        CREATE TABLE IF NOT EXISTS Polygon (
            id TEXT PRIMARY KEY
        );
        """
        create_landunit_table = """
        CREATE TABLE IF NOT EXISTS LandUnit (
            code TEXT PRIMARY KEY
        );
        """
        create_plotplan_table = """
        CREATE TABLE IF NOT EXISTS PlotPlan (
            name TEXT PRIMARY KEY
        );
        """
        create_polygon_landunit_table = """
        CREATE TABLE IF NOT EXISTS PolygonLandUnit (
            polygon_id TEXT,
            landunit_code TEXT,
            PRIMARY KEY (polygon_id, landunit_code)
            FOREIGN KEY (polygon_id) REFERENCES Polygon(id),
            FOREIGN KEY (landunit_code) REFERENCES LandUnit(code)
        );
        """
        create_landunit_plotplan_table = """
        CREATE TABLE IF NOT EXISTS LandUnitPlotPlan (
            landunit_code TEXT,
            plotplan_name TEXT,
            PRIMARY KEY (landunit_code, plotplan_name)
            FOREIGN KEY (landunit_code) REFERENCES LandUnit(code),
            FOREIGN KEY (plotplan_name) REFERENCES PlotPlan(name)
        );
        """
        
        self.execute_query(create_polygon_table)
        self.execute_query(create_landunit_table)
        self.execute_query(create_plotplan_table)
        self.execute_query(create_polygon_landunit_table)
        self.execute_query(create_landunit_plotplan_table)

    def init_tables(self, csv_path):
        """ Initialisation of tables Polygon, LandUnit, PolygonLandUnit."""
        self.import_poly_landunit_from_csv(csv_path)

    def import_poly_landunit_from_csv(self, csv_path):
        """Import PolyID and LandUnit values from a CSV file into the tables."""
        try:
            df = pd.read_csv(csv_path)
            for index, row in df.iterrows():
                polygon_id = row['PolyID']
                landunit_code = row['LandUnit']
                self.upsert_polygon(polygon_id)
                self.upsert_landunit(landunit_code)
                self.upsert_polygon_landunit(polygon_id, landunit_code)
        except Exception as e:
            cprint(f"Error importing CSV to database: {e}")
            
    def upsert_polygon(self, polygon_id):
        query = "INSERT OR REPLACE INTO Polygon (id) VALUES (?)"
        self.execute_query(query, (polygon_id,))

    def upsert_landunit(self, landunit_code):
        query = "INSERT OR REPLACE INTO LandUnit (code) VALUES (?)"
        self.execute_query(query, (landunit_code,))

    def upsert_plotplan(self, plotplan_name):
        query = "INSERT OR REPLACE INTO PlotPlan (name) VALUES (?)"
        self.execute_query(query, (plotplan_name,))

    def upsert_polygon_landunit(self, polygon_id, landunit_code):
        query = "INSERT OR REPLACE INTO PolygonLandUnit (polygon_id, landunit_code) VALUES (?, ?)"
        self.execute_query(query, (polygon_id, landunit_code))

    def upsert_landunit_plotplan(self, landunit_code, plotplan_name):
        query = "INSERT OR REPLACE INTO LandUnitPlotPlan (landunit_code, plotplan_name) VALUES (?, ?)"
        self.execute_query(query, (landunit_code, plotplan_name))

    def delete_tables(self):
        """Drop all tables in the database."""
        drop_polygon_table = "DROP TABLE IF EXISTS Polygon"
        drop_landunit_table = "DROP TABLE IF EXISTS LandUnit"
        drop_plotplan_table = "DROP TABLE IF EXISTS PlotPlan"
        drop_polygon_landunit_table = "DROP TABLE IF EXISTS PolygonLandUnit"
        drop_landunit_plotplan_table = "DROP TABLE IF EXISTS LandUnitPlotPlan"
        self.execute_query(drop_polygon_table)
        self.execute_query(drop_landunit_table)
        self.execute_query(drop_plotplan_table)
        self.execute_query(drop_polygon_landunit_table)
        self.execute_query(drop_landunit_plotplan_table)

    def execute_query(self, query, params=None):
        """Wrapper to execute a query and return the results."""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            cprint(f"Error executing query: {e}")
            return None

    def create_connection(self):
        """Create a database connection and return the connection object."""
        try:
            conn = sqlite3.connect(self.db_name)
            return conn
        except sqlite3.Error as e:
            cprint(f"Error creating connection to database: {e}")
            return None
    
    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
