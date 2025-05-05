from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger
from core.security import get_current_user
from crud import iodta
from schemas import iodta as iodta_schemas


router = APIRouter()


@router.get("/list_devices", summary="获取设备列表")
async def list_devices(
    instance_id: str | None = Query(None, description="实例ID"),
    product_id: str | None = Query(None, description="产品ID"),
    gateway_id: str | None = Query(None, description="网关ID"),
    is_cascade_query: bool | None = Query(None, description="是否级联查询"),
    node_id: str | None = Query(None, description="节点ID"),
    device_name: str | None = Query(None, description="设备名称"),
    limit: int | None = Query(None, description="分页大小"),
    marker: str | None = Query(None, description="分页标记"),
    offset: int | None = Query(None, description="偏移量"),
    start_time: str | None = Query(None, description="开始时间"),
    end_time: str | None = Query(None, description="结束时间"),
    app_id: str | None = Query(None, description="应用ID"),
    user: str = Depends(get_current_user),
):
    devices = await iodta.list_devices(
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
        app_id=app_id,
    )
    if not devices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No devices found",
        )
    return devices


@router.post("/create_or_delete_device", summary="管理设备组中的设备")
async def create_or_delete_device(
    body: iodta_schemas.CreateOrDeleteDeviceInGroup,
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.create_or_delete_device(body)
        return result
    except Exception as e:
        logger.error(f"Error managing device group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.post("/add_application", summary="创建资源空间")
async def add_application(
    body: iodta_schemas.AddApplication, user: str = Depends(get_current_user)
):
    try:
        result = await iodta.add_application(body.app_name)
        return result
    except Exception as e:
        logger.error(f"Error adding application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.delete("/delete_application", summary="删除资源空间")
async def delete_application(
    body: iodta_schemas.DeleteApplication,
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.delete_application(
            instance_id=body.instance_id, app_id=body.app_id
        )
        return result
    except Exception as e:
        logger.error(f"Error deleting application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/show_application", summary="查询资源空间")
async def show_application(
    instance_id: str = Query(..., description="实例ID"),
    app_id: str = Query(..., description="应用ID"),
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.show_application(instance_id=instance_id, app_id=app_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )
        return result
    except HTTPException as httpe:
        raise httpe
    except Exception as e:
        logger.error(f"Error showing application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/show_applications", summary="查询资源空间列表")
async def show_applications(
    instance_id: str = Query(..., description="实例ID"),
    default_app: bool | None = Query(None, description="是否查询默认应用"),
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.show_applications(
            instance_id=instance_id, default_app=default_app
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No applications found",
            )
        return result
    except HTTPException as httpe:
        raise httpe
    except Exception as e:
        logger.error(f"Error showing applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.put("/update_application", summary="更新资源空间")
async def update_application(
    body: iodta_schemas.UpdateApplication,
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.update_application(
            app_id=body.app_id,
            instance_id=body.instance_id,
            body=body.body,
        )
        return result
    except Exception as e:
        logger.error(f"Error updating application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.post("/create_async_command", summary="下发异步设备命令")
async def create_async_command(
    body: iodta_schemas.CreateAsyncCommand,
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.create_async_command(
            device_id=body.device_id,
            instance_id=body.instance_id,
            body=body.body,
        )
        return result
    except Exception as e:
        logger.error(f"Error creating async command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/list_async_commands", summary="查询设备下队列中的命令")
async def list_async_commands(
    device_id: str = Query(..., description="设备ID"),
    instance_id: str = Query(..., description="实例ID"),
    limit: int | None = Query(None, description="分页大小"),
    marker: str | None = Query(None, description="分页标记"),
    offset: int | None = Query(None, description="偏移量"),
    start_time: str | None = Query(None, description="开始时间"),
    end_time: str | None = Query(None, description="结束时间"),
    status: str | None = Query(None, description="命令状态"),
    command_name: str | None = Query(None, description="命令名称"),
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.list_async_commands(
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
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No async commands found",
            )
        return result
    except HTTPException as httpe:
        raise httpe
    except Exception as e:
        logger.error(f"Error listing async commands: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.post("/add_device_group", summary="添加设备组")
async def add_device_group(
    body: iodta_schemas.AddDeviceGroup, user: str = Depends(get_current_user)
):
    try:
        result = await iodta.add_device_group(
            instance_id=body.instance_id,
            body=body.body,
        )
        return result
    except Exception as e:
        logger.error(f"Error adding device group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.delete("/delete_device_group", summary="删除设备组")
async def delete_device_group(
    body: iodta_schemas.DeleteDeviceGroup,
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.delete_device_group(
            instance_id=body.instance_id, group_id=body.group_id
        )
        return result
    except Exception as e:
        logger.error(f"Error deleting device group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/list_device_groups", summary="查询设备组列表")
async def list_device_groups(
    instance_id: str = Query(..., description="实例ID"),
    limit: int | None = Query(None, description="分页大小"),
    marker: str | None = Query(None, description="分页标记"),
    offset: int | None = Query(None, description="偏移量"),
    last_modified_time: str | None = Query(None, description="最后修改时间过滤"),
    app_id: str | None = Query(None, description="应用ID过滤"),
    group_type: str | None = Query(None, description="设备组类型过滤"),
    name: str | None = Query(None, description="设备组名称过滤"),
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.list_device_groups(
            instance_id=instance_id,
            limit=limit,
            marker=marker,
            offset=offset,
            last_modified_time=last_modified_time,
            app_id=app_id,
            group_type=group_type,
            name=name,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No device groups found",
            )
        return result
    except HTTPException as httpe:
        raise httpe
    except Exception as e:
        logger.error(f"Error listing device groups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/show_devices_in_group", summary="查询设备组设备列表")
async def show_devices_in_group(
    instance_id: str = Query(..., description="实例ID"),
    group_id: str = Query(..., description="设备组ID"),
    limit: int | None = Query(None, description="分页大小"),
    marker: str | None = Query(None, description="分页标记"),
    offset: int | None = Query(None, description="偏移量"),
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.show_devices_in_group(
            instance_id=instance_id,
            group_id=group_id,
            limit=limit,
            marker=marker,
            offset=offset,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No devices found in group",
            )
        return result
    except HTTPException as httpe:
        raise httpe
    except Exception as e:
        logger.error(f"Error showing devices in group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.put("/update_device_group", summary="修改设备组")
async def update_device_group(
    body: iodta_schemas.UpdateDeviceGroup,
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.update_device_group(
            group_id=body.group_id,
            instance_id=body.instance_id,
            body=body.body,
        )
        return result
    except Exception as e:
        logger.error(f"Error updating device group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.post("/add_device", summary="添加设备")
async def add_device(
    body: iodta_schemas.AddDevice, user: str = Depends(get_current_user)
):
    try:
        result = await iodta.add_device(instance_id=body.instance_id, body=body.body)
        return result
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.delete("/delete_device", summary="删除设备")
async def delete_device(
    body: iodta_schemas.DeleteDevice,
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.delete_device(
            instance_id=body.instance_id, device_id=body.device_id
        )
        return result
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/show_device", summary="查询设备")
async def show_device(
    instance_id: str = Query(..., description="实例ID"),
    device_id: str = Query(..., description="设备ID"),
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.show_device(instance_id=instance_id, device_id=device_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found",
            )
        return result
    except HTTPException as httpe:
        raise httpe
    except Exception as e:
        logger.error(f"Error showing device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.put("/update_device", summary="修改设备")
async def update_device(
    body: iodta_schemas.UpdateDevice,
    user: str = Depends(get_current_user),
):
    try:
        result = await iodta.update_device(
            device_id=body.device_id,
            instance_id=body.instance_id,
            body=body.body,
        )
        return result
    except Exception as e:
        logger.error(f"Error updating device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
