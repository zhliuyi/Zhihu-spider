import redis
from .settings import *#   . 加一个当前路径找的更快
class Reids_client(object):#(object)让python2也可以用#被实例化，连接就创建好了
    def __init__(self):#也要密码，扩展性
        if PASSWORD:
            self._db = redis.Redis(host =HOST,port = PORT,password=PASSWORD)
        else:
            self._db = redis.Redis(host =HOST,port = PORT)
    #从头不获取一定数量的代理，是为了校验
    def get(self,count=1):#count=1获取多少个，写入就不用传，传就可以自己改
        proxies = self._db.lrange(PROXIES,0,count-1)#获取多少个代理
        #删除，将获取到的代理删除。
        self._db.ltrim(PROXIES,count,-1)#ltrim()是将哪些保留
        return proxies
    #提供一个从尾部获取代理的方法：用代理的时候就从尾部获取一个最新的
    def pop(self):
        try:#异常：当代理池为空
            ##_db.rpop(PROXIES)是什么类型的，redis存的是二进制byte类型，所以需要decode将他变成字符串
            return self._db.rpop(PROXIES).decode('utf-8')#因为redis里存的是byte类型
        except Exception:
            print('代理池为空！|无法获取！')

    # 添加代理，从尾部添加
    def put(self,proxy):
        self._db.rpush(PROXIES,proxy)

    #获取代理池的长度
    @property#不用传参，将一个方法变成属性
    def queue_len(self):
        return self._db.llen(PROXIES)

    #删除代理池
    def fulsh(self):
        self._db.flushdb()


