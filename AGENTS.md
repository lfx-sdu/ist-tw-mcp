# Taiwan Transfer Pilot

Use the participant’s configured MCP server at
`https://ist-tw.sdu-alchemist.org/mcp` over Streamable HTTP. The participant
enters the token from their brand email in the client’s secure Authorization
header. Keep the token out of chat and tool arguments.

- **Find the workspace.** Call `list_workspaces` and use the workspace the participant chooses.
- **Get reports.** Call `list_published_files` and `download_published_file`. Give the participant the browser links.
- **Run a historical plan.** Read the workspace’s `head_version_id` with `get_data_version`. Use the returned `source_contract.as_of` with `create_planning_job`, then poll `get_planning_job`.
- **Find a past result.** Use `list_workspace_planning_jobs` if the job ID is missing. Use `download_planning_artifact` to get the Excel file.
- **Make a weekly audit.** Use `create_weekly_audit` with the prior week’s successful plan, the closed week’s sales version, and the Monday date. Download `weekly_audit.xlsx` from the completed job.
- **Upload data.** For an approved file, use `create_upload` in an upload-enabled workspace and give the participant the browser link. Check `get_upload_status` before mapping or importing it.
