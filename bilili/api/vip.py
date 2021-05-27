from ..tools import spider
from .utils import MaxRetry


@MaxRetry(2)
def is_vip() -> bool:
    info_api = "https://api.bilibili.com/x/web-interface/nav"
    res_json = spider.get(info_api, timeout=3).json()
    res_json_data = res_json.get("data")
    if res_json_data.get("vipStatus") == 1:
        return True
    return False
