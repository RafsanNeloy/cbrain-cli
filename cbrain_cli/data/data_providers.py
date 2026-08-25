from cbrain_cli.cli_utils import (
    CbrainClient,
    CliApiError,
    CliValidationError,
    pagination,
)


def show_data_provider(args):
    """
    Get data provider details for the specified data provider ID.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument

    Returns
    -------
    dict
        Data provider details
    """
    # Get the data provider ID from the --id argument.
    data_provider_id = getattr(args, "id", None)
    if not data_provider_id:
        return list_data_providers(args)
    data = CbrainClient.from_credentials().get(f"/data_providers/{data_provider_id}")
    if data.get("error"):
        raise CliApiError(data.get("error"))
    return data


def list_data_providers(args):
    """
    Get list of all data providers from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag

    Returns
    -------
    list
        List of data provider dictionaries
    """
    params = pagination(args, {})
    return CbrainClient.from_credentials().get("/data_providers", params=params)


def is_alive(args):
    """
    Check if a data provider is alive.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument
    """
    data_provider_id = getattr(args, "id", None)
    if not data_provider_id:
        raise CliValidationError("Data provider ID is required", field="id")
    return CbrainClient.from_credentials().get(f"/data_providers/{data_provider_id}/is_alive")


def delete_unregistered_files(args):
    """
    Delete unregistered files from a data provider.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument
    """
    data_provider_id = getattr(args, "id", None)
    if not data_provider_id:
        raise CliValidationError("Data provider ID is required", field="id")
    data, _ = CbrainClient.from_credentials().send(
        "POST", f"/data_providers/{data_provider_id}/delete"
    )
    return data


def browse_data_provider(args):
    """
    Browse files on a data provider.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments including id

    Returns
    -------
    list or dict
        Browse listing from the data provider
    """
    data_provider_id = getattr(args, "id", None)
    if not data_provider_id:
        raise CliValidationError("Data provider ID is required", field="id")
    return CbrainClient.from_credentials().get(f"/data_providers/{data_provider_id}/browse")


def register_files(args):
    """
    Register files from a data provider into CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments including id, basenames, file_type, group_id

    Returns
    -------
    tuple
        (response_data, response_status)
    """
    data_provider_id = getattr(args, "id", None)
    basenames = getattr(args, "basenames", None)
    if not data_provider_id:
        raise CliValidationError("Data provider ID is required", field="id")
    if not basenames:
        raise CliValidationError("At least one basename is required", field="--basenames")

    # BrainPortal expects "Type-basename" strings, e.g. "TextFile-foo.txt"
    file_type = getattr(args, "file_type", None) or "SingleFile"
    filetypes = [f"{file_type}-{b}" for b in basenames]

    payload = {"basenames": basenames, "filetypes": filetypes}
    group_id = getattr(args, "group_id", None)
    if group_id is not None:
        payload["other_group_id"] = group_id
    return CbrainClient.from_credentials().send(
        "POST", f"/data_providers/{data_provider_id}/register", payload=payload
    )


def unregister_files(args):
    """
    Unregister files from a data provider.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments including id and basenames

    Returns
    -------
    tuple
        (response_data, response_status)
    """
    data_provider_id = getattr(args, "id", None)
    basenames = getattr(args, "basenames", None)
    if not data_provider_id:
        raise CliValidationError("Data provider ID is required", field="id")
    if not basenames:
        raise CliValidationError("At least one basename is required", field="--basenames")
    return CbrainClient.from_credentials().send(
        "POST",
        f"/data_providers/{data_provider_id}/unregister",
        payload={"basenames": basenames},
    )
