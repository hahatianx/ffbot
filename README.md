#Robot yukari

###About
This is a simple process which can be deployed on a linux/macOS machine.
It is aimed at providing FF14 related information gathered 
from the Internet to all the members in the QQ group.  The project is
not well designed under 'object-orientation', and it is not designed for highly
concurrent occasions. Feel free to clone and deploy it on your machine for personal 
and lite use.


Actually, there have been several FF14 QQ robots released before mine.
[TATA](https://bbs.nga.cn/read.php?tid=14726260&rand=978);
[TATARU](https://bbs.nga.cn/read.php?tid=14654174&rand=524) More fancy
functions are provided.  However, for limited resources, it may be difficult to
have a chance to get one.  That is why I decided to construct my own project.

Thanks Bluefissure and his source code.  I have learnt a lot from his code.
Here is his robot [TATA](https://github.com/Bluefissure/FFXIVBOT/) on github.

###Structure
The whole project consists of several parts.  The backend is a Django application
based on Python3.  The user interface is a qq account, used to exchange information
with other members in the QQ group.  The communication between the two ends is based on
websocket, a full-duplex protocol.  Since no queue structure is applied, the whole
project may be quite low-efficient. And that is why I do not recommended for heavy use.

###Deployment
Before deployment, you have to have two(recommended) machines(1 linux and 1 windows).
The Linux machines is used to run django backend, while the windows machine runs a program
[Coolq](https://cqp.cc/), a qq robot API.
1. Install Redis, Mysql on your linux machine;
2. Clone the source code onto your linux machine, and run it;
3. Download Coolq onto your windows machine;
4. Download HttpApi for Coolq and check your HttpApi Config;

Then your two machines should have real-time communications.  Have Fun!
