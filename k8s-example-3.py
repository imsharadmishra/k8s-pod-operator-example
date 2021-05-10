from datetime import datetime, timedelta
from airflow import DAG
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
import uuid

# This section defines default configuration for DAG
dag_default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2021, 5, 6, 12, 40)
}

# This section defines DAG configuration
dag = DAG(dag_id='k8s-example-3',
          description='k8s-pod-operator example',
          tags=['k8s-pod-operator','example'],
          is_paused_upon_creation=True,
          catchup=False,
          schedule_interval='*/2 * * * *',
          max_active_runs=1,
          default_args=dag_default_args)

# This section defines default_env_vars configuration
default_env_vars = {}
default_shared_resource_requirements = k8s.V1ResourceRequirements(
    limits={
        'memory': '500Mi',
        'cpu': '500m',
    })
job_name = "k8s-job"
meta_name = 'k8s-job-' + uuid.uuid4().hex
mount_path = "/tmp/mnt"
metadata = k8s.V1ObjectMeta(name=(meta_name))
volume_name = "shared-volume"
volume = k8s.V1Volume(name=volume_name,
                      empty_dir=k8s.V1EmptyDirVolumeSource(medium=""))
volume_mount = k8s.V1VolumeMount(name=volume_name,
                                 mount_path=mount_path,
                                 sub_path=None,
                                 read_only=False)
full_pod_spec = k8s.V1Pod(
    metadata=metadata,
    spec=k8s.V1PodSpec(containers=[
        k8s.V1Container(
            name="base",
            resources=default_shared_resource_requirements,
            image="centos:latest",
        )
    ], ))

# This section defines KubernetesPodOperator
t_1 = KubernetesPodOperator(
    namespace="airflow",
    ports=[k8s.V1ContainerPort(name='http', container_port=80)],
    name=job_name,
    is_delete_operator_pod=False,
    hostnetwork=False,
    startup_timeout_seconds=1000,
    resources=default_shared_resource_requirements,
    get_logs=True,
    task_id=job_name,
    full_pod_spec=full_pod_spec,
    pod_template_file="/opt/airflow/dags/pod_template_file_example.yaml",
    dag=dag)
