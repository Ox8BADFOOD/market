from django.core.files.storage import Storage
from market import settings

class FastDFSStorage(Storage):
    """自定义文件存储系统，修改存储的方案"""
    def __init__(self, fdfs_base_url=None):
        """
        构造方法，可以不带参数，也可以携带参数
        :param fdfs_base_url:Storage的IP
        """
        self.fdfs_base_url = fdfs_base_url or settings.MEDIA_URL


    def _open(self, name, mode='rb'):
        """
        打开文件时会被调用：文档告诉我们必须重写
        :param name: 文件路径
        :param mode: 打开方式
        :return:
        """
        # 因为当前不是去打开某个文件，所以这个方法目前没有用，但是又必须重写所以pass
        pass

    def _save(self, name, content):
        """
        保存文件时会被调用，文档告诉我们必须重写
        :param name: 文件路径
        :param content: 文件的二进制类容
        :return: None
        """
        pass

    def url(self, name):
        """
        返回name所指文件的绝对URL
        :param name: 要读取文件的引用:group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        :return: http://192.168.103.158:8888/group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        """
        return settings.MEDIA_URL + name
