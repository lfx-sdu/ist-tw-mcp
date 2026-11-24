# ROS workspace example

Use the ROS tenant token and the settings in [mcp.example.json](mcp.example.json).
Follow the [client setup](../../README.md#connect-your-mcp-client) to install the
shared adapter and fill in the absolute paths. The MCP server entry is
`taiwan-transfer-pilot-ros`.

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
