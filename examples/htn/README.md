# HTN workspace example

Use the HTN tenant token with the hosted MCP server. Follow the
[client setup](../../README.md#connect-your-mcp-client) or use the fields in
[mcp.example.json](mcp.example.json). The server entry is `taiwan-transfer-pilot-htn`.

## Review the historical results and rerun the first plan

Ask your agent:

> Select my **HTN historical pilot** workspace. Save my Phase 3 PDF and workbook,
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
   Open each returned browser link to download its workbook.

The saved plans use synthetic inputs. This walkthrough retrieves those plans
from history.
