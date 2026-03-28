from celery_app import celery_app
import run_pipeline

@celery_app.task
def run_pipeline_task():
    run_pipeline.main()