"""
This is an example dag for using the KubernetesPodOperator.
"""

from kubernetes.client import models as k8s
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator

default_args = {
    'owner': 'airflow'
}

with DAG(
    dag_id='k8s-example-0',
    default_args=default_args,
    schedule_interval="*/5 * * * *",
    start_date=days_ago(2),
    catchup=False,
    tags=['k8s-pod-operator','example'],
) as dag:
    k = KubernetesPodOperator(
        namespace='airflow',
        image="ubuntu:latest",
        cmds=["bash", "-cx"],
        arguments=["echo hello"],
        name="k8s-pod",
        task_id="task",
        is_delete_operator_pod=True,
        hostnetwork=False,
        startup_timeout_seconds=1000
    )