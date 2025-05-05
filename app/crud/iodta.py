from service.iotda_service import client
from huaweicloudsdkcore.exceptions import exceptions

from loguru import logger
from huaweicloudsdkiotda.v5 import (
    ListDevicesRequest,
    CreateOrDeleteDeviceInGroupRequest,
    AddApplicationRequest,
    DeleteApplicationRequest,
    ShowApplicationRequest,
    ShowApplicationsRequest,
    UpdateApplicationRequest,
    CreateAsyncCommandRequest,
    ListAsyncCommandsRequest,
    AddDeviceGroupRequest,
    DeleteDeviceGroupRequest,
    ListDeviceGroupsRequest,
    ShowDevicesInGroupRequest,
    UpdateDeviceGroupRequest,
    AddDeviceRequest,
    DeleteDeviceRequest,
    ShowDeviceRequest,
    UpdateDeviceRequest,
)


async def list_devices(
    instance_id=None,
    product_id=None,
    gateway_id=None,
    is_cascade_query=None,
    node_id=None,
    device_name=None,
    limit=None,
    marker=None,
    offset=None,
    start_time=None,
    end_time=None,
    app_id=None,
):
    try:
        # 实例化请求对象
        request = ListDevicesRequest(
            instance_id=instance_id,
            product_id=product_id,
            gateway_id=gateway_id,
            is_cascade_query=is_cascade_query,
            node_id=node_id,
            device_name=device_name,
            limit=limit,
            marker=marker,
            offset=offset,
            start_time=start_time,
            end_time=end_time,
            app_id=app_id
        )
        # 调用查询设备列表接口
        response = client.list_devices_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def create_or_delete_device(
    instance_id=None, group_id=None, action_id=None, device_id=None
):
    """
    管理设备组中的设备

    应用服务器可调用此接口管理设备组中的设备。单个设备组内最多添加20,000个设备，一个设备最多可以被添加到10个设备组中。
    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
    :type instance_id: str
    :param group_id: **参数说明**：设备组ID，用于唯一标识一个设备组，在创建设备组时由物联网平台分配。 **取值范围**：长度不超过36，十六进制字符串和连接符（-）的组合
    :type group_id: str
    :param action_id: **参数说明**：操作类型，支持添加设备和删除设备。 **取值范围**： - addDevice: 添加设备。添加已注册的设备到指定的设备组中。 - removeDevice: 删除设备。从指定的设备组中删除设备，只是解除了设备和设备组的关系，该设备在平台仍然存在。
    :type action_id: str
    :param device_id: **参数说明**：设备ID，用于唯一标识一个设备。在注册设备时直接指定，或者由物联网平台分配获得。由物联网平台分配时，生成规则为\&quot;product_id\&quot; + \&quot;_\&quot; + \&quot;node_id\&quot;拼接而成。 **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
    :type device_id: str
    """
    try:
        request = CreateOrDeleteDeviceInGroupRequest(
            instance_id=instance_id,
            group_id=group_id,
            action_id=action_id,
            device_id=device_id,
        )
        response = client.create_or_delete_device_in_group_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def add_application(app_name: str):
    """
    创建资源空间
    """
    try:
        request = AddApplicationRequest(app_name=app_name)
        response = client.add_application_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def delete_application(instance_id=None, app_id=None):
    """
    删除资源空间
    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。
    :type instance_id: str
    :param app_id: **参数说明**：资源空间ID，唯一标识一个资源空间，由物联网平台在创建资源空间时分配。资源空间对应的是物联网平台原有的应用，在物联网平台的含义与应用一致，只是变更了名称。 **取值范围**：长度不超过36，只允许字母、数字、下划线（_）、连接符（-）的组合。
    :type app_id: str
    """
    try:
        request = DeleteApplicationRequest(instance_id=instance_id, app_id=app_id)
        response = client.delete_application_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def show_application(instance_id=None, app_id=None):
    """
    查询资源空间

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。
    :type instance_id: str
    :param app_id: **参数说明**：资源空间ID，唯一标识一个资源空间，由物联网平台在创建资源空间时分配。资源空间对应的是物联网平台原有的应用，在物联网平台的含义与应用一致，只是变更了名称。 **取值范围**：长度不超过36，只允许字母、数字、下划线（_）、连接符（-）的组合。
    :type app_id: str
    """
    try:
        request = ShowApplicationRequest(instance_id=instance_id, app_id=app_id)
        response = client.show_application_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def show_applications(instance_id=None, default_app=None):
    """
    查询资源空间列表

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。
    :type instance_id: str
    :param default_app: **参数说明**：默认资源空间标识，不携带则查询所有资源空间。 **取值范围**： - true：查询默认资源空间。 - false：查询非默认资源空间。
    :type default_app: bool
    """
    try:
        request = ShowApplicationsRequest(
            instance_id=instance_id, default_app=default_app
        )
        response = client.show_applications_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def update_application(instance_id=None, app_id=None, body=None):
    """
    更新资源空间

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。
    :type instance_id: str
    :param app_id: **参数说明**：资源空间ID，唯一标识一个资源空间，由物联网平台在创建资源空间时分配。资源空间对应的是物联网平台原有的应用，在物联网平台的含义与应用一致，只是变更了名称。 **取值范围**：长度不超过36，只允许字母、数字、下划线（_）、连接符（-）的组合。
    :type app_id: str
    :param body: Body of the UpdateApplicationRequest
    :type body: :class:`huaweicloudsdkiotda.v5.UpdateApplicationDTO`
    """
    try:
        request = UpdateApplicationRequest(
            instance_id=instance_id, app_id=app_id, body=body
        )
        response = client.update_application_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def create_async_command(device_id=None, instance_id=None, body=None):
    """
    下发异步设备命令

    :param device_id: **参数说明**：下发命令的设备ID，用于唯一标识一个设备，在注册设备时由物联网平台分配获得。 **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
    :type device_id: str
    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，建议携带该参数，在使用专业版时必须携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID，具体获取方式请参考[[查看实例详情](https://support.huaweicloud.com/usermanual-iothub/iot_01_0079.html#section1)](tag:hws) [[查看实例详情](https://support.huaweicloud.com/intl/zh-cn/usermanual-iothub/iot_01_0079.html#section1)](tag:hws_hk)。
    :type instance_id: str
    :param body: Body of the CreateAsyncCommandRequest
    :type body: :class:`huaweicloudsdkiotda.v5.AsyncDeviceCommandRequest`
    """

    try:
        request = CreateAsyncCommandRequest(
            device_id=device_id, instance_id=instance_id, body=body
        )
        response = client.create_async_command_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def list_async_commands(
    device_id=None,
    instance_id=None,
    limit=None,
    marker=None,
    offset=None,
    start_time=None,
    end_time=None,
    status=None,
    command_name=None,
):
    """
    查询设备下队列中的命令

    :param device_id: **参数说明**：下发命令的设备ID，用于唯一标识一个设备，在注册设备时由物联网平台分配获得。 **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
        :type device_id: str
        :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，建议携带该参数，在使用专业版时必须携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID，具体获取方式请参考[[查看实例详情](https://support.huaweicloud.com/usermanual-iothub/iot_01_0079.html#section1)](tag:hws) [[查看实例详情](https://support.huaweicloud.com/intl/zh-cn/usermanual-iothub/iot_01_0079.html#section1)](tag:hws_hk)。
        :type instance_id: str
        :param limit: **参数说明**：分页查询时每页显示的记录数，默认值为10，取值范围为1-50的整数。
        :type limit: int
        :param marker: **参数说明**：上一次分页查询结果中最后一条记录的ID，在上一次分页查询时由物联网平台返回获得。分页查询时物联网平台是按marker也就是记录ID降序查询的，越新的数据记录ID也会越大。若填写marker，则本次只查询记录ID小于marker的数据记录。若不填写，则从记录ID最大也就是最新的一条数据开始查询。如果需要依次查询所有数据，则每次查询时必须填写上一次查询响应中的marker值。
        :type marker: str
        :param offset: **参数说明**：表示从marker后偏移offset条记录开始查询。默认为0，取值范围为0-500的整数。当offset为0时，表示从marker后第一条记录开始输出。限制offset最大值是出于API性能考虑，您可以搭配marker使用该参数实现翻页，例如每页50条记录，1-11页内都可以直接使用offset跳转到指定页，但到11页后，由于offset限制为500，您需要使用第11页返回的marker作为下次查询的marker，以实现翻页到12-22页。
        :type offset: int
        :param start_time: **参数说明**：查询命令下发时间在startTime之后的记录，格式：yyyyMMdd&#39;T&#39;HHmmss&#39;Z&#39;，如20151212T121212Z。
        :type start_time: str
        :param end_time: **参数说明**：查询命令下发时间在endTime之前的记录，格式：yyyyMMdd&#39;T&#39;HHmmss&#39;Z&#39;，如20151212T121212Z。
        :type end_time: str
        :param status: **参数说明**：命令状态。
        :type status: str
        :param command_name: **参数说明**：命令名称。
        :type command_name: str
    """
    try:
        request = ListAsyncCommandsRequest(
            device_id=device_id,
            instance_id=instance_id,
            limit=limit,
            marker=marker,
            offset=offset,
            start_time=start_time,
            end_time=end_time,
            status=status,
            command_name=command_name,
        )
        response = client.list_async_commands_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def add_device_group(instance_id=None, body=None):
    """
    添加设备组

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
        :type instance_id: str
        :param body: Body of the AddDeviceGroupRequest
        :type body: :class:`huaweicloudsdkiotda.v5.AddDeviceGroupDTO`
    """

    try:
        request = AddDeviceGroupRequest(instance_id=instance_id, body=body)
        response = client.add_device_group_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def delete_device_group(instance_id=None, group_id=None):
    """
    删除设备组

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
        :type instance_id: str
        :param group_id: **参数说明**：设备组ID，用于唯一标识一个设备组，在创建设备组时由物联网平台分配。 **取值范围**：长度不超过36，十六进制字符串和连接符（-）的组合。
        :type group_id: str
    """
    try:
        request = DeleteDeviceGroupRequest(instance_id=instance_id, group_id=group_id)
        response = client.delete_device_group_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def list_device_groups(
    instance_id=None,
    limit=None,
    marker=None,
    offset=None,
    last_modified_time=None,
    app_id=None,
    group_type=None,
    name=None,
):
    """
    查询设备组列表

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
        :type instance_id: str
        :param limit: **参数说明**：分页查询时每页显示的记录数。 **取值范围**：1-50的整数，默认值为10。
        :type limit: int
        :param marker: **参数说明**：上一次分页查询结果中最后一条记录的ID，在上一次分页查询时由物联网平台返回获得。分页查询时物联网平台是按marker也就是记录ID降序查询的，越新的数据记录ID也会越大。若填写marker，则本次只查询记录ID小于marker的数据记录。若不填写，则从记录ID最大也就是最新的一条数据开始查询。如果需要依次查询所有数据，则每次查询时必须填写上一次查询响应中的marker值。 **取值范围**：长度为24的十六进制字符串，默认值为ffffffffffffffffffffffff。
        :type marker: str
        :param offset: **参数说明**：表示从marker后偏移offset条记录开始查询。当offset为0时，表示从marker后第一条记录开始输出。限制offset最大值是出于API性能考虑，您可以搭配marker使用该参数实现翻页，例如每页50条记录，1-11页内都可以直接使用offset跳转到指定页，但到11页后，由于offset限制为500，您需要使用第11页返回的marker作为下次查询的marker，以实现翻页到12-22页。 **取值范围**：0-500的整数，默认为0。
        :type offset: int
        :param last_modified_time: **参数说明**：查询设备组在last_modified_time之后修改的记录。 **取值范围**：格式为yyyyMMdd&#39;T&#39;HHmmss&#39;Z&#39;，如20151212T121212Z。
        :type last_modified_time: str
        :param app_id: **参数说明**：资源空间ID。此参数为非必选参数，存在多资源空间的用户需要使用该接口时，可以携带该参数查询指定资源空间下的产品列表，不携带该参数则会查询该用户下所有产品列表。 **取值范围**：长度不超过36，只允许字母、数字、下划线（_）、连接符（-）的组合。
        :type app_id: str
        :param group_type: **参数说明**：设备组类型，默认为静态设备组；当设备组类型为动态设备组时，需要填写动态设备组规则
        :type group_type: str
        :param name: **参数说明**：设备组名称，单个资源空间下不可重复。 **取值范围**：长度不超过64，只允许中文、字母、数字、以及_? &#39;#().,&amp;%@!-等字符的组合。
        :type name: str
    """
    try:
        request = ListDeviceGroupsRequest(
            instance_id=instance_id,
            limit=limit,
            marker=marker,
            offset=offset,
            last_modified_time=last_modified_time,
            app_id=app_id,
            group_type=group_type,
            name=name,
        )
        response = client.list_device_groups_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def show_devices_in_group(
    instance_id=None, group_id=None, limit=None, marker=None, offset=None
):
    """
    查询设备组设备列表

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
        :type instance_id: str
        :param group_id: **参数说明**：设备组ID，用于唯一标识一个设备组，在创建设备组时由物联网平台分配。 **取值范围**：长度不超过36，十六进制字符串和连接符（-）的组合。
        :type group_id: str
        :param limit: **参数说明**：分页查询时每页显示的记录数。 **取值范围**：1-50的整数，默认值为10。
        :type limit: int
        :param marker: **参数说明**：上一次分页查询结果中最后一条记录的ID，在上一次分页查询时由物联网平台返回获得。分页查询时物联网平台是按marker也就是记录ID降序查询的，越新的数据记录ID也会越大。若填写marker，则本次只查询记录ID小于marker的数据记录。若不填写，则从记录ID最大也就是最新的一条数据开始查询。如果需要依次查询所有数据，则每次查询时必须填写上一次查询响应中的marker值。 **取值范围**：长度为24的十六进制字符串，默认值为ffffffffffffffffffffffff。
        :type marker: str
        :param offset: **参数说明**：表示从marker后偏移offset条记录开始查询。当offset为0时，表示从marker后第一条记录开始输出。限制offset最大值是出于API性能考虑，您可以搭配marker使用该参数实现翻页，例如每页50条记录，1-11页内都可以直接使用offset跳转到指定页，但到11页后，由于offset限制为500，您需要使用第11页返回的marker作为下次查询的marker，以实现翻页到12-22页。 **取值范围**：0-500的整数，默认为0。
        :type offset: int
    """
    try:
        request = ShowDevicesInGroupRequest(
            instance_id=instance_id,
            group_id=group_id,
            limit=limit,
            marker=marker,
            offset=offset,
        )
        response = client.show_devices_in_group_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def update_device_group(instance_id=None, group_id=None, body=None):
    """
    修改设备组

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
        :type instance_id: str
        :param group_id: **参数说明**：设备组ID，用于唯一标识一个设备组，在创建设备组时由物联网平台分配。 **取值范围**：长度不超过36，十六进制字符串和连接符（-）的组合。
        :type group_id: str
        :param body: Body of the UpdateDeviceGroupRequest
        :type body: :class:`huaweicloudsdkiotda.v5.UpdateDeviceGroupDTO`
    """

    try:
        request = UpdateDeviceGroupRequest(
            instance_id=instance_id, group_id=group_id, body=body
        )
        response = client.update_device_group_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def add_device(instance_id=None, body=None):
    """
    添加设备

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
        :type instance_id: str
        :param body: Body of the AddDeviceRequest
        :type body: :class:`huaweicloudsdkiotda.v5.AddDevice`
    """
    try:
        request = AddDeviceRequest(instance_id=instance_id, body=body)
        response = client.add_device_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def delete_device(instance_id=None, device_id=None):
    """
    删除设备

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
            :type instance_id: str
            :param device_id: **参数说明**：设备ID，用于唯一标识一个设备。在注册设备时直接指定，或者由物联网平台分配获得。由物联网平台分配时，生成规则\&quot;product_id\&quot; + \&quot;_\&quot; + \&quot;node_id\&quot;拼接而成。 **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
            :type device_id: str
    """
    try:
        request = DeleteDeviceRequest(instance_id=instance_id, device_id=device_id)
        response = client.delete_device_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def show_device(instance_id=None, device_id=None):
    """
    查询设备

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
        :type instance_id: str
        :param device_id: **参数说明**：设备ID，用于唯一标识一个设备。在注册设备时直接指定，或者由物联网平台分配获得。由物联网平台分配时，生成规则\&quot;product_id\&quot; + \&quot;_\&quot; + \&quot;node_id\&quot;拼接而成。 **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
        :type device_id: str
    """
    try:
        request = ShowDeviceRequest(instance_id=instance_id, device_id=device_id)
        response = client.show_device_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None


async def update_device(instance_id=None, device_id=None, body=None):
    """
    修改设备

    :param instance_id: **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
        :type instance_id: str
        :param device_id: **参数说明**：设备ID，用于唯一标识一个设备。在注册设备时直接指定，或者由物联网平台分配获得。由物联网平台分配时，生成规则\&quot;product_id\&quot; + \&quot;_\&quot; + \&quot;node_id\&quot;拼接而成。 **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
        :type device_id: str
        :param body: Body of the UpdateDeviceRequest
        :type body: :class:`huaweicloudsdkiotda.v5.UpdateDeviceDTO`
    """
    try:
        request = UpdateDeviceRequest(
            instance_id=instance_id, device_id=device_id, body=body
        )
        response = client.update_device_async(request)
        return response
    except exceptions.ClientRequestException as e:
        logger.error(
            f"状态码:{e.status_code}, 请求id:{e.request_id}, 错误信息:{e.error_msg}, 错误码:{e.error_code}"
        )
        return None
