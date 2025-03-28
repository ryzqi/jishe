import json
import requests  
from requests.exceptions import (
    RequestException,
    JSONDecodeError,
)  
from typing import Optional, Dict, Any, List
from app.core.config import settings



GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"
DIRECTIONS_URL = "https://restapi.amap.com/v5/direction/driving"  




def _geocode_tool_internal(
    address: str, city: Optional[str] = None
) -> Dict[str, float]:
    """Internal synchronous: gets coordinates, returns dict or empty dict."""
    params = {"key": settings.GAODE_API_KEY, "address": address, "output": "JSON"}
    if city:
        params["city"] = city
    location_result: Dict[str, float] = {}
    try:
        # 使用 requests.get 进行同步请求
        response = requests.get(GEOCODE_URL, params=params, timeout=10)  # 添加超时
        response.raise_for_status()  # 检查 HTTP 错误状态码
        result_data: Dict[str, Any] = response.json()  # 解析 JSON

        if result_data.get("status") != "1":
            print(
                f"高德地理编码 API 错误: status={result_data.get('status')}, info={result_data.get('info')} (地址: {address})"
            )
            return location_result

        geocodes_list = result_data.get("geocodes")
        if not isinstance(geocodes_list, list) or not geocodes_list:
            return location_result

        first_geocode = geocodes_list[0]
        if isinstance(first_geocode, dict):
            location_str = first_geocode.get("location")
            if isinstance(location_str, str) and "," in location_str:
                try:
                    parts = location_str.split(",")
                    if len(parts) == 2:
                        longitude = float(parts[0].strip())
                        latitude = float(parts[1].strip())
                        location_result = {
                            "longitude": longitude,
                            "latitude": latitude,
                        }
                except ValueError:
                    print(f"解析坐标时 ValueError: '{location_str}'")
                except Exception as parse_err:
                    print(f"解析坐标时未知错误: {parse_err}")

        return location_result
    # 捕获 requests 可能抛出的异常
    except RequestException as e:
        print(f"请求高德地理编码时网络错误 (地址: {address}): {e}")
        return location_result
    # requests.JSONDecodeError 继承自 json.JSONDecodeError, 但更明确
    except JSONDecodeError as e:
        print(f"解析高德地理编码响应 JSON 时出错 (地址: {address}): {e}")
        return location_result
    except Exception as e:
        print(f"处理地理编码时未知错误 (地址: '{address}'): {e}")
        return location_result


def _directions_tool_internal(
    origin: str,
    destination: str,
    waypoints: Optional[str] = None,
) -> Dict[str, Any]:
    """Internal synchronous: gets directions, returns dict."""
    params = {
        "key": settings.GAODE_API_KEY,
        "origin": origin,
        "destination": destination,
        "show_fields": "cost",  
    }
    if waypoints:
        params["waypoints"] = waypoints

    result_payload: Dict[str, Any] = {}
    try:
        # 使用 requests.get 进行同步请求
        response = requests.get(DIRECTIONS_URL, params=params, timeout=15)  # 增加超时
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "1" and data.get("infocode") == "10000":
            route = data.get("route", {})
            paths = route.get("paths", [])
            formatted_routes: List[Dict[str, Any]] = []
            path_list = paths  # 明确变量名
            if isinstance(path_list, list):
                for path in path_list:
                    cost_info = path.get("cost", {})
                    # 确保duration是数值类型再转换
                    duration_str = cost_info.get("duration", "0")
                    try:
                        duration_seconds = int(float(duration_str))
                    except (ValueError, TypeError):
                        duration_seconds = 0
                        print(
                            f"Warning: Invalid duration value received: {duration_str}"
                        )

                    # 确保distance是数值类型再转换
                    distance_str = path.get("distance", "0")
                    try:
                        distance_meters = int(distance_str)
                    except (ValueError, TypeError):
                        distance_meters = 0
                        print(
                            f"Warning: Invalid distance value received: {distance_str}"
                        )

                    route_info = {
                        "distance_meters": distance_meters,
                        "duration_minutes": duration_seconds // 60,
                        "instructions": [],
                    }
                    steps = path.get("steps", [])
                    if isinstance(steps, list):
                        for step in steps:
                            instruction = step.get("instruction")
                            if instruction:
                                route_info["instructions"].append(instruction)
                    formatted_routes.append(route_info)

            if formatted_routes:
                result_payload = {"routes": formatted_routes}
            else:
                # 如果API成功但没有路径，也返回明确信息
                result_payload = {
                    "info": data.get("info", "未找到符合条件的路线。")
                }  # 使用API返回的info（如果存在）
        else:
            # API 返回错误状态
            result_payload = {
                "error": "高德路线规划API返回错误",
                "status": data.get("status"),
                "info": data.get("info"),
                "infocode": data.get("infocode"),
            }

    except RequestException as e:
        # 更具体的错误分类（可选，但有帮助）
        error_type = "网络连接或请求错误"
        if isinstance(e, requests.exceptions.Timeout):
            error_type = "请求超时"
        elif isinstance(e, requests.exceptions.HTTPError):
            error_type = f"HTTP请求错误: {e.response.status_code}"

        result_payload = {"error": error_type, "message": str(e)}
    except JSONDecodeError:
        result_payload = {"error": "无法解析API响应内容 (非JSON格式)"}
    except Exception as e:
        result_payload = {"error": "处理路线规划时发生未知错误", "message": str(e)}

    return result_payload





def geocode_and_extract_locations(
    address: str, city: Optional[str] = None
) -> str:  # 返回值仍是 JSON 字符串
    """Gets the latitude and longitude coordinates for a given address using geocoding (synchronous).

    Uses the Amap Geocoding API internally. Returns an empty JSON object string
    if the address cannot be found or an error occurs.

    Args:
        address: The detailed address string to geocode,
            e.g., '北京市朝阳区阜通东大街6号'.
        city: The city name where the address is located, e.g., '北京'.
            Providing this can improve geocoding accuracy (optional). Defaults to None.

    Returns:
        A JSON string containing the geocoding results (typically including
        longitude and latitude) or an empty JSON object string '{}' on failure.
        Example success (content varies): '{"longitude": 116.481488, "latitude": 39.990464}'
        Example failure: '{}'
    """
    try:
        # 直接调用同步的内部函数，不再需要 http client session
        location_dict = _geocode_tool_internal(address=address, city=city)
        # 确保返回的是字典，即使是空的
        if not isinstance(location_dict, dict):
            print(
                f"Warning: _geocode_tool_internal did not return a dict. Received: {type(location_dict)}"
            )
            return "{}"  # 保持返回空 JSON 字符串的约定
        return json.dumps(location_dict)
    except Exception as e:
        # 这个顶级异常捕获现在主要处理 _geocode_tool_internal 内部未捕获的意外错误
        # 或者 json.dumps 可能遇到的极罕见错误（如循环引用，理论上这里不会发生）
        print(f"Error in geocode_and_extract_locations synchronous wrapper: {e}")
        return "{}"  # 返回空 JSON 字符串


def get_amap_driving_directions(
    origin: str,
    destination: str,
    waypoints: Optional[str] = None,
) -> str:  # 返回值仍是 JSON 字符串
    """Gets driving directions between two or more points using the Amap API (synchronous).

    Takes origin, destination, and optional waypoints as longitude,latitude strings
    and returns route information including distance, duration, and instructions.

    Args:
        origin: The starting point coordinates in "longitude,latitude" format
            (e.g., "116.481,39.989").
        destination: The ending point coordinates in "longitude,latitude" format
            (e.g., "116.405,39.904").
        waypoints: Intermediate points coordinates (optional). Format is
            "longitude,latitude". Multiple waypoints should be separated by
            semicolons ';', e.g., "116.41,39.92;116.42,39.93". Defaults to None.

    Returns:
        A JSON string representing the driving directions result or an error message.
        On success, the JSON string typically contains a 'routes' key:
        '{"routes": [{"distance_meters": int, "duration_minutes": int, "instructions": [str, ...]}]}'.
        On input validation failure or API error, the JSON string contains an
        'error' key: '{"error": "description", "message": "details..."}' or potentially
        other API-specific error formats like '{"info": "No routes found."}'.
    """

    # 参数验证逻辑保持不变
    def is_valid_lon_lat(coord: str) -> bool:
        if not isinstance(coord, str):  # 增加类型检查
            return False
        try:
            lon, lat = map(float, coord.split(","))
            return -180 <= lon <= 180 and -90 <= lat <= 90
        except (ValueError, TypeError):  # 捕获更具体的异常
            return False

    error_payload: Dict[str, str] = {}  # 指定类型
    if not is_valid_lon_lat(origin):
        error_payload = {
            "error": "参数格式错误",
            "message": "起点 'origin' 必须是 '经度,纬度' 格式的字符串。",
        }
    elif not is_valid_lon_lat(destination):
        error_payload = {
            "error": "参数格式错误",
            "message": "终点 'destination' 必须是 '经度,纬度' 格式的字符串。",
        }
    elif waypoints:
        if not isinstance(waypoints, str):
            error_payload = {
                "error": "参数格式错误",
                "message": "途经点 'waypoints' 必须是字符串（如果提供）。",
            }
        else:
            points = waypoints.split(";")
            if not all(
                is_valid_lon_lat(point) for point in points if point
            ):  # 检查所有非空路径点
                # 查找第一个无效点以提供更具体的错误消息
                invalid_point = next(
                    (p for p in points if p and not is_valid_lon_lat(p)), None
                )
                error_payload = {
                    "error": "参数格式错误",
                    "message": f"途经点 'waypoints' 中的 '{invalid_point or '一个点'}' 必须是 '经度,纬度' 格式，多个用 ';' 分隔。",
                }

    if error_payload:
        return json.dumps(error_payload)

    try:
        # 直接调用同步的内部函数
        result_dict = _directions_tool_internal(
            origin=origin,
            destination=destination,
            waypoints=waypoints,
        )
        # 确保返回的是字典
        if not isinstance(result_dict, dict):
            print(
                f"Warning: _directions_tool_internal did not return a dict. Received: {type(result_dict)}"
            )
            return json.dumps(
                {
                    "error": "内部处理错误",
                    "message": "从路线规划服务收到意外的数据格式。",
                }
            )
        return json.dumps(result_dict)
    except Exception as e:
        # 同样，这个顶级异常捕获处理包装器或 json.dumps 的意外错误
        print(f"Error in get_amap_driving_directions synchronous wrapper: {e}")
        return json.dumps(
            {
                "error": "内部服务器错误",
                "message": "处理路线规划请求时发生意外错误。",
            }
        )



