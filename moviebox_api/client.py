import requests
import json
import logging
import time
from typing import Optional, Dict, Any
from urllib.parse import urlencode, urlparse
from .utils import generate_tr_signature, md5_hex, GATEWAY_SECRET_ONLINE, get_default_client_info, generate_client_token
from .auth import MovieBoxAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieBoxClient:
    BASE_URL = "https://api.inmoviebox.com"

    def __init__(self, auth: Optional[MovieBoxAuth] = None):
        if auth is None:
            auth = MovieBoxAuth()
        self.auth = auth
        self.session = requests.Session()
        # Android app headers
        self.session.headers.update({
            "User-Agent": "okhttp/4.11.0",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "Keep-Alive"
        })

    def get_auth_headers(self, timestamp: str) -> Dict[str, str]:
        """Provides consistent headers matching the MovieBox app's security model."""
        headers = {
            "User-Agent": "MovieBoxPro/16.2.1 (Android 12; Pixel 6)",
            "Accept": "application/json",
            "X-M-Version": "16.2.1",
            "Referer": f"{self.BASE_URL}/",
            "X-Sign-Version": "2.0",
            "X-Client-Token": generate_client_token(),
            "X-Client-Info": json.dumps(get_default_client_info(), separators=(",", ":")),
            "X-Client-Status": "0",
            "X-Play-Mode": "2"
        }
        # Fixed appid to match gateway_sdk initialization parameter and removed appkey (which causes 440)
        headers["appid"] = "4U01pxRu278GqCZKY9"
        headers["region"] = "IN"
        headers["lang"] = "en"
        headers["os"] = "android"
        headers["X-Timestamp"] = timestamp
        return headers

    def request_otp(self, account: str, auth_type: int = 1, type: int = 1):
        """
        Requests an OTP for login or registration.
        POST /wefeed-mobile-bff/user-api/get-sms-code
        type: 1 = Register, 2 = Login, 3 = Reset Password
        """
        payload = {
            "package_name": "com.community.mbox.in",
            "authType": auth_type, # 1=Mail, 0=Phone
            "type": type 
        }
        if "@" in account:
            payload["mail"] = account
            payload["authType"] = 1
        else:
            payload["phone"] = account
            payload["authType"] = 0
            
        res = self.request("POST", "/wefeed-mobile-bff/user-api/get-sms-code", data=payload)
        logger.info(f"OTP Response: {res}")
        
        # API might return code 0 or 200 for success
        if res.get("code") in [200, 0]:
            return {"status": "success", "msg": res.get("msg") or "OTP Sent"}
        
        return {"status": "error", "message": res.get("msg") or "Failed to send OTP", "res": res}

    def login(self, account: str, password: str, auth_type: int = 1):
        hashed_pwd = md5_hex(password)
        payload = {
            "password": hashed_pwd,
            "package_name": "com.community.mbox.in",
            "authType": auth_type,
            "type": 0
        }
        
        if "@" in account:
            payload["mail"] = account
            payload["authType"] = 1
        else:
            payload["phone"] = account
            payload["authType"] = 0
            
        res = self.request("POST", "/wefeed-mobile-bff/user-api/login", data=payload)
        logger.info(f"Login Response: {res}")
        
        if res.get("code") in [200, 0] and "data" in res:
            data = res["data"]
            token = data.get("token")
            user_id = data.get("userId")
            if token:
                self.auth.update_session(token, user_id, data)
                self.auth.is_guest_mode = False
                return {"status": "success", "user": data}
            
        msg = res.get("msg") or "Unknown API Error"
        return {"status": "error", "message": msg, "res": res}

    def register(self, account: str, password: str, otp: str, auth_type: int = 1):
        """
        Official Register Flow with OTP:
        POST /wefeed-mobile-bff/user-api/register
        """
        hashed_pwd = md5_hex(password)
        payload = {
            "password": hashed_pwd,
            "verificationCode": otp,
            "package_name": "com.community.mbox.in",
            "authType": auth_type,
            "type": 1 # For register, type is likely 1
        }
        
        if "@" in account:
            payload["mail"] = account
            payload["authType"] = 1
        else:
            payload["phone"] = account
            payload["authType"] = 0
            
        res = self.request("POST", "/wefeed-mobile-bff/user-api/register", data=payload)
        logger.info(f"Register Response: {res}")
        
        if res.get("code") in [200, 0] and "data" in res:
            data = res["data"]
            token = data.get("token")
            user_id = data.get("userId")
            if token:
                 self.auth.update_session(token, user_id, data)
            self.auth.is_guest_mode = False
            return {"status": "success", "user": data}
            
        msg = res.get("msg") or "Registration Failed"
        return {"status": "error", "message": msg, "res": res}

    def logout(self):
        self.auth.login_guest()
        return {"status": "success"}

    def convert_domains(self, domains=None):
        """
        Uses the Global Server Load Balancer (GSLB) to find working mirrors.
        This is the "Phase 5" ultimate failover.
        """
        if domains is None:
            domains = [urlparse(self.BASE_URL).netloc]
            
        from .utils import generate_gslb_sign, sha256_hex
        
        # Pin device info for GSLB stability
        package_name = "com.community.mbox.in"
        device_id = "868203051234567" # Match test script
        key = sha256_hex(device_id)
        
        # Build payload in exact Smali order
        payload = {
            "appId": package_name,
            "key": key,
            "oldKey": "",
            "domains": domains,
            "mcc": "404",
            "locale": "IN",
            "language": "en",
            "model": "SM-S918B"
        }
        
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "X-Gslb-Sign": generate_gslb_sign(package_name, device_id),
            "User-Agent": "okhttp/4.11.0"
        }
        
        # Official app uses compact JSON for GSLB
        body = json.dumps(payload, separators=(',', ':'))
        
        try:
            url = "https://gslb.shalltry.com/gslb/domain/convert"
            logger.info(f"Pinging GSLB for domains: {domains}")
            res = requests.post(url, data=body, headers=headers, timeout=10)
            data = res.json()
            if data.get("code") == 0 and "data" in data:
                # Return the map of original -> converted domains
                conv_map = data["data"]
                logger.info(f"GSLB Conversion Result: {conv_map}")
                return conv_map
            else:
                logger.error(f"GSLB API Error: {data}")
        except Exception as e:
            logger.error(f"GSLB Conversion failed: {e}")
            if 'res' in locals():
                 logger.error(f"Raw Response: {res.text}")
            
        return {}

    def request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Any = None, **kwargs) -> Dict:
        if params is None:
            params = {}
        
        parsed_base = urlparse(self.BASE_URL)
        if "host" not in params:
             params["host"] = parsed_base.netloc

        url = f"{self.BASE_URL}{endpoint}"
        
        body_str = ""
        if data is not None:
            body_str = json.dumps(data, separators=(',', ':'))

        timestamp = int(time.time() * 1000)
        headers = self.get_auth_headers(str(timestamp))
        # Merge with auth class (token/client status)
        headers.update(self.auth.get_auth_headers())
        
        headers["Content-Type"] = "application/json;charset=UTF-8"
        headers["Host"] = parsed_base.netloc
        
        sorted_keys = sorted(params.keys())
        query_str = "&".join([f"{k}={params[k]}" for k in sorted_keys])
        sig_url = f"{url}?{query_str}"

        headers["x-tr-signature"] = generate_tr_signature(method, sig_url, body_str, timestamp=timestamp)
        
        if body_str:
            headers["Content-Length"] = str(len(body_str))
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params, 
                data=body_str if method.upper() in ["POST", "PUT"] else None,
                headers=headers,
                timeout=kwargs.get("timeout", 15)
            )

            # --- SMART PATH HEALING ---
            # If we get a 404, we might be using the wrong prefix for this specific edge node
            if response.status_code == 404 or "404 page not found" in response.text:
                alt_endpoint = ""
                if "/wefeed-mobile-bff" in endpoint:
                    alt_endpoint = endpoint.replace("/wefeed-mobile-bff", "")
                else:
                    alt_endpoint = "/wefeed-mobile-bff" + endpoint
                
                if alt_endpoint:
                    logger.info(f"Retrying with HEALED path: {alt_endpoint}")
                    url_alt = f"{self.BASE_URL}{alt_endpoint}"
                    headers_alt = headers.copy()
                    
                    # Re-sign for the new URL
                    sorted_keys = sorted(params.keys())
                    query_str_alt = "&".join([f"{k}={params[k]}" for k in sorted_keys])
                    headers_alt["x-tr-signature"] = generate_tr_signature(method, f"{url_alt}?{query_str_alt}", body_str, timestamp=timestamp)
                    
                    response = self.session.request(
                        method=method,
                        url=url_alt,
                        params=params,
                        data=body_str if method.upper() in ["POST", "PUT"] else None,
                        headers=headers_alt,
                        timeout=kwargs.get("timeout", 15)
                    )
            
            # Dynamic Token Refresh via x-user header (allocates guest/refreshed tokens)
            x_user = None
            for k, v in response.headers.items():
                if k.lower() == 'x-user':
                    x_user = v
                    break
            if x_user:
                try:
                    user_data = json.loads(x_user)
                    token = user_data.get("token")
                    user_id = user_data.get("userId")
                    if token:
                        logger.info(f"Dynamically updated session token from response header: {token[:30]}... UID: {user_id}")
                        self.auth.update_session(token, user_id, user_data)
                except Exception as ex:
                    logger.error(f"Failed to parse x-user header: {ex}")

            # Gracefully handle non-JSON responses (e.g. "ok")
            try:
                return response.json()
            except json.JSONDecodeError:
                text = response.text
                logger.error(f"Failed to decode JSON from {endpoint}. Status: {response.status_code}. Text: {text[:500]}")
                if text.lower() == "ok":
                    return {"code": 0, "msg": "ok", "data": {}}
                return {"code": 1, "msg": f"Server Error: {text[:50]}", "data": {}}

        except Exception as e:
            logger.error(f"Request exception: {e}")
            return {"code": 500, "msg": str(e)}
