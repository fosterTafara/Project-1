-- DROP DATABASE Project;

CREATE Database IF NOT EXISTS Project;
USE Project;

SET default_storage_engine= InnoDb;

-- Drop table Building;
CREATE TABLE IF NOT EXISTS Building (
location_id varchar(75),
building_address varchar(50),
Primary Key (location_id) 
);

-- Drop table Users;
CREATE TABLE IF NOT EXISTS Users (
user_id int NOT NULL AUTO_INCREMENT, -- Just numbers
first_name varchar (50),
last_name varchar (50),
email varchar (50), -- could just add UNIQUE here as a constraint
location_id varchar (75),
permision_id varchar (50), -- dont know if it will be numbers/characters or both  
Primary Key (user_id),
foreign key (location_id) references Building (location_id),
UNIQUE KEY (email)
);

-- Drop table Device;
CREATE TABLE IF NOT EXISTS Device (
device_id int not null AUTO_INCREMENT, -- need confirmation what device id will look like
device_name varchar(50),
device_type varchar(50),
os_type varchar(30),
os_version varchar(20),
device_ram varchar(10),
device_cpu varchar(50),
device_bit int,
screen_res varchar(30),
device_grade varchar(30),
device_uuid varchar(100),
-- location_id varchar(50),  don't think this is needed
Primary Key (device_id)
);
ALTER TABLE Device AUTO_INCREMENT=1051;

-- Drop table CheckingSystem;
CREATE TABLE IF NOT EXISTS CheckingSystem (
user_id INT,
device_id INT,
borrow_date DATE, -- CONSIDER DATETIME FORMAT OR TIMESTAMP
borrow_time TIME,
return_date DATE,
return_time TIME,
-- project varchar (50), 
foreign key (device_id) references Device (device_id),
foreign key (user_id) references Users (user_id)
);

INSERT INTO Device (device_id, device_name, device_type, os_type, os_version, device_ram, device_cpu,
device_bit, screen_res, device_grade, device_uuid) VALUES
("1000","Q Bert","Amazon Fire HD 7","Android","4.5.5","1 GB","Dual-Core 1.5GHz","1","800 x 1280 (216ppi)","Low","None"),
("1001","Princess Zelda","Dell E 6400","Windows","TBC","TBC","TBC","1","TBC","TBC","TBC"),
("1002","Link","Dell Laptop","Windows","TBC","TBC","TBC","1","TBC","TBC","TBC"),
("1003","Link","Dell Laptop","Windows","TBC","TBC","TBC","1","TBC","TBC","TBC"),
("1004","Bison","Galaxy S5","Android","4.4.2","2 GB","Quad-Core 2.5GHz","1","1080 x 1920 (432ppi)","Medium","None"),
("1005","Balrog","Galaxy S7 Edge","Android","6.0.1","4 GB","Octa-Core 4x2.3 GHz & 4x1.6 GHz","1","1440 x 2560 (534ppi)","High","None"),
("1006","E-Honda","Galaxy Tab 1","Android","4.0.4","1 GB","Dual-Core 1GHz","1","800 x 1280 (149ppi)","Low","None"),
("1007","Zangief","Galaxy Tab 4","Android","5.0.2","1.5 GB","Quad-Core 1.2GHz","1","800 x 1280 (216ppi)","Low","None"),
("1008","Guile","HTC One mini 2","Android","4.4.2","1 GB","Quad-Core 1.2GHz","1","720 x 1280 (326ppi)","Low","None"),
("1009","Dr Robotnik","iPad 4","IOS","10.1","1GB","Dual-Core 1.4GHz","32","1536 x 2048 (264ppi)","Medium","3e751193bdbf92b35a440f225318b5498de96c9e"),
("1010","Fox McCloud","iPad Air (retina)","IOS","10.3.2","1 GB DDR3","Dual-Core 1.3GHz","64","1536 x 2048 (264ppi)","Medium","7c7a369fd078c67f1cc123685ad887d3e32a6552"),
("1011","Kratos","iPad Air 2","IOS","9.3.4","2 GB","Octa-core 1.5 GHz","64","2048 x 1536 (264ppi)","High","0b7886a9d846ea7cd50f80c1eefbeba3ead44b21"),
("1012","Silver","iPad Mini","IOS","9.2","500MB","Dual-Core 1GHz","32","768 x 1024 (163 ppi)","Obsolete","e73f9b4cb93e83f718622016e31d90c06692d782"),
("1013","Vector","iPad Mini","IOS","8.4","500MB","Dual-Core 1GHz","32","768 x 1024 (163 ppi)","Obsolete","fc4fde35ea28101e8a11f9a706c3fc4eff4537cf"),
("1014","Espio","iPad Mini 2 (retina)","IOS","11.2","1GB","Dual-Core 1.3GHz","64","1536 x 2048 (324 ppi)","Low","7ecfbae1544a8d56ccdacd6dc27ed9038196b2f5"),
("1015","Knuckles","iPad Mini 2 (retina)","IOS","10 Beta 2","1GB","Dual-Core 1.3GHz","64","1536 x 2048 (324 ppi)","Low","82b93d029411bbede53c16523c7f6c58054e526b"),
("1016","Max Payne","iPad mini 4","IOS","10.1","2 GB","Quad-core 1.5 GHz","64","2048 x 1536 (326ppi)","High","03d9afd06672d3db910b3330f88d68290119022a"),
("1017","???","iPad Pro","IOS","11.1","4 GB","Hexa-core 2.39 GHz","64","2224 x 1668","High","193ea81981bbc3ea8535688ea1c8b5f6eaa4514e"),
("1018","Barret","iPhone 4","IOS","7.1.2","500MB","Single-Core 1GHz","32","640 x 960 (330ppi)","Obsolete","40b7c83097b9a803b38b193f97124f21682653a4"),
("1019","Vincent","iPhone 4s","IOS","8.4.0","500MB","Dual-Core 1GHz","32","640 x 960 (326ppi)","Obsolete","369fcdf892d01f490215c4d9e0f2570d707c2f8a"),
("1020","Basch","iPhone 5","IOS","10.0.1","1GB","Dual-Core 1.3GHz","32","640 x 1136 (326ppi)","Low","086deb3ff832fe09fc492d835f8f539d853a70d5"),
("1021","Karen","iPhone 5s","IOS","11.1.1","1GB","Dual-Core 1.3GHz","64","640 x 1136 (326ppi)","Low","11c7581c85ca118915b345a2da4fb558bce0cdb7"),
("1022","Squall","iPhone 6","IOS","10.3.2","1 GB DDR3","Dual-Core 1.4GHz","64","750 x 1334 (326ppi)","Medium","a3eb076b6f1d46fa40c3661ed928592df544b945"),
("1023","Cid","iPhone 6+","IOS","11.2","1 GB DDR3","Dual-Core 1.4GHz","64","1080 x 1920 (401ppi)","Medium","9cda2720c72ff3e26e82e49ea796c8a4f9246f8e"),
("1024","Fran","iPhone 6S","IOS","11.2.2","2 GB DDR 4","Dual-Core 1.85 GHz","64","1334 x 750 (326 ppi)","High","49c2e825d69a758ff9379dd1ba0b9c24913f645e"),
("1025","Mr Bones","iPhone 7","IOS","10.3.3","2 GB","Quad-core 2.34 GHz","64","750 x 1334 (326ppi)","High","702c1adf30db79fd37da10e5866eb63157ef7356"),
("1026","Lara Croft","iPhone 7+","IOS","10.3.2","3 GB","Quad-core 2.34 GHz","64","1920 x 1080 (401ppi)","High","f65ca802c90c9f80669fb4f18d8aa422da594875"),
("1027","Mr Pricklepants","iPhone 7+","IOS","11.1.2","3 GB","Quad-core 2.34 GHz","64","1920 x 1080 (401ppi)","High","788e06f1bf0c9da090d5c51ad15034e699f793ce"),
("1028","Seifer","iPhone 8","IOS","11.0.3","2 GB","Hexa-core 2.39 GHz","64","750 x 1334 (326ppi)","High","TBC"),
("1029","Mr X","iPhone x","IOS","11.1.2","3 GB","Hexa-core 2.39 GHz","64","2436 x 1125 (458ppi)","High","903e2d8c7291d8d3d386a3a0886f21d969704b54"),
("1030","Gordon Freeman","iPod 5","IOS","9.3.5","500MB","Dual-Core 1GHz","32","640 x 1136 (326ppi)","Obsolete","8df683d2213df8bffdb6f8157e38c8b41809fb69"),
("1031","Guy Brush","iPod 5","IOS","9","500MB","Dual-Core 1GHz","32","640 x 1136 (326ppi)","Obsolete","TBC"),
("1032","Iggy","iPod 5","IOS","8.4.1","500MB","Dual-Core 1GHz","32","640 x 1136 (326ppi)","Obsolete","ba9ff54ef1d18b27feb179271c49f90a6d813531"),
("1033","John Marston","iPod 5","IOS","8.3.0","500MB","Dual-Core 1GHz","32","640 x 1136 (326ppi)","Obsolete","53ddbab0034331cab54858dd980906cbb457367f"),
("1034","Lemmy","iPod 5","IOS","9.0.2","500MB","Dual-Core 1GHz","32","640 x 1136 (326ppi)","Obsolete","d4b31d4fef7b969148b9493b32cd53ffa280bf3a"),
("1035","Toad","iPod 5","IOS","8.1.1","500MB","Dual-Core 1GHz","32","640 x 1136 (326ppi)","Obsolete","0395cc76b2f123d2debb5db2d26a8e4b44d44218"),
("1036","Slippy Toad","iPod 6","IOS","10.3","1GB","Dual-Core 1.4GHz","64","750 x 1334 (326 ppi)","Low","cdc1507bc464102fb7321e72273b58d3bee8a6c5"),
("1037","King","Kindle Fire HD","Android","TBC","1 GB","Dual-Core 1.5GHz","1","1200 x 1920 (254ppi)","Low","None"),
("1038","Glados","LG G Pad","Android","4.4.2","2 GB","Quad-Core 1.7GHz","1","1200 x 1920 (273ppi)","Medium","None"),
("1039","Wheatley","LG G3","Android","5.0.0","3 GB","Quad-Core 2.5GHz","1","1440 x 2560 (538ppi)","Medium","None"),
("1040","Ken","Nexus 10","Android","4.4.4","2 GB","Dual-Core 1.7GHz","1","1600 x 2560 (299ppi)","Low","None"),
("1041","Blanka","Nexus 7","Android","5.0.2","1 GB","Quad-Core 1.2GHz","1","800 x 1280 (216ppi)","Low","None"),
("1042","Roach","Nexus 9","Android","7 Preview","2 GB","Dual-Core 2.3GHz","1","1536 x 2048 (281ppi)","Medium","None"),
("1043","???","Rift","VR","TBC","TBC","TBC","0","TBC","TBC","TBC"),
("1044","Akuma","Samsung Tab A","Android","5.0.2","2 GB","Quad-Core 1.2GHz","1","768 x 1024 (132ppi)","Low","None"),
("1045","Batman","Vive","VR","TBC","TBC","TBC","0","TBC","TBC","TBC"),
("1046","Superman","Vive","VR","TBC","TBC","TBC","0","TBC","TBC","TBC"),
("1047","Kuma","W8 Nokia","Windows","8.1","500MB","Dual-Core 1GHz","1","480 x 800 (233ppi)","Low","TBC"),
("1048","Gun Jack","W8 Surface","Windows","TBC","2 GB","Quad-Core 1.3GHz","1","768 x 1366 (148ppi)","Low - Mid","TBC"),
("1049","Sonic","iPad 2","IOS","8.4.1","500MB","Dual-Core 1GHz","32","768 x 1024 (132ppi)","Obsolete","6745ece4fd066224e05129278e7eb75c562fea28"),
("1050","Pac Man","Chromebook","Windows","TBC","TBC","TBC","1","TBC","TBC","TBC")

;