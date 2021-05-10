from datetime import datetime, timedelta
from airflow import DAG
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
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
dag = DAG(dag_id='k8s-example-1',
          description='k8s-pod-operator example',
          tags=['example', 'k8s-pod-operator'],
          is_paused_upon_creation=True,
          catchup=False,
          schedule_interval='*/2 * * * *',
          max_active_runs=1,
          default_args=dag_default_args)

# This section defines default_env_vars configuration
default_env_vars = {}

# This sections defines configuration for init_container, volume and commands
mount_path = "/tmp/mnt"
init_container_image = "ubuntu:latest"
default_shared_resource_requirements = k8s.V1ResourceRequirements(
    limits={
        'memory': '1Gi',
        'cpu': '500m',
    })
volume_name = "shared-volume"
volume = k8s.V1Volume(name=volume_name,
                      empty_dir=k8s.V1EmptyDirVolumeSource(medium=""))
volume_mount = k8s.V1VolumeMount(name=volume_name,
                                 mount_path=mount_path,
                                 sub_path=None,
                                 read_only=False)
init_container = k8s.V1Container(
    name="init-container",
    image=init_container_image,
    volume_mounts=[volume_mount],
    command=["bash", "-cx"],
    args=[f"echo hello > {mount_path}/hello.txt"],
    resources=default_shared_resource_requirements)
job_name = "k8s-job"

# This section defines KubernetesPodOperator
t_1 = KubernetesPodOperator(namespace="airflow",
                            image="ubuntu:latest",
                            cmds=["bash", "-cx"],
                            arguments=[f"cat {mount_path}/hello.txt"],
                            name=job_name,
                            is_delete_operator_pod=True,
                            hostnetwork=False,
                            startup_timeout_seconds=1000,
                            volumes=[volume],
                            init_containers=[init_container],
                            volume_mounts=[volume_mount],
                            resources=default_shared_resource_requirements,
                            get_logs=True,
                            task_id=job_name,
                            dag=dag)
