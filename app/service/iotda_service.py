from huaweicloudsdkcore.region.region import Region
from huaweicloudsdkiotda.v5 import IoTDAAsyncClient
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from core.config import settings


ak = settings.HUAWEICLOUD_SDK_AK
sk = settings.HUAWEICLOUD_SDK_SK
project_id = "8b086955-1e5d-45f7-ab7b-1a54fdbf5e68"
region_id = "cn-north-4"
endpoint = "2f6dd797a9.st1.iotda-app.cn-north-4.myhuaweicloud.com"

REGION = Region(region_id, endpoint)

# 创建认证
# 创建BasicCredentials实例并初始化
credentials = BasicCredentials(ak, sk, project_id)

client = (
    IoTDAAsyncClient.new_builder()
    .with_credentials(credentials)
    .with_region(REGION)
    .build()
)
