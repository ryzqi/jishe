import pydantic
from typing import Optional, Any


class CreateOrDeleteDeviceInGroup(pydantic.BaseModel):
    """管理设备组中的设备"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
    )
    group_id: Optional[str] = (
        None  # **参数说明**：设备组ID，用于唯一标识一个设备组，在创建设备组时由物联网平台分配。 **取值范围**：长度不超过36，十六进制字符串和连接符（-）的组合
    )
    action_id: Optional[str] = (
        None  # **参数说明**：操作类型，支持添加设备和删除设备。 **取值范围**： - addDevice: 添加设备。添加已注册的设备到指定的设备组中。 - removeDevice: 删除设备。从指定的设备组中删除设备，只是解除了设备和设备组的关系，该设备在平台仍然存在。
    )
    device_id: Optional[str] = (
        None  # **参数说明**：设备ID，用于唯一标识一个设备。在注册设备时直接指定，或者由物联网平台分配获得。由物联网平台分配时，生成规则为"product_id" + "_" + "node_id"拼接而成。 **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
    )


class AddApplication(pydantic.BaseModel):
    """创建资源空间"""

    app_name: str  # 应用名称


class DeleteApplication(pydantic.BaseModel):
    """删除资源空间"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。
    )
    app_id: Optional[str] = (
        None  # **参数说明**：资源空间ID，唯一标识一个资源空间，由物联网平台在创建资源空间时分配。资源空间对应的是物联网平台原有的应用，在物联网平台的含义与应用一致，只是变更了名称。 **取值范围**：长度不超过36，只允许字母、数字、下划线（_）、连接符（-）的组合。
    )


class ShowApplications(pydantic.BaseModel):
    """查询资源空间列表"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。
    )
    default_app: Optional[bool] = (
        None  # **参数说明**：默认资源空间标识，不携带则查询所有资源空间。 **取值范围**： - true：查询默认资源空间。 - false：查询非默认资源空间。
    )


class UpdateApplication(pydantic.BaseModel):
    """更新资源空间"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。
    )
    app_id: Optional[str] = (
        None  # **参数说明**：资源空间ID，唯一标识一个资源空间，由物联网平台在创建资源空间时分配。资源空间对应的是物联网平台原有的应用，在物联网平台的含义与应用一致，只是变更了名称。 **取值范围**：长度不超过36，只允许字母、数字、下划线（_）、连接符（-）的组合。
    )
    body: Optional[Any] = (
        None  # 请求体 (类型: huaweicloudsdkiotda.v5.UpdateApplicationDTO)
    )


class CreateAsyncCommand(pydantic.BaseModel):
    """下发异步设备命令"""

    device_id: Optional[str] = (
        None  # **参数说明**：下发命令的设备ID，用于唯一标识一个设备，在注册设备时由物联网平台分配获得。 **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
    )
    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，建议携带该参数，在使用专业版时必须携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID...
    )
    body: Optional[Any] = (
        None  # 请求体 (类型: huaweicloudsdkiotda.v5.AsyncDeviceCommandRequest)
    )


class AddDeviceGroup(pydantic.BaseModel):
    """添加设备组"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
    )
    body: Optional[Any] = (
        None  # 请求体 (类型: huaweicloudsdkiotda.v5.AddDeviceGroupDTO)
    )


class DeleteDeviceGroup(pydantic.BaseModel):
    """删除设备组"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
    )
    group_id: Optional[str] = (
        None  # **参数说明**：设备组ID，用于唯一标识一个设备组，在创建设备组时由物联网平台分配。 **取值范围**：长度不超过36，十六进制字符串和连接符（-）的组合。
    )


class UpdateDeviceGroup(pydantic.BaseModel):
    """修改设备组"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
    )
    group_id: Optional[str] = (
        None  # **参数说明**：设备组ID，用于唯一标识一个设备组，在创建设备组时由物联网平台分配。 **取值范围**：长度不超过36，十六进制字符串和连接符（-）的组合。
    )
    body: Optional[Any] = (
        None  # 请求体 (类型: huaweicloudsdkiotda.v5.UpdateDeviceGroupDTO)
    )


class AddDevice(pydantic.BaseModel):
    """添加设备"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
    )
    body: Optional[Any] = None  # 请求体 (类型: huaweicloudsdkiotda.v5.AddDevice)


class DeleteDevice(pydantic.BaseModel):
    """删除设备"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
    )
    device_id: Optional[str] = (
        None  # **参数说明**：设备ID，用于唯一标识一个设备... **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
    )


class UpdateDevice(pydantic.BaseModel):
    """修改设备"""

    instance_id: Optional[str] = (
        None  # **参数说明**：实例ID。物理多租下各实例的唯一标识，一般华为云租户无需携带该参数，仅在物理多租场景下从管理面访问API时需要携带该参数。您可以在IoTDA管理控制台界面，选择左侧导航栏“总览”页签查看当前实例的ID
    )
    device_id: Optional[str] = (
        None  # **参数说明**：设备ID，用于唯一标识一个设备... **取值范围**：长度不超过128，只允许字母、数字、下划线（_）、连接符（-）的组合。
    )
    body: Optional[Any] = None  # 请求体 (类型: huaweicloudsdkiotda.v5.UpdateDeviceDTO)
