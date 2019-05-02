SELECT users.firstName, users.lastName, checkingsystem.deviceId, device.deviceStatus
from users
inner join checkingsystem 
on users.userId = checkingsystem.userId 
inner join device on checkingsystem.deviceId = device.deviceId
where checkingsystem.returnDate is null; 