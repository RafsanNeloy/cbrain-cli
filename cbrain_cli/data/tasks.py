import json

from cbrain_cli.cli_utils import (
    CbrainClient,
    CliValidationError,
    pagination,
)

# Names accepted by CBRAIN POST /tasks/operation
TASK_OPERATIONS = (
    "terminate",
    "archive",
    "archive_file",
    "unarchive",
    "zap_wd",
    "save_wd",
    "hold",
    "release",
    "suspend",
    "resume",
    "duplicate",
    "recover",
    "restart_setup",
    "restart_cluster",
    "restart_postprocess",
)


def list_tasks(args):
    """
    List all tasks from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag and optional bourreau_id filter

    Returns
    -------
    list
        List of task dictionaries
    """
    params = {}
    filter_name = getattr(args, "filter_name", None)
    bourreau_id = getattr(args, "bourreau_id", None)

    if filter_name is not None:
        if filter_name != "bourreau_id":
            raise CliValidationError(f"Unsupported filter: {filter_name}", field="filter_name")
        if bourreau_id is None:
            raise CliValidationError(
                "Bourreau ID is required when filter is bourreau-id",
                field="bourreau_id",
            )
        params["bourreau_id"] = str(bourreau_id)
    elif bourreau_id is not None:
        raise CliValidationError(
            "Filter bourreau-id is required when Bourreau ID is specified",
            field="filter_name",
        )

    params = pagination(args, params)
    return CbrainClient.from_credentials().get("/tasks", params=params)


def show_task(args):
    """
    Show detailed information about a specific task from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the task argument with task_id

    Returns
    -------
    dict
        Task details dictionary
    """
    task_id = getattr(args, "task", None)
    if not task_id:
        raise CliValidationError("Task ID is required", field="task")
    return CbrainClient.from_credentials().get(f"/tasks/{task_id}")


def operation_task(args):
    """
    Run a bulk operation on tasks.
    """
    operation = getattr(args, "operation", None)
    if not operation:
        raise CliValidationError("Operation is required", field="operation")
    if operation not in TASK_OPERATIONS:
        raise CliValidationError(
            f"Unsupported operation: {operation}",
            field="operation",
        )

    task_ids = getattr(args, "task_id", None) or []
    batch_ids = getattr(args, "batch_id", None) or []
    if not task_ids and not batch_ids:
        raise CliValidationError(
            "At least one --task-id or --batch-id is required",
            field="--task-id",
        )

    payload = {"operation": operation}
    if task_ids:
        payload["tasklist"] = list(task_ids)
    if batch_ids:
        payload["batch_ids"] = list(batch_ids)

    dup_bourreau_id = getattr(args, "dup_bourreau_id", None)
    if dup_bourreau_id is not None:
        payload["dup_bourreau_id"] = dup_bourreau_id
    archive_dp_id = getattr(args, "archive_dp_id", None)
    if archive_dp_id is not None:
        payload["archive_dp_id"] = archive_dp_id
    if getattr(args, "nozip", False):
        payload["nozip"] = True

    data, _ = CbrainClient.from_credentials().send("POST", "/tasks/operation", payload=payload)
    return data


def create_task(args):
    """
    Create a new task in CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments including tool_config_id, results_dp_id, file_ids, invoke

    Returns
    -------
    tuple
        (response_data, response_status)
    """
    tool_config_id = getattr(args, "tool_config_id", None)
    results_dp_id = getattr(args, "results_dp_id", None)
    file_ids = getattr(args, "file_ids", None)

    for val, label, field in [
        (tool_config_id, "Tool config ID is required", "tool_config_id"),
        (results_dp_id, "Results data provider ID is required", "results_dp_id"),
        (file_ids, "At least one file ID is required", "file_ids"),
    ]:
        if not val:
            raise CliValidationError(label, field=field)

    invoke = {}
    invoke_json = getattr(args, "invoke", None)
    if invoke_json:
        try:
            invoke = json.loads(invoke_json)
        except json.JSONDecodeError as e:
            raise CliValidationError(f"Invalid JSON for --invoke: {e}", field="invoke") from e

    payload = {
        "cbrain_task": {
            "tool_config_id": tool_config_id,
            "results_data_provider_id": results_dp_id,
            "params": {
                "interface_userfile_ids": file_ids,
                "invoke": invoke,
            },
        }
    }
    return CbrainClient.from_credentials().send("POST", "/tasks", payload=payload)
