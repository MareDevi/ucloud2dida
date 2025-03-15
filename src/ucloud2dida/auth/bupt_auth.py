import requests
import json
import re
from ..utils.logger import logger
from ..utils.exceptions import AuthenticationError


class BuptAuthenticator:
    def __init__(self):
        self.cookies = None

    def authenticate(self, username, password):
        """执行认证流程"""
        logger.info("开始北邮认证")
        try:
            execution = self._get_execution_value(username, password)
            ticket = self._get_login_cookies(username, password, execution)
            auth_data = self._post_api(ticket)
            self._save_auth_data(auth_data)
            logger.info("北邮认证完成")
            return auth_data
        except Exception as e:
            logger.error(f"北邮认证失败: {str(e)}")
            raise AuthenticationError(f"北邮认证失败: {str(e)}")

    def _get_execution_value(self, username, password):
        url = "https://auth.bupt.edu.cn/authserver/login?service=http://ucloud.bupt.edu.cn"
        response = self._follow_redirects(url)
        if match := re.search(
            r'<input\s+name="execution"\s+value="([^"]+)"', response.text
        ):
            return match.group(1)
        logger.error("获取execution值失败")
        raise AuthenticationError("获取execution值失败")

    def _follow_redirects(self, url):
        response = requests.get(url, allow_redirects=False)
        while response.status_code == 302:
            redirected_url = response.headers["Location"]
            response = requests.get(redirected_url, allow_redirects=False)
        self.cookies = response.cookies
        return response

    def _get_login_cookies(self, username, password, execution):
        url = "https://auth.bupt.edu.cn/authserver/login?service=http://ucloud.bupt.edu.cn"
        data = {
            "username": username,
            "password": password,
            "submit": "登录",
            "type": "username_password",
            "execution": execution,
            "_eventId": "submit",
        }

        response = requests.post(
            url, data=data, allow_redirects=False, cookies=self.cookies
        )
        redirected_url = response.headers["Location"]
        if match := re.search(r"ticket=(\S+)", redirected_url):
            return match.group(1)
        raise AuthenticationError("无法获取ticket")

    def _post_api(self, ticket):
        """从API获取认证数据"""
        logger.debug("请求UCloud认证数据")
        response = requests.get("https://ucloud.bupt.edu.cn/", allow_redirects=True)
        js_pattern = r'<script src="([^"]+\.js)"></script>'
        js_links = re.findall(js_pattern, response.text)

        for link in js_links:
            if "index" in link:
                js_content = requests.get(f"https://ucloud.bupt.edu.cn/{link}").text
                if match := re.search(
                    r'headers:\s*{\s*Authorization:\s*"([^"]+)",\s*"Tenant-Id":\s*"([^"]+)"\s*}',
                    js_content,
                ):
                    auth_token = match.group(1)
                    tenant_id = match.group(2)

                    url = "https://apiucloud.bupt.edu.cn/ykt-basics/oauth/token"
                    headers = {
                        "Authorization": auth_token,
                        "Tenant-Id": tenant_id,
                        "Accept": "application/json",
                    }
                    response = requests.post(
                        url,
                        headers=headers,
                        data={"ticket": ticket, "grant_type": "third"},
                    )
                    data = response.json()

                    return {
                        "tenant_id": tenant_id,
                        "user_id": data["user_id"],
                        "auth_token": auth_token,
                        "blade": data["access_token"],
                    }

        logger.error("获取认证信息失败")
        raise AuthenticationError("获取认证信息失败")

    def _save_auth_data(self, auth_data):
        """保存认证数据到文件"""
        logger.debug("保存认证数据")
        with open("auth.json", "w") as f:
            json.dump(auth_data, f)


# 创建全局认证器实例
authenticator = BuptAuthenticator()
get_co_and_sa = authenticator.authenticate
