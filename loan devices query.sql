use project;
select device.deviceId,device.deviceName, device.deviceType, checkingsystem.dueDate 
from device 
inner join checkingsystem on device.deviceId = checkingsystem.deviceId 
where checkingsystem.userId = users.userId
AND checkingsystem.returnDate is NULL 
AND checkingsystem.holdDate is null;	
	