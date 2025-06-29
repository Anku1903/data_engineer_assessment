CREATE TABLE Address_info (
  Address_ID INT AUTO_INCREMENT PRIMARY KEY,
  Address VARCHAR(255),
  Street_Address VARCHAR(255),
  City VARCHAR(100),
  State VARCHAR(50),
  Zip INT
);



CREATE TABLE Property (
  Property_ID INT AUTO_INCREMENT PRIMARY KEY,
  Property_Title VARCHAR(255) NOT NULL,
  Market VARCHAR(100),
  Flood VARCHAR(50),
  Property_Type VARCHAR(50),
  Highway VARCHAR(50),
  Train VARCHAR(50),
  Tax_Rate DECIMAL(10,2),
  SQFT_Basement INT,
  HTW VARCHAR(10),
  Pool VARCHAR(10),
  Commercial VARCHAR(10),
  Water VARCHAR(50),
  Sewage VARCHAR(50),
  Year_Built INT,
  SQFT_MU INT,
  SQFT_Total INT,
  Parking VARCHAR(50),
  Bed INT,
  Bath INT,
  BasementYesNo VARCHAR(10),
  Layout VARCHAR(50),
  Rent_Restricted VARCHAR(10),
  Neighborhood_Rating INT,
  Latitude DECIMAL(10,8),
  Longitude DECIMAL(11,8),
  Subdivision VARCHAR(100),
  School_Average DECIMAL(10,2),
  Address_ID INT NOT NULL REFERENCES Address_info(Address_ID)
);

CREATE TABLE Leads (
  Lead_ID INT AUTO_INCREMENT PRIMARY KEY,
  Property_ID INT NOT NULL REFERENCES Property(Property_ID),
  Reviewed_Status VARCHAR(50),
  Most_Recent_Status VARCHAR(50),
  Source VARCHAR(50),
  Occupancy VARCHAR(10),
  Net_Yield DECIMAL(10,2),
  IRR DECIMAL(10,2),
  Selling_Reason VARCHAR(100),
  Seller_Retained_Broker VARCHAR(10),
  Final_Reviewer VARCHAR(100)
);

CREATE TABLE Valuation (
  Valuation_ID INT AUTO_INCREMENT PRIMARY KEY,
  Property_ID INT NOT NULL REFERENCES Property(Property_ID),
  Previous_Rent INT,
  List_Price INT,
  Zestimate INT,
  ARV INT,
  Expected_Rent INT,
  Rent_Zestimate INT,
  Low_FMR INT,
  High_FMR INT,
  Redfin_Value INT
);

CREATE TABLE Rehab (
  Rehab_ID INT AUTO_INCREMENT PRIMARY KEY,
  Property_ID INT NOT NULL REFERENCES Property(Property_ID),
  Underwriting_Rehab INT,
  Rehab_Calculation INT,
  Paint VARCHAR(10),
  Flooring_Flag VARCHAR(10),
  Foundation_Flag VARCHAR(10),
  Roof_Flag VARCHAR(10),
  HVAC_Flag VARCHAR(10),
  Kitchen_Flag VARCHAR(10),
  Bathroom_Flag VARCHAR(10),
  Appliances_Flag VARCHAR(10),
  Windows_Flag VARCHAR(10),
  Landscaping_Flag VARCHAR(10),
  Trashout_Flag VARCHAR(10)
);

CREATE TABLE HOA (
  HOA_ID INT AUTO_INCREMENT PRIMARY KEY,
  Property_ID INT NOT NULL REFERENCES Property(Property_ID),
  HOA INT,
  HOA_Flag VARCHAR(10)
);

CREATE TABLE Taxes (
  Tax_ID INT AUTO_INCREMENT PRIMARY KEY,
  Property_ID INT NOT NULL REFERENCES Property(Property_ID),
  Taxes INT
);
