# ROS workspace example

Use the ROS token from your pilot access email with the hosted MCP server.
Follow the [client setup](../../README.md#connect-your-mcp-client) or use
[mcp.example.json](mcp.example.json). The server entry is `taiwan-transfer-pilot-ros`.

## Review the historical results and rerun the first plan

Ask your agent:

> Select my **ROS historical pilot** workspace. Save my Phase 3 PDF and workbook,
> rerun the Full plan for the supplied date, and save the recommendations workbook.

1. Use `list_workspaces` to discover this workspace and its `head_version_id`.
2. Call `list_published_files`. Use `download_published_file` with the
   workspace ID and each file ID you want to save. The catalogue includes a
   PDF, an Excel workbook, and the historical planning inputs archive.
3. Call `get_data_version`, then submit `create_planning_job` with its version
   ID, its `source_contract.as_of` date, `run_type: full`, and a fresh idempotency key.
4. Poll `get_planning_job` and save `recommendations.xlsx` with
   `download_planning_artifact`. The version lists the expected result for the
   supplied first planning date.

The saved Phase 3 workbook covers the multiweek historical study. The new
recommendations workbook covers the first planning date and its inputs.

## Review an Allocation-only scenario

Ask your agent:

> Open my ROS pilot demo workspace and find the successful Allocation-only
> plan dated May 3, 2026. Show the recommendation rows with source,
> destination, SKU, and quantity. Then show me how I could rerun that scenario
> with a total cap of three pieces.

The agent can follow these steps:

1. Call `list_workspaces` and select **ROS pilot demo (synthetic)**. Its
   assigned profile is `ros_tw`. Use the returned workspace ID.
2. Call `list_workspace_planning_jobs` and select the successful
   `allocation_only` job for `2026-05-03`. Read its configuration with
   `get_planning_job` and its rows with `list_planning_recommendations`.
3. Call `get_run_options` and show the proposed
   `allocation_rules: {"max_pieces": 3}`. Retain the selected demo job's
   workspace, data version, and planning date.
4. If the participant requests the rerun, submit `create_planning_job` in
   Allocation-only mode with those inputs and a new idempotency key. Poll the
   new job, check that its recommended pieces respect the cap, and save
   `recommendations.xlsx` using the new job ID.

Start with the saved scenario so the participant can review the output before
queuing a new job.
