# APM workspace example

Use the APM token from your pilot access email with the hosted MCP server.
Follow the [client setup](../../README.md#connect-your-mcp-client) or use
[mcp.example.json](mcp.example.json). The server entry is `taiwan-transfer-pilot-apm`.

## Review the historical results and rerun the first plan

Ask your agent:

> Select my **APM historical pilot** workspace. Save my Phase 3 PDF and workbook,
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

## Recover the weekly sales audit

Ask your agent:

> Open my APM pilot demo workspace. Find the latest successful weekly sales
> audit for May 4 through May 10, 2026. Save the Excel workbook and tell me
> how many pieces were recommended and how many net sales pieces were recorded.

The agent can follow these steps:

1. Call `list_workspaces` and select **APM pilot demo (synthetic)**. Its
   assigned profile is `apm_tw`. Use the returned workspace ID.
2. Call `list_workspace_planning_jobs` and look for a successful job with
   `kind: weekly_audit`. Use `get_planning_job` to confirm the audited week
   and identify the saved plan and sales version used.
3. Call `download_planning_artifact` with the **audit job's ID** and the
   filename `weekly_audit.xlsx`. Return the browser download link.
4. Use the workbook's **Receiver sales** sheet to compare recommended pieces
   with gross sales, returns, and net sales by receiving store and SKU.
   **Summary** records the dates and the two input versions.

The worksheet compares synthetic recommendations with synthetic sales for the
week. Its sales counts include all recorded sales for those receiver and SKU
pairs within the week.
