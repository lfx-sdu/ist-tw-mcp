# HTN workspace example

Use the HTN tenant token and the settings in [mcp.example.json](mcp.example.json).
Follow the [client setup](../../README.md#connect-your-mcp-client) to install the
shared adapter and fill in the absolute paths. The MCP server entry is
`taiwan-transfer-pilot-htn`.

## Compare the two saved planning modes

Ask your agent:

> Open my HTN pilot demo workspace. Find the successful Full and
> Allocation-only plans dated May 3, 2026. Show me the recommended line and
> piece counts for each mode and save both recommendation workbooks.

The agent can follow these steps:

1. Call `list_workspaces` and select **HTN pilot demo (synthetic)**. Its
   assigned profile is `htn_tw`. Use the returned workspace ID.
2. Call `list_workspace_planning_jobs` and select the successful `full` and
   `allocation_only` jobs for `2026-05-03`.
3. Call `get_planning_job` and `list_planning_recommendations` for each job.
   Compare the planned pieces and the recommendation counts. Use the run
   audit to report which inputs and settings the job used.
4. Call `download_planning_artifact` with `recommendations.xlsx` for each job.
   The two workbooks have distinct job IDs in their filenames.

The saved plans use synthetic inputs. This walkthrough retrieves those plans
from history.
